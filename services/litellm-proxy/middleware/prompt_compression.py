"""
Prompt Compression Middleware using LLMLingua
Integrates with LiteLLM's custom logger system to compress prompts before LLM calls
"""

import os
import time
from typing import Optional, Literal, Dict, Any, List
from litellm.integrations.custom_logger import CustomLogger

# Try to import LLMLingua, but make it optional for development
try:
    from llmlingua import PromptCompressor
    LLMLINGUA_AVAILABLE = True
except ImportError:
    LLMLINGUA_AVAILABLE = False
    print("Warning: LLMLingua not available. Prompt compression will be disabled.")


class PromptCompressionMiddleware(CustomLogger):
    """
    Custom middleware for compressing prompts using LLMLingua before sending to LLMs.
    
    Implements LiteLLM's CustomLogger interface to hook into the request lifecycle.
    Compression is applied in the async_pre_call_hook before the LLM API call.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize compressor if LLMLingua is available
        self.compressor = None
        if LLMLINGUA_AVAILABLE:
            try:
                self.compressor = PromptCompressor(
                    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
                    device_map="cpu"  # Use CPU for now, can be configured for GPU
                )
                print("PromptCompressionMiddleware initialized with LLMLingua")
            except Exception as e:
                print(f"Failed to initialize LLMLingua compressor: {e}")
        
        # Compression configuration per use case (env-configurable)
        self.compression_config = {
            "default": {
                "enabled": True,
                "target_ratio": float(os.getenv("COMPRESSION_DEFAULT_RATIO", "0.5")),
                "min_tokens": int(os.getenv("COMPRESSION_DEFAULT_MIN_TOKENS", "500")),
                "rate": float(os.getenv("COMPRESSION_DEFAULT_RATIO", "0.5"))
            },
            "rag_queries": {
                "enabled": True,
                "target_ratio": float(os.getenv("COMPRESSION_RAG_RATIO", "0.33")),
                "min_tokens": int(os.getenv("COMPRESSION_RAG_MIN_TOKENS", "1000")),
                "rate": float(os.getenv("COMPRESSION_RAG_RATIO", "0.33"))
            },
            "chat": {
                "enabled": True,
                "target_ratio": float(os.getenv("COMPRESSION_CHAT_RATIO", "0.6")),
                "min_tokens": int(os.getenv("COMPRESSION_CHAT_MIN_TOKENS", "300")),
                "rate": float(os.getenv("COMPRESSION_CHAT_RATIO", "0.6"))
            }
        }
    
    async def async_pre_call_hook(
        self,
        user_api_key_dict,
        cache,
        data: dict,
        call_type: Literal["completion", "embeddings", "image_generation"]
    ) -> Optional[dict]:
        """
        Hook that runs before LLM API call.
        Compresses prompts if configured for the tenant/user and meets size threshold.
        
        Args:
            user_api_key_dict: User/tenant authentication info
            cache: LiteLLM cache instance
            data: Request data (contains messages, model, etc.)
            call_type: Type of API call
        
        Returns:
            Modified data dict with compressed prompt or original data
        """
        
        # Only compress completion calls (not embeddings or image generation)
        if call_type != "completion":
            return data
        
        # Skip compression if LLMLingua not available
        if not self.compressor:
            return data
        
        # Check if compression is enabled for this user/tenant
        tenant_id = getattr(user_api_key_dict, 'team_id', 'default')
        compression_enabled = self._check_compression_enabled(tenant_id)
        
        if not compression_enabled:
            return data
        
        # Extract messages from request
        messages = data.get("messages", [])
        if not messages:
            return data
        
        # Determine compression profile from metadata
        metadata = data.get("metadata", {})
        profile = self._select_compression_profile(metadata)
        
        try:
            # Compress the prompt
            compression_start = time.time()
            compressed_data = await self._compress_messages(messages, data, profile)
            compression_time = time.time() - compression_start
            
            # Log compression metrics
            await self._log_compression_metrics(
                tenant_id=tenant_id,
                original_tokens=compressed_data["original_tokens"],
                compressed_tokens=compressed_data["compressed_tokens"],
                savings_percent=compressed_data["savings_percent"],
                compression_time=compression_time,
                profile=profile
            )
            
            return compressed_data["data"]
        
        except Exception as e:
            # Log error but don't fail the request - return original data
            print(f"Compression failed for tenant {tenant_id}: {e}")
            return data
    
    async def _compress_messages(self, messages: List[dict], data: dict, profile: str = "default") -> Dict[str, Any]:
        """
        Compress message content while preserving structure.
        
        Args:
            messages: List of message dicts with role and content
            data: Full request data
            profile: Compression profile to use ("default", "rag_queries", or "chat")
        
        Returns:
            Dict containing compressed data and metrics
        """
        
        # Separate system, user, and assistant messages
        system_msgs = [m for m in messages if m.get("role") == "system"]
        user_msgs = [m for m in messages if m.get("role") == "user"]
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
        
        # Extract content for compression
        # Context: previous conversation turns (exclude the latest question)
        context = []
        if len(user_msgs) > 1:
            context = [m["content"] for m in user_msgs[:-1]]
        if assistant_msgs:
            context.extend([m["content"] for m in assistant_msgs])
        
        # Question: latest user message
        question = user_msgs[-1]["content"] if user_msgs else ""
        
        # Instruction: system message
        instruction = system_msgs[0]["content"] if system_msgs else ""
        
        # Get token count estimate
        original_tokens = self._estimate_tokens(messages)
        
        # Get compression config for selected profile
        config = self.compression_config.get(profile, self.compression_config["default"])
        
        # Only compress if above threshold
        if original_tokens < config["min_tokens"]:
            return {
                "data": data,
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "savings_percent": 0
            }
        
        # Compress using LLMLingua
        try:
            compressed_result = self.compressor.compress_prompt(
                context,
                instruction=instruction,
                question=question,
                rate=config["rate"],
                condition_compare=True,
                condition_in_question="after",
                rank_method="longllmlingua",
                use_sentence_level_filter=True,
                context_budget="+100",
                dynamic_context_compression_ratio=0.4,
                reorder_context="sort"
            )
            
            # Reconstruct messages with compressed content
            compressed_messages = []
            
            # Keep system message if present
            if system_msgs:
                compressed_messages.append(system_msgs[0])
            
            # Add compressed user message
            compressed_messages.append({
                "role": "user",
                "content": compressed_result["compressed_prompt"]
            })
            
            # Update data with compressed messages
            compressed_data = data.copy()
            compressed_data["messages"] = compressed_messages
            
            return {
                "data": compressed_data,
                "original_tokens": compressed_result["origin_tokens"],
                "compressed_tokens": compressed_result["compressed_tokens"],
                "savings_percent": (1 - compressed_result["ratio"]) * 100
            }
        
        except Exception as e:
            print(f"LLMLingua compression failed: {e}")
            # Return original data if compression fails
            return {
                "data": data,
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "savings_percent": 0
            }
    
    def _estimate_tokens(self, messages: List[dict]) -> int:
        """
        Estimate token count for messages using rough heuristic.
        More accurate counting can be done with tiktoken if needed.
        
        Args:
            messages: List of message dicts
        
        Returns:
            Estimated token count
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            # Rough estimate: 1 token ≈ 4 characters (average for English)
            total += len(content) // 4
        return total
    
    def _select_compression_profile(self, metadata: Dict[str, Any]) -> str:
        """
        Select compression profile based on request metadata.
        
        Args:
            metadata: Request metadata dictionary
        
        Returns:
            Profile name ("default", "rag_queries", or "chat")
        """
        # Check for RAG query flag in metadata
        # LiteLLM passes metadata from request headers prefixed with x-
        is_rag = metadata.get("x-rag") == "true" or metadata.get("rag") == "true"
        if is_rag:
            return "rag_queries"
        
        # Check for chat flag
        is_chat = metadata.get("x-chat") == "true" or metadata.get("chat") == "true"
        if is_chat:
            return "chat"
        
        # Default profile
        return "default"
    
    def _check_compression_enabled(self, tenant_id: str) -> bool:
        """
        Check if compression is enabled for tenant.
        In production, this would check feature flags via Flagsmith or Platform API.
        
        Args:
            tenant_id: Tenant identifier
        
        Returns:
            True if compression should be applied
        """
        # For R1, enable for all tenants
        # In R2+, integrate with Flagsmith/Platform API
        return True
    
    async def _log_compression_metrics(
        self,
        tenant_id: str,
        original_tokens: int,
        compressed_tokens: int,
        savings_percent: float,
        compression_time: float,
        profile: str = "default"
    ):
        """
        Log compression metrics to Prometheus and console.
        
        Args:
            tenant_id: Tenant identifier
            original_tokens: Original prompt token count
            compressed_tokens: Compressed prompt token count
            savings_percent: Percentage of tokens saved
            compression_time: Time taken to compress in seconds
            profile: Compression profile used
        """
        try:
            # Import prometheus metrics
            from prometheus_client import Counter, Histogram
            
            # Define metrics (these will be created once)
            compression_requests = Counter(
                'litellm_compression_requests_total',
                'Total number of compression requests',
                ['tenant_id', 'profile']
            )
            compression_savings = Histogram(
                'litellm_compression_savings_percent',
                'Compression savings percentage',
                ['tenant_id', 'profile']
            )
            compression_latency = Histogram(
                'litellm_compression_latency_seconds',
                'Compression operation latency',
                ['tenant_id', 'profile']
            )
            original_tokens_metric = Histogram(
                'litellm_compression_original_tokens',
                'Original token count before compression',
                ['tenant_id', 'profile']
            )
            compressed_tokens_metric = Histogram(
                'litellm_compression_compressed_tokens',
                'Token count after compression',
                ['tenant_id', 'profile']
            )
            
            # Record metrics
            compression_requests.labels(tenant_id=tenant_id, profile=profile).inc()
            compression_savings.labels(tenant_id=tenant_id, profile=profile).observe(savings_percent)
            compression_latency.labels(tenant_id=tenant_id, profile=profile).observe(compression_time)
            original_tokens_metric.labels(tenant_id=tenant_id, profile=profile).observe(original_tokens)
            compressed_tokens_metric.labels(tenant_id=tenant_id, profile=profile).observe(compressed_tokens)
            
        except Exception as e:
            # Don't fail request if metrics logging fails
            print(f"Failed to log compression metrics: {e}")
        
        # Also log to console for debugging
        print(
            f"Compression for tenant {tenant_id} [profile={profile}]: "
            f"{original_tokens} → {compressed_tokens} tokens "
            f"({savings_percent:.1f}% saved, {compression_time*1000:.1f}ms)"
        )


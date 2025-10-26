"""
LiteLLM Proxy Middleware
Custom middleware for prompt compression and observability
"""

from .prompt_compression import PromptCompressionMiddleware

__all__ = ["PromptCompressionMiddleware"]

# Initialize the middleware instance
prompt_compression_middleware = PromptCompressionMiddleware()


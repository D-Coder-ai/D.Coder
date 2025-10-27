#!/usr/bin/env python3
"""
Quota Sync Sidecar Service
Subscribes to NATS quota.updated events from LiteLLM and mirrors quota data to Redis
for Kong Gateway quota-mirror plugin consumption.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any

import redis.asyncio as redis
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig
from nats.js import JetStreamContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class QuotaSyncService:
    """Service to sync quota updates from NATS to Redis"""

    def __init__(self):
        # NATS configuration
        self.nats_url = os.getenv('NATS_URL', 'nats://nats:4222')
        self.nats_stream = os.getenv('NATS_STREAM', 'QUOTAS')
        self.nats_subject = os.getenv('NATS_SUBJECT', 'quota.updated')
        self.nats_consumer = os.getenv('NATS_CONSUMER', 'quota-sync-kong')

        # Redis configuration
        self.redis_host = os.getenv('REDIS_HOST', 'redis')
        self.redis_port = int(os.getenv('REDIS_PORT', '6379'))
        self.redis_db = int(os.getenv('REDIS_DB', '0'))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        self.redis_key_prefix = os.getenv('REDIS_KEY_PREFIX', 'quota:tenant:')

        # Service state
        self.nc = None
        self.js = None
        self.redis_client = None
        self.running = False

    async def connect_nats(self) -> None:
        """Connect to NATS JetStream"""
        try:
            self.nc = NATS()
            await self.nc.connect(servers=[self.nats_url])
            self.js = self.nc.jetstream()
            logger.info(f"Connected to NATS at {self.nats_url}")

            # Ensure stream exists
            try:
                await self.js.stream_info(self.nats_stream)
                logger.info(f"NATS stream '{self.nats_stream}' already exists")
            except Exception:
                # Create stream if it doesn't exist
                logger.info(f"Creating NATS stream '{self.nats_stream}'")
                await self.js.add_stream(
                    StreamConfig(
                        name=self.nats_stream,
                        subjects=[self.nats_subject],
                        retention='limits',
                        max_age=86400  # 24 hours retention
                    )
                )
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise

    async def connect_redis(self) -> None:
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}",
                password=self.redis_password,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def process_quota_event(self, msg) -> None:
        """Process a quota.updated event from NATS"""
        try:
            # Parse event envelope
            event_data = json.loads(msg.data.decode())

            event_id = event_data.get('eventId')
            tenant_id = event_data.get('tenantId')
            payload = event_data.get('payload', {})

            logger.info(f"Processing quota event {event_id} for tenant {tenant_id}")

            if not tenant_id:
                logger.warning(f"Event {event_id} missing tenantId, skipping")
                await msg.ack()
                return

            # Extract quota data from payload
            quota_limit = payload.get('limit', 0)
            quota_used = payload.get('used', 0)
            quota_remaining = payload.get('remaining', 0)
            quota_period = payload.get('period', 'monthly')
            reset_at = payload.get('resetAt')

            # Store in Redis hash
            redis_key = f"{self.redis_key_prefix}{tenant_id}"
            quota_data = {
                'limit': str(quota_limit),
                'used': str(quota_used),
                'remaining': str(quota_remaining),
                'period': quota_period,
                'reset_at': reset_at or '',
                'last_updated': event_data.get('occurredAt', ''),
                'event_id': event_id
            }

            await self.redis_client.hset(redis_key, mapping=quota_data)

            # Set TTL based on period (ensure data doesn't go stale)
            ttl_seconds = {
                'hourly': 3600,
                'daily': 86400,
                'monthly': 2592000,  # 30 days
            }.get(quota_period, 86400)
            await self.redis_client.expire(redis_key, ttl_seconds)

            logger.info(
                f"Updated quota for tenant {tenant_id}: "
                f"used={quota_used}/{quota_limit} ({quota_period})"
            )

            # Acknowledge message
            await msg.ack()

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse event JSON: {e}")
            await msg.nak()
        except Exception as e:
            logger.error(f"Error processing quota event: {e}", exc_info=True)
            await msg.nak()

    async def subscribe_to_quota_events(self) -> None:
        """Subscribe to quota.updated events"""
        try:
            # Create or get durable consumer
            psub = await self.js.pull_subscribe(
                subject=self.nats_subject,
                durable=self.nats_consumer,
                stream=self.nats_stream
            )

            logger.info(f"Subscribed to {self.nats_subject} as {self.nats_consumer}")

            # Process messages
            while self.running:
                try:
                    # Fetch messages (batch of 10, wait up to 5 seconds)
                    messages = await psub.fetch(batch=10, timeout=5.0)
                    for msg in messages:
                        await self.process_quota_event(msg)
                except TimeoutError:
                    # No messages available, continue
                    pass
                except Exception as e:
                    logger.error(f"Error fetching messages: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Failed to subscribe to quota events: {e}")
            raise

    async def start(self) -> None:
        """Start the quota sync service"""
        logger.info("Starting Quota Sync Service")
        self.running = True

        try:
            # Connect to NATS and Redis
            await self.connect_nats()
            await self.connect_redis()

            # Subscribe to quota events
            await self.subscribe_to_quota_events()

        except Exception as e:
            logger.error(f"Service error: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop the quota sync service"""
        logger.info("Stopping Quota Sync Service")
        self.running = False

        if self.nc:
            await self.nc.close()
            logger.info("Disconnected from NATS")

        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")


async def main():
    """Main entry point"""
    service = QuotaSyncService()

    # Handle graceful shutdown
    import signal

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(service.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        await service.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

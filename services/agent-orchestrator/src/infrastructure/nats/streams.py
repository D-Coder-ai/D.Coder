"""
JetStream stream configuration
"""

from nats.js.api import RetentionPolicy, StreamConfig

WORKFLOWS_STREAM = StreamConfig(
    name="WORKFLOWS",
    subjects=["workflow.>"],
    retention=RetentionPolicy.LIMITS,
    max_age=86400 * 7,  # 7 days
)

INTEGRATIONS_STREAM = StreamConfig(
    name="INTEGRATIONS",
    subjects=["integration.>"],
    retention=RetentionPolicy.LIMITS,
    max_age=86400 * 7,
)

QUOTAS_STREAM = StreamConfig(
    name="QUOTAS",
    subjects=["quota.>"],
    retention=RetentionPolicy.LIMITS,
    max_age=86400 * 30,  # 30 days
)


async def setup_streams(js) -> None:
    """
    Setup JetStream streams (idempotent)
    """
    streams = [WORKFLOWS_STREAM, INTEGRATIONS_STREAM, QUOTAS_STREAM]

    for stream_config in streams:
        try:
            await js.add_stream(stream_config)
        except Exception:
            try:
                await js.update_stream(stream_config)
            except Exception:
                pass

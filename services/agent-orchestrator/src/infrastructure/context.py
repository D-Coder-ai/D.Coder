"""
Request context management using context variables
"""

from contextvars import ContextVar

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
tenant_id_ctx: ContextVar[str | None] = ContextVar("tenant_id", default=None)
platform_id_ctx: ContextVar[str | None] = ContextVar("platform_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)


def get_request_id() -> str | None:
    """Get current request ID from context"""
    return request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    """Set request ID in context"""
    request_id_ctx.set(request_id)


def get_tenant_id() -> str | None:
    """Get current tenant ID from context"""
    return tenant_id_ctx.get()


def set_tenant_id(tenant_id: str) -> None:
    """Set tenant ID in context"""
    tenant_id_ctx.set(tenant_id)


def get_platform_id() -> str | None:
    """Get current platform ID from context"""
    return platform_id_ctx.get()


def set_platform_id(platform_id: str) -> None:
    """Set platform ID in context"""
    platform_id_ctx.set(platform_id)


def get_user_id() -> str | None:
    """Get current user ID from context"""
    return user_id_ctx.get()


def set_user_id(user_id: str) -> None:
    """Set user ID in context"""
    user_id_ctx.set(user_id)


def get_trace_id() -> str | None:
    """Get current trace ID from context"""
    return trace_id_ctx.get()


def set_trace_id(trace_id: str) -> None:
    """Set trace ID in context"""
    trace_id_ctx.set(trace_id)

# dcoder-common

Shared Python utilities for D.Coder platform services.

## Installation

For development (editable install):
```bash
pip install -e packages/python/dcoder-common
```

In Docker containers (services):
```dockerfile
COPY packages/python/dcoder-common /packages/dcoder-common
RUN pip install -e /packages/dcoder-common
```

## Contents

- `dcoder_common/middleware/` - Shared FastAPI middleware
- `dcoder_common/models/` - Shared Pydantic models
- `dcoder_common/auth/` - Authentication utilities
- `dcoder_common/observability/` - Logging, metrics, tracing

## Usage

```python
from dcoder_common.middleware import LoggingMiddleware, TenantMiddleware
from dcoder_common.models import TenantContext

app = FastAPI()
app.add_middleware(LoggingMiddleware)
app.add_middleware(TenantMiddleware)
```


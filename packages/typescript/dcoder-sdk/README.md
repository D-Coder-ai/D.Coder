# @dcoder/sdk

TypeScript SDK for D.Coder platform client applications.

## Installation

```bash
pnpm add @dcoder/sdk
```

## Usage

```typescript
import { DCoderClient } from '@dcoder/sdk';

const client = new DCoderClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Example: Get tenants
const tenants = await client.tenants.list();
```

## API

- `client.tenants` - Tenant management
- `client.providers` - Provider configuration
- `client.quotas` - Quota and usage tracking
- `client.llm` - LLM inference endpoints


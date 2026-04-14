# Catalyst Center API Path Reference

## Scope
This project uses a single OpenAPI source:
- `openapi_specs/intent_api_3_1_3.json`

All MCP tools are generated from this spec and exposed with the `intent_` prefix.

## Base Paths
- Intent operations: `/dna/intent/api/v1/*`
- Token endpoint: `/dna/system/api/v1/auth/token`

The OpenAPI `servers` entry in `intent_api_3_1_3.json` is `/`, so each path in `paths` is already absolute (for example, `/dna/intent/api/v1/network-device`).

## Runtime URL Construction
1. `src/core/api_loader.py` loads operation paths directly from the spec.
2. `src/middleware/auth.py` forwards those paths to the API client.
3. `src/services/catalyst_api.py` joins the cluster base URL with the path.

Example:
- Base URL: `https://catalyst-center.example.com`
- Path: `/dna/intent/api/v1/endpoint-analytics/endpoints`
- Final URL: `https://catalyst-center.example.com/dna/intent/api/v1/endpoint-analytics/endpoints`

## Authentication Flow
1. Request token via `POST /dna/system/api/v1/auth/token`.
2. Use returned token in `X-Auth-Token` for subsequent calls.
3. On `401`, client re-authenticates and retries.

Optional AES auth mode is supported by configuration in `src/config/settings.py`.

## Valid Tool Naming
Tool name format:
- `intent_<operationId>`

Examples from current generated tool descriptions:
- `intent_queryTheEndpoints`
- `intent_getTaskDetails`
- `intent_registerAnEndpoint`
- `intent_getEndpointDetails`
- `intent_createAProfilingRule`

## Common Troubleshooting
### 404 errors
- Verify the request path begins with `/dna/intent/api/v1/`.
- Verify the operation exists in `openapi_specs/intent_api_3_1_3.json`.

### 401 errors
- Verify token endpoint connectivity: `POST /dna/system/api/v1/auth/token`.
- Check credentials and auth mode configuration (`basic` vs `aes256`).

### Tool mismatch errors
- Ensure role/allow-list entries use exact tool names from the generated `intent_*` set.

## References
- `openapi_specs/intent_api_3_1_3.json`
- `src/services/catalyst_api.py`
- `src/middleware/auth.py`
- `src/config/migrations/008_seed_tool_descriptions.sql`

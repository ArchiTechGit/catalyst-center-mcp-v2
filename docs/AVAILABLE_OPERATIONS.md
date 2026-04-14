# Available Operations - Catalyst Center Intent API

## Source of Truth
Operations and tool names come from:
- `openapi_specs/intent_api_3_1_3.json`
- `src/config/migrations/008_seed_tool_descriptions.sql`

This project uses a single API namespace: `intent`.

## Tool Naming Convention
- Format: `intent_<operationId>`
- Example tool names from the current generated set:
1. `intent_queryTheEndpoints`
2. `intent_fetchTheCountOfEndpoints`
3. `intent_registerAnEndpoint`
4. `intent_getEndpointDetails`
5. `intent_deleteAnEndpoint`
6. `intent_createAProfilingRule`
7. `intent_getListOfProfilingRules`
8. `intent_getTaskDetails`
9. `intent_getANCPolicies`
10. `intent_getThreatTypes`

## Representative Endpoint Mapping
1. `intent_queryTheEndpoints` -> `GET /dna/intent/api/v1/endpoint-analytics/endpoints`
2. `intent_fetchTheCountOfEndpoints` -> `GET /dna/intent/api/v1/endpoint-analytics/endpoints/count`
3. `intent_registerAnEndpoint` -> `POST /dna/intent/api/v1/endpoint-analytics/endpoints`
4. `intent_getEndpointDetails` -> `GET /dna/intent/api/v1/endpoint-analytics/endpoints/{epId}`
5. `intent_getTaskDetails` -> `GET /dna/intent/api/v1/endpoint-analytics/tasks/{taskId}`

## Access Mode Behavior
1. Read-only mode: only `GET` operations are allowed.
2. Edit mode: `POST`, `PUT`, and `DELETE` operations are also allowed.

## How to Enumerate Current Operations
Use runtime enumeration from the loaded spec:

```bash
docker exec -i catc_mcp_mcp_server python -c "
import sys
sys.path.insert(0, '/app')
from src.core.api_loader import APILoader

loader = APILoader()
spec = loader.load_openapi_spec('intent_api_3_1_3.json')
for op in loader.list_operations(spec):
    print(f'{op["method"]:6s} {op["path"]:70s} intent_{op["operation_id"]}')
"
```

## Notes
1. Older `manage_*`, `analyze_*`, and `infra_*` names are obsolete.
2. If a role contains obsolete names, update them to valid `intent_*` tool names.
3. Prefer checking `008_seed_tool_descriptions.sql` for curated operation descriptions.

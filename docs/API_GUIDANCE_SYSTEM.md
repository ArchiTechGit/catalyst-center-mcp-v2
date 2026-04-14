# API Guidance System

## Overview
The API Guidance System stores prompt guidance and workflow hints used to enrich MCP tool descriptions at runtime.

This repository is now aligned to a single API namespace:
- `intent` from `openapi_specs/intent_api_3_1_3.json`

## Data Model
1. API guidance: top-level guidance by API name (for this repo, `intent`).
2. Category guidance: guidance grouped by category (for example `endpoint_analytics`, `tasks`, `policy`).
3. Workflow: reusable multi-step sequences for common operations.
4. Tool override: operation-level custom guidance keyed by full MCP tool name.

## Tool Naming
All generated tools follow:
- `intent_<operationId>`

Examples from current generated tooling:
1. `intent_queryTheEndpoints`
2. `intent_fetchTheCountOfEndpoints`
3. `intent_registerAnEndpoint`
4. `intent_getEndpointDetails`
5. `intent_deleteAnEndpoint`
6. `intent_createAProfilingRule`
7. `intent_getListOfProfilingRules`
8. `intent_getTaskDetails`

## GuidanceService API
Primary service: `src/services/guidance_service.py`

### Core methods
1. `get_api_guidance(api_name)`
2. `list_api_guidance(active_only=True)`
3. `upsert_api_guidance(api_name, **kwargs)`
4. `delete_api_guidance(api_name)`
5. `get_category_guidance(api_name, category_name)`
6. `list_category_guidance(api_name=None, active_only=True)`
7. `upsert_category_guidance(api_name, category_name, **kwargs)`
8. `delete_category_guidance(category_id)`
9. `create_workflow(name, display_name, **kwargs)`
10. `set_workflow_steps(workflow_id, steps)`
11. `upsert_tool_override(operation_name, **kwargs)`
12. `generate_system_prompt()`

## Usage Example
```python
from src.services.guidance_service import GuidanceService

service = GuidanceService()

api_guidance = await service.upsert_api_guidance(
    api_name="intent",
    display_name="Catalyst Center Intent API",
    description="Guidance for Catalyst Center Intent API operations",
    general_guidance="Start with read operations to validate identifiers and current state",
    common_patterns="List -> Detail -> Action -> Task validation",
    gotchas="Async operations return task IDs; poll task status before assuming completion",
    is_active=True,
    section_order=1,
)

category = await service.upsert_category_guidance(
    api_name="intent",
    category_name="endpoint_analytics",
    display_name="Endpoint Analytics",
    description="Guidance for endpoint analytics operations",
    usage_tips="Use count/list calls first, then target endpoint-level calls",
    prerequisites="Valid Catalyst Center auth and cluster reachability",
    related_categories=["tasks", "profiling_rules"],
    is_active=True,
)

workflow = await service.create_workflow(
    name="endpoint_analytics_quick_start",
    display_name="Endpoint Analytics Quick Start",
    description="Basic endpoint analytics workflow",
    use_case="Validate endpoint visibility and retrieve endpoint details",
    estimated_duration="5-10 minutes",
    use_case_tags=["endpoint", "analytics"],
    is_active=True,
)

await service.set_workflow_steps(
    workflow_id=workflow.id,
    steps=[
        {
            "step_order": 1,
            "step_name": "List endpoints",
            "operation_name": "intent_queryTheEndpoints",
            "description": "Retrieve a bounded endpoint list",
            "parameters": {"limit": 50},
            "expected_result": "Endpoints returned",
            "validation": "Response contains endpoint records",
        },
        {
            "step_order": 2,
            "step_name": "Get endpoint detail",
            "operation_name": "intent_getEndpointDetails",
            "description": "Inspect a specific endpoint",
            "parameters": {"epId": "<endpoint-id>"},
            "expected_result": "Endpoint detail returned",
            "validation": "Response includes the requested endpoint ID",
        },
        {
            "step_order": 3,
            "step_name": "Check task status",
            "operation_name": "intent_getTaskDetails",
            "description": "Validate async operation outcomes",
            "parameters": {"taskId": "<task-id>"},
            "expected_result": "Task state visible",
            "validation": "Task is successful or has actionable error details",
        },
    ],
)
```

## Best Practices
1. Keep guidance examples tied to real `intent_*` operation names.
2. Do not reference legacy `manage_*`, `analyze_*`, or `infra_*` namespaces.
3. Keep workflow steps explicit about required IDs and validation checks.
4. Prefer read-first patterns before executing write operations.

## References
- `openapi_specs/intent_api_3_1_3.json`
- `src/config/migrations/008_seed_tool_descriptions.sql`
- `src/services/guidance_service.py`

# Guidance Service Quick Reference

## Purpose
Quick reference for using `GuidanceService` with the single Catalyst Center Intent API model.

## API Namespace
- API name: `intent`
- Tool naming: `intent_<operationId>`

## Common Operations
```python
from src.services.guidance_service import GuidanceService

service = GuidanceService()

# API guidance
await service.upsert_api_guidance(
    api_name="intent",
    display_name="Catalyst Center Intent API",
    description="Operational guidance for intent tools",
    general_guidance="Prefer list/count/detail validation before write operations",
    is_active=True,
)

# Category guidance
await service.upsert_category_guidance(
    api_name="intent",
    category_name="endpoint_analytics",
    display_name="Endpoint Analytics",
    description="Guidance for endpoint analytics workflows",
    usage_tips="Use intent_queryTheEndpoints and intent_fetchTheCountOfEndpoints first",
    prerequisites="Cluster reachable and authenticated",
    related_categories=["tasks", "profiling_rules"],
    is_active=True,
)

# Workflow
workflow = await service.create_workflow(
    name="endpoint_workflow",
    display_name="Endpoint Workflow",
    description="Inspect endpoint inventory and verify task outcomes",
    use_case="Day-2 endpoint analytics validation",
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
            "parameters": {"limit": 25},
        },
        {
            "step_order": 2,
            "step_name": "Get endpoint details",
            "operation_name": "intent_getEndpointDetails",
            "parameters": {"epId": "<endpoint-id>"},
        },
        {
            "step_order": 3,
            "step_name": "Check task status",
            "operation_name": "intent_getTaskDetails",
            "parameters": {"taskId": "<task-id>"},
        },
    ],
)

# Tool override
await service.upsert_tool_override(
    operation_name="intent_registerAnEndpoint",
    custom_description="Registers an endpoint in Catalyst Center endpoint analytics",
    usage_guidance="Validate endpoint identifiers and target scope before registration",
    warnings="Write operation: confirm change window and rollback approach",
    is_active=True,
)
```

## High-Value Tool Examples
1. `intent_queryTheEndpoints`
2. `intent_fetchTheCountOfEndpoints`
3. `intent_registerAnEndpoint`
4. `intent_getEndpointDetails`
5. `intent_deleteAnEndpoint`
6. `intent_createAProfilingRule`
7. `intent_getTaskDetails`

## Best Practices
1. Keep examples tied to real operations from `intent_api_3_1_3.json`.
2. Avoid legacy namespaces like `manage_*`, `analyze_*`, `infra_*`.
3. Store category guidance by operational domain, not old platform labels.
4. Validate async outcomes with task APIs after write operations.

## References
- `src/services/guidance_service.py`
- `src/config/migrations/008_seed_tool_descriptions.sql`
- `openapi_specs/intent_api_3_1_3.json`

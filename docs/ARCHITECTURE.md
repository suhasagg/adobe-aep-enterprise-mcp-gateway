# Architecture Deep Dive

## Control-plane versus data-plane

The MCP layer describes tools and accepts calls. The control plane establishes whether those calls may execute. Adobe product adapters are the data-plane integration boundary.

## Recommended invocation state machine

```text
RECEIVED
  |
  v
AUTHORIZED
  |
  +--> DENIED
  |
  v
PENDING_APPROVAL
  |
  +--> REJECTED
  |
  v
STARTED
  |
  +--> SUCCEEDED
  +--> FAILED
  +--> UNKNOWN -> RECONCILING -> SUCCEEDED/FAILED
```

The reference code implements the core subset. Add UNKNOWN/reconciliation before enabling sensitive production writes.

## Why a registry instead of arbitrary URLs?

A generic authenticated HTTP proxy would allow prompt injection or a compromised agent to select unexpected Adobe endpoints. The registry constrains capability to explicitly reviewed operations.

## Scaling

Separate synchronous discovery/read calls from durable write execution. Put writes behind a queue and persist state before dispatch. Partition rate limits and worker pools by tenant/product so one noisy integration cannot exhaust the entire gateway.

## Approval integrity

Approval must bind principal, tenant, tool, normalized parameters and policy context. In high-assurance deployments sign the approval envelope and store its digest in an append-only audit stream.

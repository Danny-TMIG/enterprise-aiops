# Enterprise AIOps / Mesh Seed

The binding layer between existing orchestrators, existing prover
tooling, and existing deploy targets — with the verification gate
that makes the whole thing auditable.

## Install

    python -m pip install -e ".[dev]"

## Run

    make serve           # or: python -m app
    make test            # all tests
    make codeql          # security scan
    make sbom sign verify

## Layers

| layer            | package                | what it does                                  |
| ---------------- | ---------------------- | --------------------------------------------- |
| mesh             | `app.mesh`             | AST + CodeQL → engineering graph, router      |
| disintermediation| `app.dis`              | model / protocol / orchestration adapters     |
| autonomy         | `app.autonomy`         | rules → remedies → watchdog                   |
| botnetmastery    | `app.botnetmastery`    | defensive C2 simulation (kill switch)         |
| seed             | `app.seed`             | intent → spec → artifact → proof object       |
| topos            | `app.topos`            | Forward ⊣ Inverse ⊣ Relational unified        |

## The product: Mesh Seed

One intent. Two human gates. One composite proof object.

    intent → spec → artifact → scan → proof → kernel → proof_object
              ↑ gate 1                        ↑ gate 2

Money model: **CPVO** — cost per verified outcome.

## Endpoints

| path                     | purpose                                  |
| ------------------------ | ---------------------------------------- |
| `GET  /health`           | liveness                                 |
| `GET  /mesh/status`      | engineering graph stats                  |
| `POST /mesh/route`       | intent → mesh nodes                      |
| `GET  /dis/status`       | providers / provers / scanners           |
| `POST /dis/complete`     | vendor-agnostic model call               |
| `POST /dis/prove`        | run a prover                             |
| `POST /dis/verify`       | orchestrator backend verdict             |
| `POST /dis/mcp`          | MCP JSON-RPC                             |
| `POST /dis/a2a`          | A2A JSON-RPC                             |
| `GET  /autonomy/status`  | rules + remedies                         |
| `POST /seed/intent`      | start a Mesh Seed run                    |
| `POST /seed/{id}/run`    | run pipeline → proof object              |
| `GET  /topos/status`     | the unified topos                        |

## License

MIT

# ASF Repository — File-by-File Reference

Each entry: 250 words maximum, plain prose, verified against the tree.
LOC and engineering effort are stated as Low / Medium / High.
No tags, no tables beyond the heading line, no ambiguity.

---

## .github/CODEOWNERS

Reviewer assignment file. Declares which GitHub users or teams must approve
changes to which paths. Without this, pull requests merge on any approval.
With it, GitHub blocks merge until a matching code owner signs off. In ASF,
CODEOWNERS should route changes to `components/ax/`, `components/ag/`, and
`components/ac/` to the architect or team owning that layer, and route
changes to `contracts/` and `40_CROSS_STACK_INTEGRATION/05_Canonical_Schemas`
to the contract owner, because boundary objects require independent review
before they change. It should also route `catalog/`, `deploy/`, and
`.github/workflows/` to whoever owns release and CI. This file is small but
load-bearing: it is the enforcement point for the review discipline the FAS
documents assume exists but do not mandate. It has no runtime effect, no
dependency, and no test. Its correctness is measured by whether an
unauthorized change to a protected path is blocked on a pull request.

LOC: Low (10–40 lines).
Engineering effort: Low. Once layer and contract owners are named, this is a
single sitting. The hard part is the decision of who owns what, not the file.

---

## .github/pull_request_template.md

Template shown to every author opening a pull request. Shapes what a reviewer
sees without requiring them to ask. In ASF it should prompt for the component
or contract touched, the layer affected, the FAS section that governs the
change, whether any canonical schema changed, whether any component.json
changed, and the exact command run to verify the change. It should also
prompt for the reason code if `status.py` reports ATTENTION after the change,
and for the Omega Seal if an orchestrator or E2E run was executed. The
template has no runtime effect. Its value is procedural: it forces authors to
state, up front, the same facts a reviewer would otherwise extract by
reading the diff and running commands. A good template reduces review round
trips by making the required context visible before review begins. It should
be short enough to be filled in under two minutes, or authors will skip
fields, which defeats the purpose. It must not ask for information the repo
can generate automatically, such as the current HEAD or the tracked file
count, because that will drift the moment the author pushes again.

LOC: Low (20–60 lines).
Engineering effort: Low. Draft once, iterate after three real pull requests.

---

## .github/workflows/ci.yml

The primary continuous integration workflow. Runs on push and pull request.
Installs the package, runs the status tool, runs the test suite, runs the
full-stack diagnostic, and reports pass or fail. It is the gate that decides
whether a change is allowed to merge under normal branch protection. It
should install Python at the version declared in `pyproject.toml`, install
the package in editable mode, install pytest, run `make test`, and run
`python3 tooling/validation/status.py`. If any step exits nonzero, the
workflow fails and the pull request is blocked. It should cache pip packages
to keep runtime under a few minutes. It should upload the diagnostic log as
an artifact on failure so a reviewer can see exactly which checkmark was
missing. It must not run the orchestrator on every push unless the
orchestrator is fast; if it is slow, that belongs in a separate workflow that
runs on a schedule or on release branches only. The workflow is the first
thing a new contributor encounters when they open a pull request, so its
failure messages should name the failing step clearly, not just print a raw
traceback.

LOC: Low to Medium (40–90 lines).
Engineering effort: Low. The pattern is standard; the work is choosing which
checks are required versus optional.

---

## .github/workflows/security-scan.yml

Security scanning workflow. Runs static analysis, dependency review, secret
scanning, and SBOM generation on a schedule and on pull requests touching
dependencies. In ASF it should run CodeQL, run a secrets scanner against the
diff, run dependency review against the lockfile or requirements, and emit
an SBOM artifact. It should not block merges on informational findings, only
on high-severity findings with a known fix. Its purpose is to catch the class
of mistake a human reviewer will not: a hard-coded credential, a vulnerable
transitive dependency, a code pattern that leaks data. It runs on a schedule
in addition to pull requests because new vulnerabilities are disclosed
against dependencies that have not changed. The workflow should be tuned so
that a clean run takes under five minutes; a scan that takes fifteen minutes
will be skipped by contributors running locally and will slow every merge.
Findings should route to a tracked issue rather than disappearing into the
workflow log.

LOC: Medium (60–120 lines).
Engineering effort: Medium. Requires choosing tools, configuring thresholds,
and wiring SBOM output to wherever artifacts are stored.

---

## .github/workflows/release.yml

Release workflow. Runs on a version tag or on a manual trigger. Builds the
release manifest, runs the full validation suite, and publishes the release
artifact. In ASF it should run `make validate`, run `make test`, capture the
orchestrator Omega Seal, write a release manifest into `deploy/releases/`,
and tag the commit. It must not publish if any gate fails. It should be
triggered by a tag, not by a merge to main, so that releases are intentional
rather than automatic. It should record the exact HEAD commit, the Python
version, and the lockfile hash in the manifest so that a release is
reproducible. It should also record the status verdict at release time, so
that a future reader can tell whether the release was cut from a clean tree
or a dirty one. The workflow is short but it is the last line of defense
before something leaves the repository. Its failure output should be verbose
enough that a release engineer can tell, from the log alone, which gate
failed and why.

LOC: Medium (50–100 lines).
Engineering effort: Medium. Requires deciding release cadence, artifact
storage, and manifest schema.

---

## catalog/inventories/components.json

Machine-readable inventory of every component in the repository. One record
per component, keyed by ID such as `COG-INT-001` or `CMP-CTL-002`. Each
record should carry the component ID, its slug, its layer, its family, its
release scope, and its path. This file is the source of truth that
`status.py` and any downstream tooling consult to answer questions like
"which components are Core v1" or "which components are deferred." It must
stay in sync with the directories under `components/`; a component added to
the tree but not to this file is invisible to tooling, and a component listed
here but absent from the tree will cause a TREE block failure. It should be
regenerated from the tree by a small script rather than edited by hand, so
that drift is impossible. It should not carry behavior, only identity and
classification. Its contents should match the component count reported by
`status.py` — 75 logical components, with the `ax`, `ag`, and `ac` split
reported per layer. Any mismatch between this file and the tree is a bug,
not a choice.

LOC: High for the data file itself (one record per component, 75 records),
Low for the generator that produces it.
Engineering effort: Low once the generator exists. High if maintained by
hand, which it should not be.

---

## catalog/inventories/modules.json

Machine-readable inventory of modules within components. Finer-grained than
`components.json`: one record per module, keyed by component ID plus module
name. In ASF a component may contain multiple modules — for example
`COG-ASSUR-001` may hold an adapter module, a service module, and internal
modules under `src/modules/`. This file records which modules exist, which
component they belong to, and whether they are public or internal. It is
consumed by tooling that needs to know, for example, which modules are
importable from outside the component versus which are private. It should
be regenerated from the tree, not edited by hand. It should never disagree
with the actual `src/` layout; if a module exists on disk but not here, that
is a drift bug. The file is the layer where "what is a component" stops
being a directory question and becomes an interface question. It is
therefore the natural place to record which modules are stable and which
are experimental, if that distinction matters for release scope. It should
remain small enough to read in full when debugging a component.

LOC: High for the data file (one record per module, several hundred across
the tree), Low for the generator.
Engineering effort: Low once the generator exists.

---

## catalog/requirements/requirements-map.json

Machine-readable map from requirements to components. Each requirement ID
(per the FAS nine-per-component rule) maps to the component that owns it.
This is the traceability index the Govern FAS calls the controlling
allocation register. It answers the question "which component is accountable
for this requirement" without requiring a reader to open 75 component
directories. It should be generated from the requirement entries in each
component\'s `docs/requirements.md`, not maintained by hand, because manual
edits drift the moment a requirement is reworded. It should carry, per
requirement: the ID, the owning component, the source FAS section, and the
conformance evidence link if one exists. It is the file a conformance
auditor reads first, because it is the only place where the answer to "is
every requirement owned" is visible in one screen. If the file and the
component docs disagree, the component docs are authoritative and the file
is stale. It should never contain a requirement with no owner; an orphan
requirement is a specification bug and should fail validation.

LOC: High for the data file, Low for the generator.
Engineering effort: Low once the generator exists, and once the component
requirements docs are complete.

---

## catalog/deployment-map.json

Machine-readable map from deployment profile to component set. Records which
components are active under which of the five ASF profiles — Mobile, Local,
Server, Enterprise, Global. It answers the question "if I am standing up the
Local profile, which components do I need." It should be generated from the
per-component release and profile declarations in `component.json`, not
edited by hand. It is consumed by deployment tooling and by the release
workflow when producing a profile-specific manifest. It must reflect the
FAS treatment of each profile: Mobile is validation-gated, Local and Server
are reference candidates, Enterprise is core local with federation deferred,
and Global is end-state with implementation deferred. Any profile that lists
a component as required must also list the components that component
depends on; a profile that omits a dependency is a broken profile. It should
not encode environment choices such as Docker versus native, because those
belong to the environment record, not to the profile map.

LOC: Medium for the data file (five profiles, component lists per profile),
Low for the generator.
Engineering effort: Low to Medium. Requires deciding which components are in
scope for each profile, which is a product decision, not a tooling one.

---

## catalog/release-scope.json

Machine-readable record of what is in and out of the current release. Records
which components are Core v1, which are deferred, which are
validation-gated, and which are research-quarantined. It is the file that
answers "is this component shipping in v1" without requiring a reader to
consult the FAS documents. It should be generated from the per-component
release declarations, not maintained by hand. It is consumed by the release
workflow and by any tooling that needs to exclude deferred components from a
build. It must reflect the FAS status of each item exactly: `COG-CMP-004`
(swarm coordinator) is research-gated, `GOV-FED-001` (federation gateway) is
deferred, `CMP-ECO-001` (economic optimizer) is validation-gated. A release
that includes a deferred component is a bug. The file should also record the
release version it applies to, so that a reader can tell whether a
component\'s status has changed since the release was cut.

LOC: Medium for the data file, Low for the generator.
Engineering effort: Low once the generator exists. The decision of what ships
is a product decision made elsewhere.

---

## components/ax/ (Aether Cognition)

Aether Cognition is the layer that develops and operates sovereign
intelligence. It contains 21 logical components across five families:
Interaction and Human Control (INT), Cognitive Runtime, State and Memory
(CORE), Knowledge, Reasoning and Planning (REA), Models, Skills and
Cognitive Composition (CMP), and Assurance, Security and Performance
(ASSUR). Each component is realized as a directory under `components/ax/`
containing README, component.json, CHANGELOG, src, tests, config,
migrations, and docs. The `src` directory holds three subdirectories —
`public`, `modules`, and `adapters` — which define what the component
exposes, what it holds internally, and how it talks to substrates outside
itself. The `tests` directory holds four subdirectories — `unit`,
`contract`, `component`, and `fixtures` — which separate fast tests from
integration tests from data. The `docs` directory holds at minimum four
files: design, state-model, failure-behavior, and requirements. Cognition
proposes. It does not authorize and it does not execute. Its components
receive a request, form a representation, resolve state, ground knowledge,
route to a substrate, reason, plan, evaluate, respond, and on a consequential
path create a capability request that Govern must authorize. The 21
components together define the full cognitive lifecycle described in §5 of
the Cognition FAS.

LOC: High across the layer. Individual components vary; the directory itself
is a container.
Engineering effort: High. This is one of three full layers and it carries the
reasoning, memory, and assurance machinery.

---

## components/ag/ (Aether Govern)

Aether Govern is the layer that decides whether proposed use of identity,
information, capabilities, and consequential action is permitted. It
contains 24 logical components across eight groups: Governance Kernel
(KRN), Identity and Authority (IAM), Policy (POL), Information Governance
(INF), Capability Coordination (CAP), Evidence and Assurance (EVD),
Administration and Operations (ADM), and Federation and Domain Exchange
(FED). Each component follows the same eight-entry layout as Cognition
components. Govern owns authority, policy, information flow, capability
eligibility, approval, evidence correlation, and outcome verification. It
does not reason, it does not plan, and it does not execute. Its output is a
decision — ALLOW, DENY, CONDITIONAL, ESCALATE, or INDETERMINATE — and when
the decision is ALLOW or CONDITIONAL, an ExecutionOrder that Compute may
act on. Govern is the only layer that can issue an execution order. It is
also the only layer that can revoke one. Its evidence components correlate
decision evidence with execution evidence and produce the GovernedOutcome
that Cognition consumes. The 24 components define the full governed
lifecycle described in §5 of the Govern FAS.

LOC: High across the layer. Govern is contract-heavy; each component carries
more schema surface than a typical Cognition component.
Engineering effort: High. This layer is where the majority of the contract
invariants are enforced.

---

## components/ac/ (Aether Compute)

Aether Compute is the layer that realizes authorized orders on physical
resources. It contains 30 logical components across eight families: Contract
and Control (CTL), Trust and Security (TRU), Topology and Resources (RES),
Workload and Execution (EXE), Data and Connectivity (DAT), Observation and
Evidence (EVD), and Economics (ECO). Compute accepts only bounded execution
orders issued through Govern. It establishes the eligible physical set,
allocates and schedules resources, realizes workloads through controlled
native systems, observes and recovers execution, and returns evidence
sufficient for Govern to verify and close the outcome. Compute cannot
broaden an order, substitute a capability, or reinterpret policy. It
qualifies and realizes; it does not decide. The 30 components define the
full execution lifecycle described in §6 of the Compute FAS. Of these, 29
are Core v1 and one — the Quote and Economic Optimizer — is
validation-gated. This is the layer an architect will stand up first,
because everything else depends on its ability to realize work.

LOC: High across the layer. Compute carries the most components and the
widest range of platform-specific code.
Engineering effort: High. This layer is where the environment decisions
(workload format, platform, storage) actually land.

---

## contracts/schemas/

Canonical schema directory, split into three subdirectories: `ax`, `ag`, and
`ac`, one per layer. Holds the JSON Schema (or equivalent) definitions for
every boundary object named in the FAS boundary alignment sections. This is
the normative source of truth for object shape across the system. A schema
change here has cross-layer effect and requires independent review. The
canonical schemas that take precedence over local names at layer boundaries
live at `40_CROSS_STACK_INTEGRATION/05_Canonical_Schemas`; this directory is
the working set from which those canonical versions are drawn, or the local
projections that conform to them. Every boundary object must validate
against the schema for its layer before it crosses a boundary. A schema in
this directory that disagrees with the canonical set is a bug. Schemas
should be versioned; a boundary object carries its schema version in the
Common Envelope, and a consumer that does not support that version must fail
closed. This directory is small in file count and large in consequence: a
change here can invalidate every component in the layer above it.

LOC: Medium to High depending on schema expressiveness. JSON Schema is
verbose; Protobuf or similar would be shorter.
Engineering effort: Medium to High. Each boundary object needs a schema, a
validator, and a test vector set covering valid, invalid, and downgrade
cases.

---

## contracts/apis/

Interface definitions for the APIs each layer exposes. Where `schemas/`
defines object shape, `apis/` defines the operations that accept and return
those objects. Holds API specifications — likely OpenAPI, gRPC proto, or
similar — for the boundaries between Cognition, Govern, and Compute, and for
any external-facing surface. Each API definition should name the boundary
object it carries, the direction of the call, and the failure semantics. An
API in this directory that bypasses the boundary contract set is a bug, not
a variant. APIs should be versioned alongside schemas. The directory is
consumed by interface tooling and by any client that talks to a layer
without going through the canonical schema path. It should not contain
implementation; that belongs under `components/`. This directory is the
place where the FAS boundary alignment table becomes executable.

LOC: Medium. API definitions are compact but each boundary needs one.
Engineering effort: Medium. Requires deciding transport, which is
`GOV-DEC-001` and `CMP-DEC-001`.

---

## contracts/events/

Event definitions for asynchronous notifications between layers. Where
`apis/` covers request-response, `events/` covers publish-subscribe. Holds
the definitions of events such as state transitions, revocations, and
evidence commits that other components may subscribe to. Every event
definition should name the emitting component, the payload schema, the
delivery guarantee, and whether it is idempotent. Cancellation and
revocation directives are the critical events; the FAS requires them to be
observable state transitions, not ordinary failures, and that requirement
lands here. An event that carries authority without a corresponding
AuthorizationDecision is a bug. Events should be versioned; a subscriber
that does not support the emitted version must fail closed for consequential
action. The directory is small and load-bearing: it defines how the system
propagates change without polling.

LOC: Low to Medium. Events are typically shorter than API definitions.
Engineering effort: Medium. The hard part is deciding which transitions are
events versus which are synchronous calls.

---

## contracts/fixtures/

Test fixtures for contracts. Holds valid and invalid instances of every
boundary object, used by contract tests to verify that schemas accept what
they should and reject what they should not. Each boundary object should
have at least four fixtures: a valid instance, a malformed instance, an
expired instance, and an unsigned or downgraded instance. This is the
directory that makes the fail-closed invariant testable. Without fixtures,
a schema is a document; with them, it is an executable requirement. Fixtures
should be small, hand-written, and stable; generated fixtures obscure the
exact case being tested. They should never contain real credentials,
real personal data, or anything that would be sensitive if leaked. The
directory is consumed by the contract test suite under `tests/`. A fixture
that passes when it should fail is a bug in the test, not in the schema.
This directory is the reason contract tests can run without standing up any
service.

LOC: Medium. One small file per fixture, four fixtures per boundary object.
Engineering effort: Low to Medium. Mechanical once schemas exist.

---

## libraries/auth/

Shared authentication and authorization library code. Holds primitives that
more than one component needs but that do not belong to any single
component. In ASF this should be minimal, because authority decisions belong
to Govern components, not to a shared library. What belongs here is the
mechanics of verifying a token, checking a signature, or resolving a
principal reference — not the policy of whether a given principal may do a
given thing. Anything that resembles a decision belongs in a Govern
component, where it is traceable. Code here is imported by many components,
so a change has broad blast radius and requires careful review. It should
have strong test coverage because a bug here affects everything. It should
not depend on any component; the dependency direction is components to
library, never library to component. If a function here starts to encode
policy, it should move to `GOV-IAM-003` or `GOV-POL-002`.

LOC: Low to Medium. Shared primitives are usually small.
Engineering effort: Medium. Requires discipline to keep policy out.

---

## libraries/crypto/

Shared cryptographic primitives. Holds hashing, signing, key derivation, and
similar operations used across layers. In ASF this library supports the
Common Envelope integrity field, the Omega Seal computation, and any
signature verification in the evidence path. It should wrap well-reviewed
libraries rather than implement primitives itself; a hand-rolled cipher is a
bug regardless of how correct it looks. It should expose a narrow interface:
sign, verify, hash, derive, and nothing more. It must not decide when to
sign or what to sign; that is component policy. It should be tested against
published test vectors for every primitive it wraps, so that a change in the
underlying library is caught immediately. Like `libraries/auth`, it must not
depend on components. Its API should be stable, because changes here ripple
everywhere. It is one of the two libraries where a bug is catastrophic, so
its review requirements should be the strictest in the repository.

LOC: Low. Thin wrappers.
Engineering effort: Medium to High. Test vectors and review discipline.

---

## libraries/logging/

Shared logging and telemetry primitives. Holds the structured logger used by
every component, plus helpers for correlation IDs and evidence context. In
ASF this library is more important than its size suggests, because the
evidence path depends on the ability to reconstruct what happened and in
what order. Every log entry should carry correlation and causation IDs from
the Common Envelope so that a reader can reconstruct a decision chain from
logs alone. The library must not decide what to log or at what level; that
is component policy. It must be fast enough that logging does not become a
bottleneck in the execution path, and it must be safe to call from any
thread. It should not depend on components, and it should be the only place
in the repository that writes directly to stdout or stderr outside of
tooling. Centralizing this makes it possible to change log format, add
redaction, or route to a collector without touching every component. Its
test coverage should verify that correlation IDs propagate correctly.

LOC: Low. A structured logger is a small file.
Engineering effort: Low to Medium. The hard part is discipline of use.

---

## deploy/units/core-runtime-unit/

Deployment unit definition. Holds everything needed to build, configure, and
run one deployable unit of ASF. The directory contains `unit.json` (the
unit\'s identity and dependencies), `build/` (build steps), `config/`
(configuration), `manifests/` (deployment manifests), `tests/` (unit-level
tests), and `runbook.md` (operational runbook). This is where the abstract
component graph becomes a concrete thing that runs on a machine. The
`unit.json` file names which components are included, which profiles the
unit supports, and which external dependencies the unit requires. The
`runbook.md` file should state, in operational terms, how to start the unit,
how to tell whether it is healthy, how to stop it, and what to do when it
fails. The unit should be reproducible: building it twice from the same
inputs produces the same artifact. It should never hard-code credentials or
environment-specific paths. This directory is the natural home for the
architect\'s decisions about workload format, because a unit is where that
decision becomes manifest.

LOC: Medium. Manifests and runbooks are short but numerous.
Engineering effort: Medium. Requires deciding deployment shape, which is
`CMP-DEC-003` and `CMP-DEC-004`.

---

## deploy/profiles/

Deployment profile definitions. Holds one subdirectory per ASF profile —
currently `departmental-cpu`, `enterprise-multidepartment`, and
`device-continuity` — each describing how ASF is configured for that
deployment context. This is where the abstract five-profile model from the
FAS becomes concrete. Each profile should name the components it includes,
the configuration overrides it applies, and the resource assumptions it
makes. A profile should not define new components or new contracts; it
selects among existing ones. The `departmental-cpu` profile is the closest
to a current reference candidate; the others may be sketches. Profiles
should be versioned. Adding a profile is a product decision, not an
engineering one, but the shape of the profile file is engineering.

LOC: Low to Medium per profile.
Engineering effort: Low to Medium per profile once the first exists.

---

## deploy/releases/

Release manifests, one directory per release version. Holds the record of
what was shipped, when, and from which commit. Each release directory
contains a `manifest.json` naming the version, the HEAD commit, the Python
version, the lockfile hash, the components included, and the status verdict
at release time. This directory is append-only: a release manifest is never
edited after the fact. It is the audit trail for what left the repository.
A reader should be able to answer, from this directory alone, which
component versions were in a given release, and which decisions were still
open when the release was cut. The manifest should also record the Omega
Seal from the orchestrator run at release time, if one was captured, so that
a release can be tied to a specific execution. Nothing here is generated at
runtime; it is written by the release workflow and committed.

LOC: Low per release. Accumulates over time.
Engineering effort: Low per release once the workflow exists.

---

## integration/cross-layer/

Cross-layer integration tests. Tests that exercise objects crossing a
boundary between Cognition, Govern, and Compute. Holds tests that verify the
Common Envelope is present and correct, that idempotency keys prevent
duplicate effects, that fail-closed behavior triggers on invalid objects,
and that cancellation and revocation propagate as observable transitions.
These are the tests that verify the contract invariants, not the behavior of
any single component. A test here that passes with a broken boundary is a
bug. Tests in this directory should be runnable without external services
where possible, using fixture data from `contracts/fixtures/`. They should
be fast enough to run on every pull request, because a boundary regression
is the most costly kind of regression in a three-layer system. They are the
direct executable counterpart to the FAS boundary alignment sections.

LOC: Medium to High. One test file per boundary object, plus invariant tests.
Engineering effort: Medium. Mechanical once fixtures exist, but requires
discipline to keep tests focused on the boundary rather than on component
behavior.

---

## integration/authority/

Authority integration tests. Tests that exercise the identity, delegation,
consent, approval, and revocation paths across components. Holds tests that
verify authentication is not treated as authorization, that delegation
chains do not amplify, that revocation blocks new orders and marks
in-flight work, and that human approval is explicit rather than inferred
from silence. These tests correspond directly to the Govern FAS §8
requirements. A test here should be able to construct a delegation chain,
attempt an amplification, and confirm the attempt fails. Authority bugs are
the most dangerous kind in a governed system, so these tests should run on
every pull request and should be the last thing relaxed if the suite grows
slow. They are also the tests most likely to catch a regression introduced
by a change in a shared library such as `libraries/auth`, because they
exercise the composition of many authority decisions rather than any single
one.

LOC: Medium. One file per authority concern.
Engineering effort: Medium. Requires a clean delegation model to test against.

---

## integration/sovereignty/

Sovereignty integration tests. Tests that verify a sovereign domain does not
leak private state into another domain, that federation does not transfer
authority, and that cross-domain consultation returns only what was
authorized. Holds tests for the boundary between Personal, Enterprise, and
Global ASF profiles. Most of this territory is deferred — `GOV-DEC-011` and
`CMP-DEC-017` are both Deferred — so this directory may contain mostly
fixtures and placeholders in v1. What exists should verify that Global ASF
consultation does not authorize disclosure of unrelated private state, and
that a requesting domain independently controls outbound disclosure and
inbound release. These tests are important even when the feature is deferred,
because they encode the constraints that any future federation implementation
must satisfy. A sovereignty test that passes when a private state leaks is
the highest-cost failure mode in the suite.

LOC: Low in v1, expected to grow.
Engineering effort: Low in v1, High once federation is implemented.

---

## integration/e2e/

End-to-end tests. Holds the full-stack diagnostic and any other test that
exercises the entire system from request to governed outcome. The primary
file here is `test_full_stack_diagnostic.py`, which runs across AC, AG, and
AX and prints five checkmarks plus a success line. This is the executable
definition of "ASF runs." Tests here should be runnable from a clean clone
with no external services, because they are the first thing a new
contributor runs and the last thing a release engineer runs before tagging.
They should be slow enough to be meaningful and fast enough to run on every
push; if a full-stack test takes more than a few minutes, it belongs in a
scheduled workflow, not in `ci.yml`. Failures here should name the layer
that failed, not just the assertion that tripped. This directory is small in
file count and large in consequence: a broken E2E test means the system does
not hold together.

LOC: Medium. The diagnostic is one substantial file.
Engineering effort: Medium. The work is keeping it fast and reliable.

---

## docs/AUTHORITY.md

Authority model documentation. States, in one place, who can decide what.
Covers the separation of authentication from authorization, the structure of
delegation and consent, the conditions under which human approval is
required, the semantics of revocation, and the break-glass procedure. This
is the file an auditor reads first, because authority bugs are the most
consequential kind. It should be readable by a non-engineer. It should not
duplicate the Govern FAS; it should reference the FAS for normative
statements and describe the current implementation. If the implementation
and the FAS disagree, the FAS is authoritative and this file should note the
discrepancy. It should state explicitly that no component may grant itself
authority, and that silence is not consent. It should be short enough to
read in one sitting.

LOC: Low to Medium. Prose, not code.
Engineering effort: Low to Medium. Requires consensus on the authority model.

---

## docs/STATUS.md

Repository status documentation. States the current state of the repo: what
is built, what is deferred, what is open, and what is blocked. Complements
`tooling/validation/status.py`, which is the runtime check; this file is the
narrative check. Should be updated whenever a decision closes or a component
changes release scope. Should list the open decisions from the FAS tables,
the blockers from the current work, and the last verification run. Should
not attempt to be a changelog; that belongs elsewhere. This is the file a
returning contributor reads to reorient.

LOC: Low. One page.
Engineering effort: Low. Requires discipline to keep current.

---

## docs/architecture/

Architecture documentation. Holds the architect onboarding guide, the module
reference, and any diagrams that explain the system. This is the directory
a new contributor reads to understand the whole, before reading code. Files
here should be one of three kinds: onboarding (how to read the repo),
reference (what each module is), or diagram (how the layers relate). They
should not duplicate the FAS documents. They should link to the FAS for
normative statements. They should be updated when the code changes shape,
not on a schedule.

LOC: Medium to High. Accumulates.
Engineering effort: Medium. Each document is a sitting.

---

## docs/decisions/

Architecture decision records. One file per decision, numbered, immutable
after acceptance. Records the question, the options considered, the choice,
and the consequences. This is where the answers to `GOV-DEC-*` and `CMP-DEC-*`
should be recorded when they close. An ADR is never edited; a decision that
changes is superseded by a new ADR that references the old one. The
directory is the audit trail for why the system is shaped the way it is.

LOC: Low per ADR.
Engineering effort: Low per ADR. Discipline to write them is the hard part.

---

## tooling/bootstrap/

Bootstrap scripts. Holds scripts that stand up a development environment or a
deployment unit from a clean checkout. Should be idempotent, should not
require network access beyond package installation, and should print clear
success or failure. This is where the "clone and run" experience lives.

LOC: Low to Medium.
Engineering effort: Low to Medium.

---

## tooling/validation/

Validation tooling. Holds `status.py`, `spec_audit.py`,
`platform_validate.py`, `validate_profiles.py`, and `check_federation_gate.py`.
These are the gates that CI and the Makefile invoke. Each should be
read-only, idempotent, and fail with a clear message. This directory is the
executable counterpart to `docs/STATUS.md`.

LOC: Medium. Each script is small; the set is substantial.
Engineering effort: Medium. Requires each gate to be correct.

---

## tooling/release/

Release tooling. Holds scripts that build the release manifest, tag the
commit, and publish artifacts. Should be callable from CI and from a
developer workstation. Should not decide release policy; that is a human
decision.

LOC: Low to Medium.
Engineering effort: Low to Medium.

---

## examples/synthetic-fixtures/

Synthetic example data. Holds fixtures that illustrate what a real boundary
object looks like, without using real data. Used by tests and by
documentation. Should be small and readable. Should never contain anything
sensitive. This is the directory a new contributor reads to see a concrete
example of the abstract contract.

LOC: Low to Medium.
Engineering effort: Low.

---

**End of reference.**

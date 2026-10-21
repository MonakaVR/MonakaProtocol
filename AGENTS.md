# MonakaVR Input Protocol (MVIP) repository instructions

This repository is the authority for the shared, versioned observation and tracking protocol: data models, schemas, capability vocabulary and semantics, codecs, validation, fixtures, compatibility rules, and distributable contract kits. It defines contracts, not runtime device integrations.

## Highest-priority invariant: producer-independent protocol

This constraint applies to all code, tests, fixtures, build scripts, packaging, and documentation. The protocol MUST remain independent of the implementation, vendor, manufacturer, model, physical device, transport, and runtime of any particular input producer.

The following five categories are **strictly prohibited**:

1. **Device-specific access:** implementing physical-device discovery, pairing, communication, control, acquisition, or recovery.
2. **Private dependencies:** importing, linking, embedding, wrapping, or reimplementing a producer-specific SDK, API, ABI, driver, private packet protocol, or internal data model.
3. **Hard-coded device identity:** embedding physical addresses, vendor/product IDs, device models, product-name tables, or other implementation-specific identity constants as contract policy.
4. **Identity-driven behavior:** branching on manufacturer, model, device name, producer kind, or magic strings/prefixes within opaque identifiers to select capability, validity, coordinate, routing, or recovery behavior.
5. **Producer-specific runtime logic:** implementing producer-specific packet decoding, coordinate correction, tracking heuristics, session/reconnect control, or runtime services.

**Do not list concrete input producers, vendors, manufacturers, device families, or hardware models in this AGENTS.md.** Use abstract roles and public contract terminology. The prohibition is universal, not limited to any enumerated examples.

Opaque identity and descriptive metadata (including device ID, manufacturer/model strings, or external resource identifiers) MAY be defined, validated, serialized, and transported by a public schema. They MUST NOT trigger producer-specific interpretation. A generic wire codec is allowed; a decoder for a concrete producer's private wire format is not.

A violation is an **architecture defect and release blocker**, not an optional refactor.

## Repository and runtime boundary

- Own versioned models, canonical capabilities vocabulary and semantics, schemas, codecs, validation, fixtures, cross-language conformance, and reproducible protocol kits.
- Do NOT add hardware access, transport/socket services, process management, producer configuration, producer discovery, or runtime lifecycle ownership.
- Do NOT add bridge mapping/calibration execution, body assignment, Fusion/Fallback/IK policy, GUI, or SteamVR driver/output implementation. These responsibilities belong to their runtime owners.
- Do NOT make any conforming producer or consumer require an implementation-specific extension or private registration path.
- Define optional device descriptors or future resource references only through an explicitly reviewed, versioned public contract. Leave local filesystem resolution, proprietary resource acquisition, and rendering to the responsible runtime/output adapter.
- Treat `source_id`, `device_id`, `publisher_id`, and `tracker_id` as case-sensitive opaque values subject to the contract's scope and identity rules. Do not infer device type, capability, body role, or native coordinate frame from their spelling.

## Contract authority, precedence, and compatibility

- Current normative, applicable protocol specifications, including `docs/C2.md`, subsequent version-specific amendments, and `docs/capabilities-contract.md`, take precedence for their respective scope over the historical `docs/codex/Task1_MonakaProtocol.md` / C1-only implementation plan.
- Read the historical task document for provenance and nonconflicting constraints, NOT as permission to overwrite current contracts or regress to an earlier wire version.
- `schema/capabilities.json` is the single canonical capabilities vocabulary. Native/JVM generated declarations, semantics, and validation MUST agree with that vocabulary and the frozen wire schemas.
- Static `capabilities` represent supported semantic channels in the admitted device/session contract. Dynamic validity, sample presence, tracking quality, freshness, and admission are distinct. Do not infer support from a sample's existence or discard declared support on transient loss.
- Modality and identity/session/space/timestamp semantics MUST follow the applicable versioned contract. Metadata messages MUST NOT refresh pose freshness; invalid diagnostic fields MUST NOT become usable channels.
- Do not fabricate, silently modify, or reinterpret fields, units, coordinate conventions, clocks, sequence semantics, ownership, message types, enum sets, public API names, or wire version/compatibility rules.
- A wire-breaking or semantic change requires an explicit architectural decision, version/migration plan, updated schemas/codecs/fixtures, and coordinated producer/consumer compatibility evidence. Do not automatically upgrade old packets by guessing missing fields.
- Preserve existing frozen codec bytes and message-specific minor-version behavior unless the approved change explicitly authorizes otherwise. Do not rewrite unrelated fixtures or source-pinned evidence.
- Build and distribute source/content-hash-pinned contract kits from a clean committed state with verifiable manifests. Do not invent hashes, reuse an unmatched kit, or assume a live sibling checkout is the source of truth.

## Verification and review gates

Before changing a public contract, enumerate affected versions, producers, consumers, and bindings **by abstract interface/role**, then document compatibility impact and authorization. For each applicable change:

1. Validate schema and codec behavior across supported languages, including invalid/unknown values, duplicate declarations, replay, missing fields, and frozen fixtures.
2. Verify at least two distinct synthetic producer identities with equivalent valid messages are interpreted identically, without implementation-name conditions.
3. Verify static capability versus dynamic validity, identity/session/space, coordinate, and timestamp semantics.
4. Verify generated vocabulary, codec/API signatures, package manifests, dependency/source pins, and compatibility gates.
5. Check the diff for producer-specific names, hard-coded identifiers, private API dependencies, transport runtimes, or hidden device-specific branches.

Report builds, tests, compatibility checks, and hardware validation separately. Mark any unrun check `NOT RUN`; do not claim runtime/HIL acceptance from library-only tests.

## Git and task discipline

- Work only in this repository unless the active task explicitly authorizes others.
- Base new work on `dev` unless the task supplies a different validated base. Do not rewrite frozen task or HIL baselines merely to synchronize instructions.
- Preserve unrelated work and uncommitted changes. Do not delete branches, force-push, rebase, amend unrelated commits, or reset away history.
- Keep changes small, reviewable, and accompanied by conformance evidence.
- If a task instruction conflicts with this producer-independence invariant or the active normative contract, stop at the conflicting boundary and report it instead of guessing or silently implementing a workaround.

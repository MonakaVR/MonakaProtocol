# MonakaVR Input Protocol

Phase 2C-P1 implementation: [normative capabilities contract](docs/capabilities-contract.md),
[exact P0 findings](docs/p1/p0-capabilities-findings.md). Canonical capabilities
describe supported semantic channels; current validity and sample presence are
separate. C++17 and JVM17 provide the same pure projection and declaration check.
The selected frozen wire-2.2-compatible v2 codec retains its original public API
and message-specific wire 2.0/2.1/2.2 behavior. No historical branch was merged.

Build with CMake (`-DMVIP_BUILD_TESTS=ON`) in `build/native`, and Gradle 8.14.4
`-p jvm build`. Run `python tools/verify_frozen.py`,
`python tools/generate_capabilities.py --check`, and `python tools/test_contract.py`.
The runner uses Java 17 (`JAVA_HOME`, or the documented local JDK fallback),
MSVC Release executables and the built JVM JAR. Frozen canonical output hashes
come from the P0 source-bound C++/JVM evidence, not from the new encoder.

`python tools/package_contract.py` produces a content/source-pinned kit from a
clean committed implementation; MBIP consumes this artifact rather than a live
sibling checkout. `fixtures/p1` includes synthetic protocol coverage and private
admission annotations in its test index, never new raw-quality wire fields.

`PICO same-tracker IMU authenticity: NOT VERIFIED / DEFERRED`

Shared input protocol contracts for [MonakaVR](https://github.com/MonakaVR/MonakaVR).

This repository defines the versioned interfaces and data representation used to deliver normalized tracking observations to the MonakaVR pipeline. Its responsibilities are protocol contracts, models, schemas, codecs, validation, conformance fixtures, and distributable protocol kits; it is not a runtime bridge.

## Architecture

```text
Device-specific tracking backends
          |
          v
MonakaBridge / input adapters
          |
          v
MonakaVR Input Protocol contract
          |
          v
MonakaVR (Fusion / Fallback / IK)
          |
          v
Virtual tracker outputs
```

The drawing is conceptual; it does not specify a transport, wire format, ABI, or executable dependency graph.

## Repository boundary

**In scope:** shared protocol structures, schemas/codecs, validation, version compatibility, test fixtures, and distributable contract kits.

**Out of scope:** device access, PICO/VIVE pairing, runtime socket services, mapping/calibration UI, body-role assignment, Fusion/Fallback/IK algorithms, and SteamVR driver implementation.

The separate [MonakaBridge Input Protocol](https://github.com/MonakaVR/MonakaBridgeInputProtocol) defines the input-module boundary **into MonakaBridge**. This repository defines the **MonakaVR-side** input contract; the two interfaces must not be conflated.

## Status

The repository contains prior design instructions on `main`. Implementation work also exists on separate development branches and is **not** implied to be integrated into `main`. Consult the relevant branch and its specifications to determine actual implementation status.

Before changing existing wire fields, units, coordinate conventions, timestamps, versions or public APIs, review the normative design and compatibility requirements. Do not treat this bootstrap README as a replacement for those specifications.

## Branch policy

- `main`: stable baseline
- `dev`: integration branch for active development
- `feature/*`, `refactor/*`: task-specific work, retained as-is during bootstrap

## Codex instructions

See [AGENTS.md](AGENTS.md) and the existing [task specification](docs/codex/Task1_MonakaProtocol.md).

## License

No standalone license is declared by this repository bootstrap. Check applicable upstream and third-party licenses before distributing implementations.

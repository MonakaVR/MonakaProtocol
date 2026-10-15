# Exact P0 findings for P1

Source: C:\Users\nynyp\Downloads\6Dof\hil\phase2cp0-protocol-audit-20261015\report.md

SHA256: `5ed80d135a9e3a76c835d2312f7ce9d58b749e397e465190b2fc6b0c561f200c`

**H-01 — 同じwire 2.0でcapabilitiesのlifetime解釈が不一致。** Bridge refactor `84f5b752…` のposeは実際に存在するderivativeだけをcapabilitiesへ加え、stateはposition/orientationのみを送る。calibrateは2つ目以降のQからangular_velocityを導出する。Core integration `0cee1fda…` はpose/stateを問わず宣言差分をCapabilityConflictとして同lifetimeを拒否する。数値/validityが正常でも発生する。新Bridge integration `f8a01b4c…` は静的outputCapabilitiesを保つため、この修正系統と古いBridgeを混在させない適合表が必要。**コード経路で確定、今回の実process再現は未実行**。[B1:42–60, B3, B5:13–28/163–198, R1:187–193, D1:21–26]

**M-02 — same-trackerの独立inertial modality/provenanceがshared境界にない。** 安定identityだけでは別周期streamのcache/sequence分離と物理同一性を表せない。derivative、fused Q、raw IMUを同義にしない。[C1, P5, A5, B2, R1]

**M-03 — raw/candidate/admittedの診断契約がない。** effective validityでBackend gateは構成可能だが、candidate/raw事実は外部共通consumerから明示的には見えない。診断をBackendへ保つ方針を文書化し、同sequenceのvalidity書換えとage刷新を禁止する必要がある。[C1, C2, P1, B2]

**M-05 — restart/space/capabilityを跨ぐ固定refのcontract integration gateが不足。** 個別testはあるが、H-01の新旧組合せ、transport-only再開と再承認不要条件、legacy C ABIのretired sessionまでを一括保証する今回の証拠はない。今回のnative/JVM codec互換PASSは、これらruntime policyの一致を証明しない。[P4, A4, W5, W6, R1]

M-02: multi-channel representability is in scope; independent raw IMU streams/authenticity remain deferred. M-03: effective validity/diagnostic separation only. M-05: capability-related compatibility harness only; session/space/reconnect remain deferred. No severity is changed.

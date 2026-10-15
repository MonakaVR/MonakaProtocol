"""Generate the P1 report/receipts in development clones only."""
import datetime,hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[1];MB=R.parent/'MonakaBridgeInputProtocol';W=R.parents[1]
def git(path,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(path),*args]).decode().strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
start=json.loads((R/'docs/p1/phase-start.json').read_text())
p0=W/'hil/phase2cp0-protocol-audit-20261015'
assert sha(p0/'report.md')==start['p0_report_sha256']
assert sha(p0/'frozen-targets.md')==start['p0_targets_sha256']
audits=[]
for row in start['states']:
 if row['role']!='audit':continue
 path=pathlib.Path(row['path'])
 assert git(path,'rev-parse','HEAD')==row['head']
 assert git(path,'branch','--show-current')==row['branch']
 assert not git(path,'status','--porcelain=v1')
 audits.append(dict(path=str(path),branch=row['branch'],sha=row['head'],clean=True,unchanged=True))
m=json.loads((R/'build/test-results.json').read_text());b=json.loads((MB/'build/test-results.json').read_text());pin=json.loads((MB/'dependencies/mvip.lock.json').read_text())
assert m['status']==b['status']=='PASS' and m['source_commit']==pin['source_commit']==b['mvip_source_commit']
assert b['original_capability_mismatch']=='RESOLVED'
commands=[
 dict(repository='MVIP',command='cmake -S cpp -B build/native -G "Visual Studio 18 2026" -A x64 -DMVIP_BUILD_TESTS=ON; cmake --build build/native --config Release',result='PASS',kind='MSVC C++17 build'),
 dict(repository='MVIP',command='gradle -p jvm --offline --no-daemon build',result='PASS',kind='JDK17 / Kotlin2.3.10 / Gradle8.14.4 build; explicit runner counts below'),
 dict(repository='MVIP',command='ctest --test-dir build/native -C Release --output-on-failure',result='PASS',tests=2),
 dict(repository='MVIP',command='python tools/test_contract.py',result=m),
 dict(repository='MVIP',command='python tools/verify_frozen.py; python tools/generate_capabilities.py --check',result='PASS; 193 immutable reference hashes + generated vocabulary drift'),
 dict(repository='MBIP',command='cmake -S cpp -B build/native -G "Visual Studio 18 2026" -A x64; cmake --build build/native --config Release',result='PASS',kind='native normalizer / encoder build'),
 dict(repository='MBIP',command='gradle -p jvm --offline --no-daemon build',result='PASS'),
 dict(repository='MBIP',command='python tools/verify_mvip.py; python tools/generate_mapping.py --check; python tools/generate_core_probe.py --check',result='PASS; pinned ZIP/JAR/member inventory, mapping and exact Core block drift'),
 dict(repository='MBIP',command='python tools/test_boundary.py',result=b)]
binaries={}
for owner,path in [('MVIP',R/'build/native/Release/mvip_codec_runner.exe'),('MVIP',R/'build/native/Release/mvip_capabilities_runner.exe'),('MVIP',R/'jvm/build/libs/monaka-input-protocol.jar'),('MBIP',MB/'build/native/Release/mbip_capabilities_runner.exe'),('MBIP',MB/'jvm/build/libs/monaka-bridge-capabilities.jar')]:binaries[owner+'/'+path.name]=sha(path)
validation=dict(phase='2C-P1',tested_at_jst=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),fixture_version='p1 + frozen monaka wire 2.0/2.1/2.2',mvip_implementation_sha=m['source_commit'],mbip_implementation_sha=b['mbip_source_commit'],mvip_kit_sha256=pin['sha256'],commands=commands,binary_sha256=binaries,audit_clones=audits,p0_source_hashes=dict(report=start['p0_report_sha256'],targets=start['p0_targets_sha256']),dev_main_merges=0,backend_core_production_edits=0,issue_changes=0,hardware='NOT RUN')
for root in [R,MB]:
 out=root/'docs/p1';out.mkdir(parents=True,exist_ok=True)
 (out/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
quoted='\n\n'.join(next(line for line in (p0/'report.md').read_text(encoding='utf-8').splitlines() if line.startswith('**'+ident+' ')) for ident in ['H-01','M-02','M-03','M-05'])
rows=json.loads((MB/'schema/capability-mapping.json').read_text())['rows']
table='\n'.join('| '+r['source']+' | '+r['validity']+' | '+r['target']+' | support/presence/effective validityを別factsで保持 | '+r['class']+' |' for r in rows)
report=f'''# Phase 2C-P1 — Capabilities Contract Reconciliation

実施日: 2026-10-15 (Asia/Tokyo)

**PASS WITH DEFERRED NON-CAPABILITY GAPS**

元のcapabilities意味論不一致: **RESOLVED**。
これはP1の明示契約・adapter・固定Core比較harnessでの判定であり、旧Bridgeを
そのまま旧Core/新Coreへ直結したproduction経路を変更したという意味ではない。
legacy producerの適合には、provisioned declaration付きadapterを明示的に使う必要がある。

## Development branch/SHA table

| Repository | Dedicated branch | 指定base SHA | 検証済みimplementation SHA |
|---|---|---|---|
| MonakaVR/MonakaVRInputProtocol | fix/capabilities-contract-reconciliation-v2c-p1 | cad72656f6e90def6dc55ee4c20fe9a181d37baf | {m['source_commit']} |
| MonakaVR/MonakaBridgeInputProtocol | fix/capabilities-contract-reconciliation-v2c-p1 | e334bfeceb7f922b3cacfc0d17eace82c0fabf33 | {b['mbip_source_commit']} |

この表はtested runtime/sourceを固定する。report/validation文書のdelivery commitは追加される。
push後の最終local/remote HEAD・clean確認は、各cloneの明示的なignored build/completion.jsonと
最終回答に記録する。dev/mainへmergeしない。旧feature branchのmergeは0。

## P0 Source of Truth / exact findings

P0 report: `C:/Users/nynyp/Downloads/6Dof/hil/phase2cp0-protocol-audit-20261015/report.md`

P0 SHA256: `{start['p0_report_sha256']}`

frozen-targets SHA256: `{start['p0_targets_sha256']}`

以下はreportから原文抽出。severity・内容は再構成していない。

{quoted}

## Normative capabilities contract

先にMVIP `docs/capabilities-contract.md`、MBIP `docs/capability-mapping.md` を仕様commitとして作成した。
capabilitiesはdevice/sourceが現session contractで提供できるsemantic channelであり、
current validity・field presence・quality・admission・Core recovery stateではない。
temporary loss/absence/stale/reacquireで宣言を消さず、pose/stateで同じ集合を保持する。

宣言scopeはfamily/publisher(存在時)/source/deviceまたはtracker/session。
セッションの認可/retired/leaseは既存receiver側の責務。capability変化のために
identity/session/spaceを自動生成し直す処理はない。新しい明示admitted sessionには別宣言を設定可能。

既存7 tokensのみ。unknownはUnsupportedValue、duplicateはInconsistentValidity、空集合は無効sampleと
整合する限り許可。意味論はsetでorder非依存、旧codecの配列順序/canonical bytesは不変。
明示declarationのmaterialization順はvocabulary順。新token/新wire field/新versionは追加していない。

## Capability vs validity model

各channelにsupported / sample_present / validを分離し、UNSUPPORTED / ABSENT / INVALID / VALIDで区別する。
capabilityだけでvalidにならず、false validityでもsupportは残る。有限の無効P/Qは診断として保持する。
metadataのpresence/tracked表記はP/Q sampleを生成しない。batteryの0とcharging=falseは有効metadata値。

独立validity bitのないderivativeは保守的に親pose validityも要求する。linear velocity/accelerationはP、
angular velocityはQが有効な場合だけ利用可能。loss中に残った非null数値はINVALID診断であり、
存在だけから有効化しない。これは固定Bridgeの既存parent-validity gateに合わせたprofileである。
raw gyro/accelerometerや親poseから独立したraw derivative validityは未定義のまま推測しない。
全てのVALID factsも別途freshness/mapping/authorization判定を要する。

## MVIP implementation

- C++17 `monaka::input`、JVM17 `dev.monaka.input` にcanonical capability enum/set、projection、pure binding check。
- vocabularyはschema/capabilities.jsonから両言語生成し、旧wire schemaの7語とdrift検査する。
- 旧feature `0b4a27c2e2de88705c92fb6dbf5a8d9ca752bf39` からv2 codec/models/schema/docs/fixtures/dependenciesを
  **193 files、個別blob hash固定で選択import**。v1 runtime/branch history/production servicesの丸ごとmergeは0。
- codecのUTF-8/size/depth/duplicate/enum/finite/quaternion/identity/time validationとpublic v2 APIは変更しない。
- source/JAR/content-hash固定kitを生成。MBIPの利用kit SHA256は `{pin['sha256']}`。

## MBIP implementation

native/JVMのpure NormalizerとCore-facing channel factsを実装した。MVIPは生成済みsource/hash固定kitで参照し、
独自capability enum/schema/codecは保有しない。vendor内の定義はMVIP配布物そのものと照合する。

STRICTが既定。source/publisher/entity/sessionとprovisioned declarationを照合し、不一致は出力せず拒否する。
LEGACY_DYNAMICは明示opt-inで、provenance付き構造宣言が必須。packetのadvertised集合が宣言のsubsetである場合だけ
全宣言へ補正する。validity/field presence/packet union/vendor名からsupportを推定しない。
identity/input provenance/time/sequence/space/mapping revisionを保持し、変更するのは宣言capability listだけ。
宣言なし、宣言外channel、foreign identity/sessionはrejectする。

これはchannel factsの正規化であり、raw Observationをcalibrated MTPへ変換する機能ではない。
元protocol family/coordinate conventionを保持し、Core poseには既存のmapping/calibrationを別途必要とする。
新DLL ABI、production receiver、routing、PICO/Altra backend、Core/Fusionには変更していない。

## Translation matrix

implicitなfield-name一致ではなくschema/capability-mapping.jsonから生成したdispatchを使う。

| MVIP capability | MVIP validity signal | MBIP representation | Core meaning | Class |
|---|---|---|---|---|
{table}
| raw gyro / raw accelerometer request | 既存token/fieldなし | channelなし | 推定しない | UNSUPPORTED |
| unknown / duplicate token | 不正宣言 | 出力なし | fail closed | REJECTED |
| HMD authority / Common World | capability-bearing sampleではない | 出力なし | 別authority consumerが担当 | REJECTED |

RENAMED/DERIVEDのcurrent rowsは0。adapterでsampleの導出を実装したとは主張しない。

## Golden / compatibility fixtures

P1の22 golden cases: supported-valid、supported-invalid、optional absent、unsupported、empty、order変更、unknown、duplicate、
未宣言derivative/valid-P、metadata、residual derivative diagnostics、same-tracker synthetic、admission、session restart、
source/publisher isolation、旧Bridge first/derived/state。inputsとexpected statesを別に固定した。
old canonical output hashesはP0の実C++/JVM出力から採取し、新encoderから期待値を作っていない。

## Same-tracker synthetic representability

同じsource/device/session/clock/space/capabilitiesでP+Q+angular_velocityのFULLからposition-invalid/Q-validへ遷移する。
synthetic fixtureのQ/angular velocityはProtocol表現可能性だけの証拠。新device/trackerは作らない。
独立した別周期raw IMU streamのprovenance/cache/clock modelを完成させた証拠ではない。

**PICO same-tracker IMU authenticity: NOT VERIFIED / DEFERRED**

## PICO admission-gate compatibility

raw_valid/stateはtest indexだけのprivate annotation。wireへ新field/enum/timerを追加しない。
candidateはeffective invalidity、admittedはeffective validityで、同じidentity/session/space/position capabilityを保持する。
sample sequenceは1/2/3、timestampは100/130/160、sent_atは120/150/180。古いsampleをrestampせず、同sequenceの
immutable validityを書き換えない。PICO-likeのQはloss中NONE、synthetic Q-onlyとは分離した。
Core-visible validityの変化にcapability再宣言やCore recovery policyの変更は不要。

## Test results

| Check | Result |
|---|---|
| MVIP native MSVC C++17 + JVM JDK17/Kotlin2.3.10/Gradle8.14.4 build | PASS |
| MVIP native CTest | 2/2 PASS |
| frozen v2.0/v2.1/v2.2 existing fixtures | {m['frozen_fixtures']} fixtures / {m['codec_probes']} codec probes PASS |
| existing fixture C++↔JVM directions | {m['cross_language_directions']} PASS |
| P1 semantic probes | {m['semantic_probes']} PASS |
| capability/codec API self tests | {m['api_self_tests']} PASS |
| MBIP native/JVM build | PASS |
| native/JVM boundary probes | {b['native_jvm_boundary_probes']} PASS |
| real MVIP serialization -> opposite-language MBIP | {b['cross_repo_serialized_directions']} directions PASS |
| faulty capability=>valid consumer / loss=>drop producer | 2 intentional negative mutants detected |
| exact frozen Core comparison BEFORE | conflict=true, conflicts=2 |
| same comparison AFTER provisioned native/JVM normalization | both conflict=false, conflicts=0 |
| source/vendor/mapping/probe drift checks | PASS |

実行command、tested commit、fixture version、binary hashesは同directoryのvalidation.jsonに記録した。
Gradle build/test taskの成功をrunner件数へ加算していない。Linux/Android/HIL/production integrationはNOT RUN。
Windows sandbox内のGradle native-services初期化失敗後、同じdevelopment cloneで権限付きoffline buildを完了した。

## Frozen wire 2.2 compatibility

**No wire version bump required / implemented.** wire構造/codec bytesは保持し、意味の区別と明示adapterを追加した。
trackingは2.0、source authorityは2.1、publisher-bound Common Worldは2.2のまま。
Common Worldの7 valid vectorsはcodecでdecode/re-encodeでき、capability projectionでは理由付きUnsupportedMessageとする。
publisher-B/source_publisher_id分離、旧nullable identity、source/publisher/session/provenanceを弱めていない。
旧dynamic producerは明示構造宣言があればadapt可能。宣言なしで正本のsupportを復元する推測はREJECTED。

## P0 finding closure matrix

original severityを維持し、capability意味論の修正と独立raw-stream/production範囲を分ける。

| P0 finding | Severity | Root cause | Spec fix | Code fix | Test | Status |
|---|---|---|---|---|---|---|
| H-01 | HIGH | dynamic sample declaration vs static Core lifetime | stable set / explicit legacy migration | strict binding + provisioned normalizer | actual frozen Core block before/after | FIXED |
| M-02: channel representability portion | MEDIUM | physical identityとchannel validityの混同 | stable multi-channel identity | support/presence/valid facts | synthetic P-loss Q/omega-valid | FIXED |
| M-02: independent raw-stream/provenance remainder | MEDIUM | 別rate/clock/raw IMU identity modelなし | P1外の範囲を明記 | 未実装、backend証明なし | syntheticはproofに昇格しない | BLOCKED — ARCHITECTURAL DECISION REQUIRED |
| M-03 | MEDIUM | raw/candidate/admittedの責務不明 | raw/gateはBackend、wireはeffective validity | raw quality fieldを追加せず保持 | candidate->admitted stable identity/caps | FIXED |
| M-05: capability integration portion | MEDIUM | 新旧ref適合gate不足 | explicit binding/profile | cross-repo harness + pinned Core comparison | old conflict / normalized no conflict、negative cases | FIXED |
| M-05: transport/space/legacy replay remainder | MEDIUM | capability以外のruntime gate | 除外範囲を明示 | P1では変更しない | NOT RUN / later phase | BLOCKED — ARCHITECTURAL DECISION REQUIRED |

元のM-02/M-05全体が解消したとは主張しない。独立raw-stream設計やtransport policyはcapability集合の意味論ではなく、
承認されたP1範囲外の残余として保存する。P1 capability reconciliation自体に未決のwire/version判断はない。

## Deferred non-capability P0 findings / unchanged scope

H-02(sender-session/space)、H-03(legacy retired-session)、M-01(production Core2.2 readiness)、M-04(full MBIP DLL ABI)、
L-01(historical rename/locks)、M-02/M-05の上記残余はDEFERRED。severityを下げない。
Issue #6、PICO reacquire gate本体、Altra ownership、Core RECOVERY_DWELL/BLEND、production receiver、backend reconnectは変更0。
audit clones2つとP0 report/frozen-targetsは不変。その他repositoryへのsource変更0。Issue変更0、dev/main merge0。

## Final decision / next step

**PASS WITH DEFERRED NON-CAPABILITY GAPS**

H-01: RESOLVED at the explicit protocol compatibility boundary. 旧直結経路をadapterなしで混在させない。
専用branchだけをpushし、merge順序はoperator reviewへ委ねる。次はP0固定beforeとP1 tested SHAの狭いpost-fix audit。
残るHIGH non-capability findingsを解決するまでPICO gate/HILへ進まない。

`PICO same-tracker IMU authenticity: NOT VERIFIED / DEFERRED`
'''
for root in [R,MB]:
 (root/'docs/p1/report.md').write_text(report,encoding='utf-8',newline='\n')
print('Generated P1 report/validation; audit clones unchanged')

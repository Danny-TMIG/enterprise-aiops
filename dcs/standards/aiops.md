# Enterprise AIOps Reference Standard

**Standard**: `dcs.aiops@1.0.0`  
**Published**: 2026-09-30  
**Authority**: local

## Requirements

### AU.audio

- **DCS-AU-001** (MUST) — WAV header has RIFF/WAVE/fmt/data chunks
  - hats: `AU`
  - test: `dcs.hats.au.test`

### AUT.automation

- **DCS-AUT-001** (MUST) — generated scripts always carry set -euo pipefail
  - hats: `AUT`
  - test: `dcs.hats.aut.test`

### BE.backend

- **DCS-BE-001** (MUST) — backend returns typed envelope
  - hats: `BE`
  - test: `dcs.hats.be.test`

### CAD.cad

- **DCS-CAD-001** (MUST) — box volume is w*h*d
  - hats: `CAD`
  - test: `dcs.hats.cad.test`

### CL.cloud

- **DCS-CL-001** (MUST) — store does put/get/list with prefixes
  - hats: `CL`
  - test: `dcs.hats.cl.test`

### CMP.compiler

- **DCS-CMP-001** (MUST) — expression compiler handles precedence
  - hats: `CMP`
  - test: `dcs.hats.cmp.test`

### CMP2.compliance

- **DCS-CMP2-001** (MUST) — compliance can reflect on its own standard
  - hats: `CMP2`
  - test: `dcs.hats.cmp2.test`

### CRY.crypto

- **DCS-CRY-001** (MUST) — HMAC verifies and rejects tampered tags
  - hats: `CRY`
  - test: `dcs.hats.cry.test`

### DA.devrel

- **DCS-DA-001** (MUST) — documented examples are syntactically valid
  - hats: `DA`
  - test: `dcs.hats.da.test`

### DB.database

- **DCS-DB-001** (MUST) — insert + select round-trips
  - hats: `DB`
  - test: `dcs.hats.db.test`

### DBA.dba

- **DCS-DBA-001** (MUST) — lookup on digest uses the index
  - hats: `DBA`
  - test: `dcs.hats.dba.test`

### DE.dataeng

- **DCS-DE-001** (MUST) — DAG executes in dependency order
  - hats: `DE`
  - test: `dcs.hats.de.test`

### DIS.distributed

- **DCS-DIS-001** (MUST) — gossip converges to full membership
  - hats: `DIS`
  - test: `dcs.hats.dis.test`

### DO.devops

- **DCS-DO-001** (MUST) — deploy plan topo-sorts services
  - hats: `DO`
  - test: `dcs.hats.do.test`

### DS.datascience

- **DCS-DS-001** (MUST) — CI brackets the sample mean
  - hats: `DS`
  - test: `dcs.hats.ds.test`

### EMB.embedded

- **DCS-EMB-001** (MUST) — hot-path function fits a 64-byte budget
  - hats: `EMB`
  - test: `dcs.hats.emb.test`

### EQ.meta

- **EQ-AUT-002** (MUST) — script exits on error
  - hats: `AUT`
  - test: `dcs.equilibrium.meta.aut_exit`
- **EQ-AUT-003** (MUST) — job scheduler rejects invalid cron
  - hats: `AUT`
  - test: `dcs.equilibrium.meta.aut_cron`
- **EQ-CMP-002** (MUST) — constant folding is idempotent
  - hats: `CMP`
  - test: `dcs.equilibrium.meta.cmp_fold`
- **EQ-CMP-003** (SHOULD) — dead code elimination preserves semantics
  - hats: `CMP`
  - test: `dcs.equilibrium.meta.cmp_dce`
- **EQ-CMP-004** (SHOULD) — SSA form: each name assigned once
  - hats: `CMP`
  - test: `dcs.equilibrium.meta.cmp_ssa`
- **EQ-DIS-002** (MUST) — eventual consistency converges
  - hats: `DIS`
  - test: `dcs.equilibrium.meta.dis_converge`
- **EQ-DIS-003** (MUST) — consensus requires quorum
  - hats: `DIS`
  - test: `dcs.equilibrium.meta.dis_quorum`
- **EQ-DIS-004** (MUST) — vector clock orders causality
  - hats: `DIS`
  - test: `dcs.equilibrium.meta.dis_vclock`
- **EQ-FM-002** (MUST) — forall over finite domain is decidable
  - hats: `FM`
  - test: `dcs.equilibrium.meta.fm_finite`
- **EQ-FM-003** (MUST) — induction base + step
  - hats: `FM`
  - test: `dcs.equilibrium.meta.fm_induction`
- **EQ-MLE-002** (MUST) — cross-validation splits do not overlap
  - hats: `MLE`
  - test: `dcs.equilibrium.meta.mle_cv`
- **EQ-MLE-003** (MUST) — model digest is stable across loads
  - hats: `MLE`
  - test: `dcs.equilibrium.meta.mle_digest`
- **EQ-MLE-004** (MUST) — batch dimension is preserved
  - hats: `MLE`
  - test: `dcs.equilibrium.meta.mle_batch`
- **EQ-PL-002** (MUST) — operator precedence is unambiguous
  - hats: `PL`
  - test: `dcs.equilibrium.meta.pl_prec`
- **EQ-PL-003** (MUST) — left-associative subtraction
  - hats: `PL`
  - test: `dcs.equilibrium.meta.pl_left`
- **EQ-QT-002** (SHOULD) — Black-Scholes formula sanity
  - hats: `QT`
  - test: `dcs.equilibrium.meta.qt_bs`
- **EQ-QT-003** (MUST) — VaR is monotone in confidence
  - hats: `QT`
  - test: `dcs.equilibrium.meta.qt_var`
- **EQ-REL-002** (MUST) — changelog entries carry a version
  - hats: `REL`
  - test: `dcs.equilibrium.meta.rel_changelog`
- **EQ-REL-003** (MUST) — git tag matches version
  - hats: `REL`
  - test: `dcs.equilibrium.meta.rel_tag`
- **EQ-REL-004** (SHOULD) — prerelease ordering
  - hats: `REL`
  - test: `dcs.equilibrium.meta.rel_prerelease`
- **EQ-RES-002** (MUST) — replication increases confidence
  - hats: `RES`
  - test: `dcs.equilibrium.meta.res_replication`
- **EQ-RES-003** (MUST) — p-value bounded
  - hats: `RES`
  - test: `dcs.equilibrium.meta.res_pval`
- **EQ-ROB-002** (MUST) — DH parameters bounded
  - hats: `ROB`
  - test: `dcs.equilibrium.meta.rob_dh`
- **EQ-ROB-003** (SHOULD) — inverse kinematics within reach
  - hats: `ROB`
  - test: `dcs.equilibrium.meta.rob_ik`
- **EQ-SA-002** (MUST) — layered architecture: no upward edges
  - hats: `SA`
  - test: `dcs.equilibrium.meta.sa_layers`
- **EQ-SA-003** (MUST) — no cycles in component graph
  - hats: `SA`
  - test: `dcs.equilibrium.meta.sa_acyclic`
- **EQ-SIM-002** (SHOULD) — physics step is symplectic
  - hats: `SIM`
  - test: `dcs.equilibrium.meta.sim_symplectic`
- **EQ-SIM-003** (MUST) — RNG reproducibility
  - hats: `SIM`
  - test: `dcs.equilibrium.meta.sim_rng`
- **EQ-STE-002** (MUST) — segment append is atomic
  - hats: `STE`
  - test: `dcs.equilibrium.meta.ste_atomic`
- **EQ-STE-003** (MUST) — compaction preserves logical view
  - hats: `STE`
  - test: `dcs.equilibrium.meta.ste_compact`

### EQ.security

- **EQ-CMP2-002** (MUST) — every requirement has a stable id
  - hats: `CMP2`
  - test: `dcs.equilibrium.security.cmp2_ids`
- **EQ-CMP2-003** (MUST) — evidence is content-addressed
  - hats: `CMP2`
  - test: `dcs.equilibrium.security.cmp2_digest`
- **EQ-CRY-002** (MUST) — AES-GCM tag is 16 bytes
  - hats: `CRY`
  - test: `dcs.equilibrium.security.cry_tag_len`
- **EQ-CRY-003** (MUST) — nonce is unique per message
  - hats: `CRY`
  - test: `dcs.equilibrium.security.cry_nonce`
- **EQ-CRY-004** (MUST) — KDF output is deterministic per salt
  - hats: `CRY`
  - test: `dcs.equilibrium.security.cry_kdf`
- **EQ-NET-002** (MUST) — packet length matches header
  - hats: `NET`
  - test: `dcs.equilibrium.security.net_length`
- **EQ-NET-003** (MUST) — checksum is verified
  - hats: `NET`
  - test: `dcs.equilibrium.security.net_checksum`
- **EQ-NWE-002** (MUST) — ACL deny beats allow
  - hats: `NWE`
  - test: `dcs.equilibrium.security.nwe_acl`
- **EQ-NWE-003** (MUST) — rate limit is finite
  - hats: `NWE`
  - test: `dcs.equilibrium.security.nwe_limit`
- **EQ-QA-002** (MUST) — assertion reports the actual value
  - hats: `QA`
  - test: `dcs.equilibrium.security.qa_msg`
- **EQ-QA-003** (MUST) — expected exceptions are asserted
  - hats: `QA`
  - test: `dcs.equilibrium.security.qa_raises`
- **EQ-RE-002** (SHOULD) — objdump-style string extraction finds markers
  - hats: `RE`
  - test: `dcs.equilibrium.security.re_strings`
- **EQ-RE-003** (MUST) — hexdump uses fixed width
  - hats: `RE`
  - test: `dcs.equilibrium.security.re_hexdump`
- **EQ-SD-002** (MUST) — SQL injection escaped
  - hats: `SD`
  - test: `dcs.equilibrium.security.sd_sqli`
- **EQ-SD-003** (MUST) — path traversal blocked
  - hats: `SD`
  - test: `dcs.equilibrium.security.sd_traversal`
- **EQ-SD-004** (MUST) — output is HTML-escaped
  - hats: `SD`
  - test: `dcs.equilibrium.security.sd_escape`
- **EQ-SO-002** (MUST) — fuzzer crashes only on ValueError
  - hats: `SO`
  - test: `dcs.equilibrium.security.so_fuzz`
- **EQ-SO-003** (MUST) — port scan respects timeout
  - hats: `SO`
  - test: `dcs.equilibrium.security.so_timeout`
- **EQ-SRE-002** (MUST) — SLO availability is between 0 and 1
  - hats: `SRE`
  - test: `dcs.equilibrium.security.sre_slo`
- **EQ-SRE-003** (MUST) — burn rate computed from budget
  - hats: `SRE`
  - test: `dcs.equilibrium.security.sre_burn`

### EQ.systems

- **EQ-BE-002** (MUST) — request envelope carries a trace id
  - hats: `BE`
  - test: `dcs.equilibrium.systems.be_trace`
- **EQ-BE-003** (MUST) — errors map to 4xx or 5xx
  - hats: `BE`
  - test: `dcs.equilibrium.systems.be_err_status`
- **EQ-BE-004** (MUST) — pagination has a bounded limit
  - hats: `BE`
  - test: `dcs.equilibrium.systems.be_page_limit`
- **EQ-BE-005** (MUST) — content negotiation picks JSON
  - hats: `BE`
  - test: `dcs.equilibrium.systems.be_negotiate`
- **EQ-BE-006** (MUST) — idempotency key required for POST-create
  - hats: `BE`
  - test: `dcs.equilibrium.systems.be_idem`
- **EQ-BE-007** (MUST) — response body is valid UTF-8
  - hats: `BE`
  - test: `dcs.equilibrium.systems.be_utf8`
- **EQ-CL-002** (MUST) — cloud region is well-formed
  - hats: `CL`
  - test: `dcs.equilibrium.systems.cl_region`
- **EQ-CL-003** (MUST) — bucket names are lowercase
  - hats: `CL`
  - test: `dcs.equilibrium.systems.cl_bucket`
- **EQ-CL-004** (MUST) — IAM action is scoped
  - hats: `CL`
  - test: `dcs.equilibrium.systems.cl_iam`
- **EQ-DB-002** (MUST) — transaction rolls back on error
  - hats: `DB`
  - test: `dcs.equilibrium.systems.db_rollback`
- **EQ-DB-003** (MUST) — UNIQUE constraint enforced
  - hats: `DB`
  - test: `dcs.equilibrium.systems.db_unique`
- **EQ-DB-004** (MUST) — foreign key cascades
  - hats: `DB`
  - test: `dcs.equilibrium.systems.db_fk`
- **EQ-DBA-002** (MUST) — index covers the query projection
  - hats: `DBA`
  - test: `dcs.equilibrium.systems.dba_covering`
- **EQ-DBA-003** (SHOULD) — ANALYZE populates sqlite_stat1
  - hats: `DBA`
  - test: `dcs.equilibrium.systems.dba_analyze`
- **EQ-DE-002** (MUST) — pipeline emits a manifest
  - hats: `DE`
  - test: `dcs.equilibrium.systems.de_manifest`
- **EQ-DE-003** (MUST) — DAG detects cycles
  - hats: `DE`
  - test: `dcs.equilibrium.systems.de_cycle`
- **EQ-DE-004** (MUST) — backfill mode re-runs only failed partitions
  - hats: `DE`
  - test: `dcs.equilibrium.systems.de_backfill`
- **EQ-DO-002** (MUST) — deploy plan has rollback
  - hats: `DO`
  - test: `dcs.equilibrium.systems.do_rollback`
- **EQ-DO-003** (MUST) — deployment is versioned
  - hats: `DO`
  - test: `dcs.equilibrium.systems.do_versioned`
- **EQ-DS-002** (MUST) — median is order-invariant
  - hats: `DS`
  - test: `dcs.equilibrium.systems.ds_median`
- **EQ-DS-003** (MUST) — std of constant series is zero
  - hats: `DS`
  - test: `dcs.equilibrium.systems.ds_std`
- **EQ-DS-004** (MUST) — correlation is in [-1, 1]
  - hats: `DS`
  - test: `dcs.equilibrium.systems.ds_corr`
- **EQ-EMB-002** (MUST) — bit width is a power of two
  - hats: `EMB`
  - test: `dcs.equilibrium.systems.emb_bitwidth`
- **EQ-EMB-003** (MUST) — flash write is word-aligned
  - hats: `EMB`
  - test: `dcs.equilibrium.systems.emb_aligned`
- **EQ-FW-002** (MUST) — frame header length prefix is correct
  - hats: `FW`
  - test: `dcs.equilibrium.systems.fw_prefix`
- **EQ-FW-003** (MUST) — CRC matches on round-trip
  - hats: `FW`
  - test: `dcs.equilibrium.systems.fw_crc`
- **EQ-HPC-002** (MUST) — thread pool bound respected
  - hats: `HPC`
  - test: `dcs.equilibrium.systems.hpc_pool`
- **EQ-HPC-003** (MUST) — chunked iteration preserves order
  - hats: `HPC`
  - test: `dcs.equilibrium.systems.hpc_chunks`
- **EQ-HW-002** (MUST) — memory size is a power of two GiB
  - hats: `HW`
  - test: `dcs.equilibrium.systems.hw_mem`
- **EQ-HW-003** (MAY) — core count matches a known Apple Silicon config
  - hats: `HW`
  - test: `dcs.equilibrium.systems.hw_cores`
- **EQ-KRN-002** (SHOULD) — SIGINT handler is installed
  - hats: `KRN`
  - test: `dcs.equilibrium.systems.krn_sigint`
- **EQ-KRN-003** (MAY) — umask is set (non-default)
  - hats: `KRN`
  - test: `dcs.equilibrium.systems.krn_umask`
- **EQ-PLT-002** (MUST) — platform-specific path resolution
  - hats: `PLT`
  - test: `dcs.equilibrium.systems.plt_paths`
- **EQ-PLT-003** (MUST) — sys.executable is non-empty
  - hats: `PLT`
  - test: `dcs.equilibrium.systems.plt_exec`
- **EQ-SYS-002** (MUST) — subprocess exit code propagated
  - hats: `SYS`
  - test: `dcs.equilibrium.systems.sys_exitcode`
- **EQ-SYS-003** (MAY) — signal.raise_signal delivers
  - hats: `SYS`
  - test: `dcs.equilibrium.systems.sys_raise`

### EQ.ui

- **EQ-AU-002** (MUST) — sample rate is standard
  - hats: `AU`
  - test: `dcs.equilibrium.ui.au_rate`
- **EQ-AU-003** (MUST) — PCM amplitude in [-1, 1]
  - hats: `AU`
  - test: `dcs.equilibrium.ui.au_pcm`
- **EQ-AU-004** (MUST) — channel count is 1 or 2
  - hats: `AU`
  - test: `dcs.equilibrium.ui.au_channels`
- **EQ-CAD-002** (MUST) — all box dimensions positive
  - hats: `CAD`
  - test: `dcs.equilibrium.ui.cad_dims`
- **EQ-CAD-003** (MUST) — mesh vertex/face ratio is Euler-consistent
  - hats: `CAD`
  - test: `dcs.equilibrium.ui.cad_euler`
- **EQ-DA-002** (MUST) — example shows expected output
  - hats: `DA`
  - test: `dcs.equilibrium.ui.da_output`
- **EQ-DA-003** (MUST) — quickstart fits a single code block
  - hats: `DA`
  - test: `dcs.equilibrium.ui.da_quickstart`
- **EQ-FE-002** (MUST) — HTML id attributes are unique
  - hats: `FE`
  - test: `dcs.equilibrium.ui.fe_ids_unique`
- **EQ-FE-003** (MUST) — CSS selectors are balanced
  - hats: `FE`
  - test: `dcs.equilibrium.ui.fe_css_balanced`
- **EQ-FE-004** (MUST) — hyperlink target is valid
  - hats: `FE`
  - test: `dcs.equilibrium.ui.fe_link_target`
- **EQ-FE-005** (MUST) — aria-label present on icon buttons
  - hats: `FE`
  - test: `dcs.equilibrium.ui.fe_aria`
- **EQ-FS-002** (MUST) — hydration payload is valid JSON
  - hats: `FS`
  - test: `dcs.equilibrium.ui.fs_hydration`
- **EQ-FS-003** (MUST) — SSR and CSR render the same shell
  - hats: `FS`
  - test: `dcs.equilibrium.ui.fs_ssr`
- **EQ-GAME-002** (MUST) — turn order alternates
  - hats: `GAME`
  - test: `dcs.equilibrium.ui.game_turns`
- **EQ-GAME-003** (MUST) — move inside board bounds
  - hats: `GAME`
  - test: `dcs.equilibrium.ui.game_bounds`
- **EQ-GAME-004** (MUST) — terminal states are absorbing
  - hats: `GAME`
  - test: `dcs.equilibrium.ui.game_terminal`
- **EQ-GFX-002** (MUST) — SVG viewBox declared
  - hats: `GFX`
  - test: `dcs.equilibrium.ui.gfx_viewbox`
- **EQ-GFX-003** (MUST) — polygon closes with Z
  - hats: `GFX`
  - test: `dcs.equilibrium.ui.gfx_polygon`
- **EQ-GFX-004** (MUST) — gradient stops in [0,1]
  - hats: `GFX`
  - test: `dcs.equilibrium.ui.gfx_gradient`
- **EQ-MO-002** (MUST) — viewport meta is present
  - hats: `MO`
  - test: `dcs.equilibrium.ui.mo_viewport`
- **EQ-MO-003** (MUST) — manifest icons include 512px
  - hats: `MO`
  - test: `dcs.equilibrium.ui.mo_icon_sizes`
- **EQ-MO-004** (SHOULD) — offline service worker caches shell
  - hats: `MO`
  - test: `dcs.equilibrium.ui.mo_sw`
- **EQ-SHD-002** (MUST) — vertex shader declares gl_Position
  - hats: `SHD`
  - test: `dcs.equilibrium.ui.shd_vertex`
- **EQ-SHD-003** (MUST) — uniform declared before use
  - hats: `SHD`
  - test: `dcs.equilibrium.ui.shd_uniform`
- **EQ-TW-002** (MUST) — heading levels do not skip
  - hats: `TW`
  - test: `dcs.equilibrium.ui.tw_headings`
- **EQ-TW-003** (MUST) — code blocks declare a language
  - hats: `TW`
  - test: `dcs.equilibrium.ui.tw_code_lang`
- **EQ-TW-004** (SHOULD) — links use absolute or https
  - hats: `TW`
  - test: `dcs.equilibrium.ui.tw_links`
- **EQ-VID-002** (MUST) — frame timestamps are monotonic
  - hats: `VID`
  - test: `dcs.equilibrium.ui.vid_monotonic`
- **EQ-VID-003** (MUST) — codec string parses
  - hats: `VID`
  - test: `dcs.equilibrium.ui.vid_codec`

### FE.frontend

- **DCS-FE-001** (MUST) — index is well-formed and exposes an htmx contract
  - hats: `FE`
  - test: `dcs.hats.fe.test`

### FM.formal

- **DCS-FM-001** (MUST) — De Morgan holds exhaustively
  - hats: `FM`
  - test: `dcs.hats.fmtl.test`

### FS.fullstack

- **DCS-FS-001** (MUST) — FE + BE compose into one page
  - hats: `FS`
  - test: `dcs.hats.fs.test`

### FW.firmware

- **DCS-FW-001** (MUST) — frame/unframe round-trips
  - hats: `FW`
  - test: `dcs.hats.fw.test`

### GAME.game

- **DCS-GAME-001** (MUST) — minimax never loses from an empty board
  - hats: `GAME`
  - test: `dcs.hats.game.test`

### GFX.graphics

- **DCS-GFX-001** (MUST) — SVG has one rect per data point
  - hats: `GFX`
  - test: `dcs.hats.gfx.test`

### HPC.hpc

- **DCS-HPC-001** (MUST) — parallel map preserves order
  - hats: `HPC`
  - test: `dcs.hats.hpc.test`

### HW.hardware

- **DCS-HW-001** (MUST) — hardware fit honors core and memory ceilings
  - hats: `HW`
  - test: `dcs.hats.hw.test`

### KRN.kernel

- **DCS-KRN-001** (MUST) — process has non-zero soft nofile limit
  - hats: `KRN`
  - test: `dcs.hats.krn.test`

### MLE.mleng

- **DCS-MLE-001** (MUST) — manifest schema is enforced
  - hats: `MLE`
  - test: `dcs.hats.mle.test`

### MO.mobile

- **DCS-MO-001** (MUST) — PWA manifest is complete
  - hats: `MO`
  - test: `dcs.hats.mo.test`

### NET.networking

- **DCS-NET-001** (MUST) — connect helper survives unreachable target
  - hats: `NET`
  - test: `dcs.hats.net.test`

### NWE.neteng

- **DCS-NWE-001** (MUST) — egress allowlist blocks non-listed targets
  - hats: `NWE`
  - test: `dcs.hats.nwe.test`

### PL.pldesign

- **DCS-PL-001** (MUST) — grammar exposes expr/term/factor
  - hats: `PL`
  - test: `dcs.hats.pl.test`

### PLT.platform

- **DCS-PLT-001** (MUST) — platform classified
  - hats: `PLT`
  - test: `dcs.hats.plt.test`

### QA.qa

- **DCS-QA-001** (MUST) — expectation helper enforces and reports
  - hats: `QA`
  - test: `dcs.hats.qa.test`

### QT.quant

- **DCS-QT-001** (MUST) — MC pi within 0.05 of math.pi
  - hats: `QT`
  - test: `dcs.hats.qt.test`

### RE.reverse

- **DCS-RE-001** (MUST) — opaque blob round-trips
  - hats: `RE`
  - test: `dcs.hats.re.test`

### REL.release

- **DCS-REL-001** (MUST) — semver parses and bumps
  - hats: `REL`
  - test: `dcs.hats.rel.test`

### RES.research

- **DCS-RES-001** (MUST) — improvement gate rejects noise
  - hats: `RES`
  - test: `dcs.hats.res.test`

### ROB.robotics

- **DCS-ROB-001** (MUST) — FK reaches the expected folded pose
  - hats: `ROB`
  - test: `dcs.hats.rob.test`

### SA.solutionsarch

- **DCS-SA-001** (MUST) — arch graph is acyclic
  - hats: `SA`
  - test: `dcs.hats.sa.test`

### SCI.scientific

- **DCS-SCI-001** (MUST) — Kahan error below 1e-6 for 10k floats
  - hats: `SCI`
  - test: `dcs.hats.sci.test`

### SD.defensive

- **DCS-SD-001** (MUST) — allowlist rejects path traversal
  - hats: `SD`
  - test: `dcs.hats.sd.test`

### SHD.shader

- **DCS-SHD-001** (MUST) — fragment shader is structurally sound
  - hats: `SHD`
  - test: `dcs.hats.shd.test`

### SIM.simulation

- **DCS-SIM-001** (MUST) — stepper produces n+1 states
  - hats: `SIM`
  - test: `dcs.hats.sim.test`

### SO.offensive

- **DCS-SO-001** (MUST) — fuzz harness raises only ValueError
  - hats: `SO`
  - test: `dcs.hats.so.test`

### SRE.sre

- **DCS-SRE-001** (MUST) — error budget enforced
  - hats: `SRE`
  - test: `dcs.hats.sre.test`

### STE.storage

- **DCS-STE-001** (MUST) — segment appends are indexed and readable
  - hats: `STE`
  - test: `dcs.hats.ste.test`

### SYS.systems

- **DCS-SYS-001** (MUST) — open fd count is bounded
  - hats: `SYS`
  - test: `dcs.hats.sys.test`

### TW.techwriter

- **DCS-TW-001** (MUST) — TOC anchors are kebab-cased
  - hats: `TW`
  - test: `dcs.hats.tw.test`

### VID.video

- **DCS-VID-001** (MUST) — 2s @ 30fps → 60 frames
  - hats: `VID`
  - test: `dcs.hats.vid.test`

### X.a11y

- **DCS-XC-A11Y-001** (MUST) — black-on-white clears WCAG AA 4.5:1
  - hats: `FE, GFX, QA`
  - test: `dcs.crosscut.a11y.test`

### X.backup

- **DCS-XC-BACKUP-001** (MUST) — snapshot/restore is integrity-checked
  - hats: `STE, SRE, SD`
  - test: `dcs.crosscut.backup.test`

### X.cdc

- **DCS-XC-CDC-001** (MUST) — version stamps are monotonic
  - hats: `DE, DB, STE`
  - test: `dcs.crosscut.cdc.test`

### X.chaos

- **DCS-XC-CHAOS-001** (MUST) — chaos injects exactly the configured fraction
  - hats: `SRE, QA, SO`
  - test: `dcs.crosscut.chaos.test`

### X.circuit

- **DCS-XC-CIRCUIT-001** (MUST) — breaker opens after threshold
  - hats: `SRE, DIS, NET`
  - test: `dcs.crosscut.circuit.test`

### X.clock

- **DCS-XC-CLOCK-001** (MUST) — injectable clock is monotonic
  - hats: `SYS, SIM`
  - test: `dcs.crosscut.clock.test`

### X.concurrency

- **DCS-XC-CONC-001** (MUST) — single-flight dedupes concurrent calls
  - hats: `SYS, DIS`
  - test: `dcs.crosscut.concurrency.test`

### X.deploy

- **DCS-XC-DEPLOY-001** (MUST) — canary rolls back when over budget
  - hats: `DO, SRE, REL`
  - test: `dcs.crosscut.deploy.test`

### X.flags

- **DCS-XC-FLAG-001** (MUST) — rollout is deterministic and stable
  - hats: `REL, DO`
  - test: `dcs.crosscut.flag.test`

### X.i18n

- **DCS-XC-I18N-001** (MUST) — message catalog falls back to English
  - hats: `FE, TW, DA`
  - test: `dcs.crosscut.i18n.test`

### X.observability

- **DCS-XC-OBS-001** (MUST) — metrics enforce cardinality ceiling
  - hats: `SRE, SYS`
  - test: `dcs.crosscut.observability.test`

### X.privacy

- **DCS-XC-PRIV-001** (MUST) — redactor strips email/phone/SSN
  - hats: `SD, CMP2, BE`
  - test: `dcs.crosscut.privacy.test`

### X.ratelimit

- **DCS-XC-RATE-001** (MUST) — token bucket enforces burst then rate
  - hats: `NET, NWE, SRE`
  - test: `dcs.crosscut.ratelimit.test`

### X.saga

- **DCS-XC-SAGA-001** (MUST) — saga compensates in reverse order
  - hats: `DIS, DE`
  - test: `dcs.crosscut.saga.test`

### X.semver

- **DCS-XC-SEMVER-001** (MUST) — caret/tilde/exact match correctly
  - hats: `REL, PL`
  - test: `dcs.crosscut.semver.test`

### X.time

- **DCS-XC-TIME-001** (MUST) — elapsed monotonic time is non-negative
  - hats: `SYS, SIM`
  - test: `dcs.crosscut.time.test`

### coalescence

- **DCS-CO-001** (MUST) — every coalescible kind is registered
  - hats: `FM, PL`
  - test: `dcs.tests.equivalence.every_coalesce_registered`
- **DCS-CO-002** (MUST) — mesh coalescence is commutative + idempotent
  - hats: `DIS, FM`
  - test: `dcs.tests.equivalence.mesh_coalescence_laws`
- **DCS-CO-003** (MUST) — run coalescence refuses disagreement
  - hats: `FM, SRE`
  - test: `dcs.tests.equivalence.run_merge_rejects`
- **DCS-CO-004** (MUST) — requirement coalescence takes stricter criticality
  - hats: `CMP2, FM`
  - test: `dcs.tests.equivalence.requirement_stricter`
- **DCS-CO-005** (MUST) — bundle coalescence is pessimistic on conflict
  - hats: `CMP2, SD`
  - test: `dcs.tests.equivalence.bundle_pessimistic`

### coherence

- **DCS-COH-001** (MUST) — standard and evidence agree on requirement ids
  - hats: `CMP2, FM`
  - test: `dcs.tests.conformance.coherence_standard_evidence`
- **DCS-COH-002** (MUST) — equivalence and coalescence registries align
  - hats: `FM, PL`
  - test: `dcs.tests.conformance.coherence_registries`
- **DCS-COH-003** (MUST) — team roster partitions the hat set
  - hats: `SA, PL`
  - test: `dcs.tests.conformance.coherence_roster`

### conformance

- **DCS-CONF-001** (MUST) — standard declaration matches evidence actuals
  - hats: `CMP2, QA`
  - test: `dcs.tests.conformance.declared_matches_actual`
- **DCS-CONF-002** (MUST) — conformance verdict is CONFORMANT
  - hats: `CMP2, QA, SRE`
  - test: `dcs.tests.conformance.verdict_is_conformant`

### coordination

- **DCS-CRD-001** (MUST) — quorum requires strict majority
  - hats: `DIS, SRE`
  - test: `dcs.tests.conformance.quorum_strict`
- **DCS-CRD-002** (MUST) — epoch is strictly monotonic
  - hats: `DIS, SIM`
  - test: `dcs.tests.conformance.epoch_monotonic`
- **DCS-CRD-003** (MUST) — reconcile is commutative
  - hats: `DIS, FM`
  - test: `dcs.tests.conformance.reconcile_commutative`
- **DCS-CRD-004** (MUST) — reconcile is associative
  - hats: `DIS, FM`
  - test: `dcs.tests.conformance.reconcile_associative`
- **DCS-CRD-005** (MUST) — reconcile is idempotent
  - hats: `DIS, FM`
  - test: `dcs.tests.conformance.reconcile_idempotent`

### equivalence

- **DCS-EQ-001** (MUST) — every artifact kind has an equivalence relation
  - hats: `FM, PL`
  - test: `dcs.tests.equivalence.every_kind_registered`
- **DCS-EQ-002** (MUST) — exact implies semantic for every kind
  - hats: `FM, SCI`
  - test: `dcs.tests.equivalence.exact_implies_semantic`
- **DCS-EQ-003** (MUST) — equivalence is reflexive, symmetric
  - hats: `FM`
  - test: `dcs.tests.equivalence.equivalence_is_relation`

### mesh

- **DCS-MESH-001** (MUST) — MeshOfMeshes.add_run accepts a bare Run
  - hats: `DIS, SYS`
  - test: `dcs.tests.mesh.mesh_add_run`
- **DCS-MESH-002** (MUST) — weave accepts a list
  - hats: `DE`
  - test: `dcs.tests.mesh.weave_accepts_list`
- **DCS-MESH-003** (MUST) — mesh exports the five public names
  - hats: `PL, BE`
  - test: `dcs.tests.mesh.mesh_exports`

### nature.adaptation

- **DCS-NAT-ADP-001** (MUST) — habituation decays monotonically
  - hats: `SCI, MLE`
  - test: `dcs.nature.adaptation.test_habituation`
- **DCS-NAT-ADP-002** (MUST) — sensitization grows monotonically
  - hats: `SCI`
  - test: `dcs.nature.adaptation.test_sensitization`
- **DCS-NAT-ADP-003** (MUST) — hebbian weight increases with co-firing
  - hats: `MLE, RES`
  - test: `dcs.nature.adaptation.test_hebbian`
- **DCS-NAT-ADP-004** (MUST) — STDP is asymmetric around dt=0
  - hats: `MLE, SCI`
  - test: `dcs.nature.adaptation.test_stdp`
- **DCS-NAT-ADP-005** (MUST) — homeostasis drives to setpoint
  - hats: `SRE, SCI`
  - test: `dcs.nature.adaptation.test_homeostasis`
- **DCS-NAT-ADP-006** (MUST) — allostasis tracks predictive signal
  - hats: `SRE, MLE`
  - test: `dcs.nature.adaptation.test_allostasis`
- **DCS-NAT-ADP-007** (SHOULD) — clonal selection improves affinity
  - hats: `SCI, SO`
  - test: `dcs.nature.adaptation.test_immune`
- **DCS-NAT-ADP-008** (SHOULD) — chemotaxis climbs a gradient
  - hats: `SCI, ROB`
  - test: `dcs.nature.adaptation.test_chemotaxis`

### nature.consensus

- **DCS-NAT-CON-001** (MUST) — hive average equals arithmetic mean
  - hats: `DIS, SCI`
  - test: `dcs.nature.consensus.test_bee_average`
- **DCS-NAT-CON-002** (MUST) — quorum commits above threshold
  - hats: `DIS, AUT`
  - test: `dcs.nature.consensus.test_quorum`

### nature.flocking

- **DCS-NAT-FLK-001** (SHOULD) — boids reaches non-zero polarisation
  - hats: `GFX, SCI, SIM`
  - test: `dcs.nature.flocking.test_boids_polarised`
- **DCS-NAT-FLK-002** (MUST) — murmuration uses exactly k-nearest
  - hats: `SCI, SIM`
  - test: `dcs.nature.flocking.test_murmuration_k`
- **DCS-NAT-FLK-003** (SHOULD) — polarisation peaks near critical density
  - hats: `SCI, RES`
  - test: `dcs.nature.flocking.test_critical_peak`
- **DCS-NAT-FLK-004** (SHOULD) — fish school stays in positive quadrant edges
  - hats: `SCI, SIM`
  - test: `dcs.nature.flocking.test_fish_edge`
- **DCS-NAT-FLK-005** (SHOULD) — locust swarm aligns in x
  - hats: `SCI, SIM`
  - test: `dcs.nature.flocking.test_locust_align`

### nature.flow

- **DCS-NAT-FLOW-001** (MUST) — Fick flux scales with concentration gradient
  - hats: `SCI, HPC`
  - test: `dcs.nature.flow.test_fick`
- **DCS-NAT-FLOW-002** (MUST) — Darcy flow scales with pressure gradient
  - hats: `SCI`
  - test: `dcs.nature.flow.test_darcy`
- **DCS-NAT-FLOW-003** (MUST) — Poiseuille flow ∝ r⁴
  - hats: `SCI, HPC`
  - test: `dcs.nature.flow.test_poiseuille`
- **DCS-NAT-FLOW-004** (MUST) — Kirchhoff: in = out
  - hats: `NET, SYS`
  - test: `dcs.nature.flow.test_kirchhoff`
- **DCS-NAT-FLOW-005** (MUST) — Fourier heat flux with negative gradient
  - hats: `SCI`
  - test: `dcs.nature.flow.test_fourier`
- **DCS-NAT-FLOW-006** (MUST) — Nernst potential for K+ is negative inside
  - hats: `SCI, RES`
  - test: `dcs.nature.flow.test_nernst`
- **DCS-NAT-FLOW-007** (MUST) — chemostat reaches steady state
  - hats: `SCI, DB`
  - test: `dcs.nature.flow.test_chemostat`
- **DCS-NAT-FLOW-008** (MUST) — osmosis driven by concentration difference
  - hats: `SCI, EMB`
  - test: `dcs.nature.flow.test_osmosis`
- **DCS-NAT-FLOW-009** (MUST) — diffusion-limited flux scales with 1/δ
  - hats: `SCI`
  - test: `dcs.nature.flow.test_diffusion_limited`

### nature.foraging

- **DCS-NAT-FRG-001** (SHOULD) — levy flight revisits fewer cells than brownian at equal steps
  - hats: `SCI, RES, ROB`
  - test: `dcs.nature.foraging.test_levy_more_efficient`
- **DCS-NAT-FRG-002** (MUST) — brownian search is diffusive (rms ~ sqrt(n))
  - hats: `SCI`
  - test: `dcs.nature.foraging.test_brownian_diffusive`
- **DCS-NAT-FRG-003** (MUST) — area-restricted stays bounded near origin
  - hats: `SCI, SIM`
  - test: `dcs.nature.foraging.test_ar_bounded`
- **DCS-NAT-FRG-004** (SHOULD) — albatross drifts toward gradient target
  - hats: `SCI, RES`
  - test: `dcs.nature.foraging.test_albatross_gradient`

### nature.morpho

- **DCS-NAT-MOR-001** (MUST) — Turing pattern forms non-uniform b
  - hats: `SCI, SIM, GFX`
  - test: `dcs.nature.morpho.test_turing`
- **DCS-NAT-MOR-002** (MUST) — Gray-Scott v is spatially non-uniform
  - hats: `SCI, SIM`
  - test: `dcs.nature.morpho.test_gs`
- **DCS-NAT-MOR-003** (SHOULD) — BZ reaction sustains a spatial pattern
  - hats: `SCI`
  - test: `dcs.nature.morpho.test_bz`
- **DCS-NAT-MOR-004** (SHOULD) — DLA produces a branching fractal cluster
  - hats: `SCI, GFX`
  - test: `dcs.nature.morpho.test_dla`
- **DCS-NAT-MOR-005** (SHOULD) — Eden growth is compact (low perimeter/area)
  - hats: `SCI`
  - test: `dcs.nature.morpho.test_eden_compact`
- **DCS-NAT-MOR-006** (MUST) — lichen edge grows outward
  - hats: `SCI, SIM`
  - test: `dcs.nature.morpho.test_lichen`
- **DCS-NAT-MOR-007** (MAY) — tree branches double per level
  - hats: `GFX, SCI`
  - test: `dcs.nature.morpho.test_tree`

### nature.oscillator

- **DCS-NAT-OSC-001** (MUST) — kuramoto synchronises above K_c
  - hats: `SCI, HPC`
  - test: `dcs.nature.oscillator.test_kuramoto_sync`
- **DCS-NAT-OSC-002** (SHOULD) — firefly pulse-coupling converges to phase lock
  - hats: `SCI, SIM`
  - test: `dcs.nature.oscillator.test_firefly_lock`
- **DCS-NAT-OSC-003** (MAY) — cricket chorus matches firefly coupling
  - hats: `SCI`
  - test: `dcs.nature.oscillator.test_cricket`
- **DCS-NAT-OSC-004** (MUST) — cardiac SA node exhibits relaxation spikes
  - hats: `SCI, SIM`
  - test: `dcs.nature.oscillator.test_cardiac`
- **DCS-NAT-OSC-005** (MUST) — circadian clock oscillates via delayed feedback
  - hats: `SCI, SIM`
  - test: `dcs.nature.oscillator.test_circadian`
- **DCS-NAT-OSC-006** (SHOULD) — Peskin-Mirollo firing synchronises
  - hats: `SCI, HPC`
  - test: `dcs.nature.oscillator.test_peskin`
- **DCS-NAT-OSC-007** (MUST) — FitzHugh-Nagumo produces spikes
  - hats: `SCI`
  - test: `dcs.nature.oscillator.test_fhn`
- **DCS-NAT-OSC-008** (MUST) — Hodgkin-Huxley produces an action potential
  - hats: `SCI, RES`
  - test: `dcs.nature.oscillator.test_hh`

### nature.population

- **DCS-NAT-POP-001** (MUST) — logistic saturates at K
  - hats: `DS, SCI`
  - test: `dcs.nature.population.test_logistic`
- **DCS-NAT-POP-002** (MUST) — gompertz approaches its plateau
  - hats: `DS, SCI`
  - test: `dcs.nature.population.test_gompertz`
- **DCS-NAT-POP-003** (SHOULD) — Allee effect: below threshold → extinction
  - hats: `SCI, DS`
  - test: `dcs.nature.population.test_allee`
- **DCS-NAT-POP-004** (SHOULD) — Lotka-Volterra shows bounded cycles
  - hats: `SCI, QT`
  - test: `dcs.nature.population.test_lv`
- **DCS-NAT-POP-005** (MUST) — SIR conserves total population
  - hats: `DS, SCI`
  - test: `dcs.nature.population.test_sir`
- **DCS-NAT-POP-006** (SHOULD) — SIRS shows waning immunity (R re-enters S)
  - hats: `DS, SCI`
  - test: `dcs.nature.population.test_sirs`
- **DCS-NAT-POP-007** (SHOULD) — host-parasite cycles (Red Queen)
  - hats: `SCI, QT`
  - test: `dcs.nature.population.test_hp`
- **DCS-NAT-POP-008** (SHOULD) — spatial predator-prey forms patterns
  - hats: `SCI, SIM`
  - test: `dcs.nature.population.test_spatial`

### nature.stigmergy

- **DCS-NAT-STG-001** (SHOULD) — ant colony collects food using pheromone trail
  - hats: `DIS, SCI`
  - test: `dcs.nature.stigmergy.test_colony`
- **DCS-NAT-STG-002** (MUST) — termite deposits evaporate over time
  - hats: `SCI, SIM`
  - test: `dcs.nature.stigmergy.test_termite_evap`
- **DCS-NAT-STG-003** (SHOULD) — slime mold prunes weak edges
  - hats: `DIS, SCI`
  - test: `dcs.nature.stigmergy.test_slime_pruning`

### nature.threshold

- **DCS-NAT-THR-001** (MUST) — quorum fires above threshold
  - hats: `SCI, DIS`
  - test: `dcs.nature.threshold.test_quorum`
- **DCS-NAT-THR-002** (MUST) — sigmoid is monotone and bounded
  - hats: `SCI, MLE`
  - test: `dcs.nature.threshold.test_sigmoid`
- **DCS-NAT-THR-003** (MUST) — integrate-and-fire fires on accumulated input
  - hats: `MLE, SCI`
  - test: `dcs.nature.threshold.test_lif`
- **DCS-NAT-THR-004** (SHOULD) — gene toggle is bistable (exactly one high)
  - hats: `SCI, RES`
  - test: `dcs.nature.threshold.test_toggle`
- **DCS-NAT-THR-005** (MUST) — order parameter zero below critical point
  - hats: `SCI, FM`
  - test: `dcs.nature.threshold.test_percolation`

### nature.walk

- **DCS-NAT-WALK-001** (MUST) — correlated walk is ballistic at kappa=1
  - hats: `SCI, SIM`
  - test: `dcs.nature.walk.test_correlated_ballistic`
- **DCS-NAT-WALK-002** (MUST) — elephant walk keeps full history
  - hats: `SCI, RES`
  - test: `dcs.nature.walk.test_elephant_memory`
- **DCS-NAT-WALK-003** (MUST) — self-avoiding walk never revisits
  - hats: `SCI`
  - test: `dcs.nature.walk.test_saw_no_revisit`
- **DCS-NAT-WALK-004** (SHOULD) — persistent walk ends far from origin
  - hats: `SCI`
  - test: `dcs.nature.walk.test_persistent_far`
- **DCS-NAT-WALK-005** (SHOULD) — 2D levy walk has heavy-tail step distribution
  - hats: `SCI, QT`
  - test: `dcs.nature.walk.test_levy_2d_heavy_tail`

### puzzles

- **DCS-PUZ-001** (MUST) — scramble never returns SOLVED
  - hats: `SCI, FM`
  - test: `dcs.tests.puzzles.scramble_safe`
- **DCS-PUZ-002** (MUST) — solve_cube round-trips
  - hats: `SCI, MLE`
  - test: `dcs.tests.puzzles.solve_round_trip`

### train

- **DCS-TRAIN-001** (MUST) — Run carries parent_id
  - hats: `BE, DE, FM`
  - test: `dcs.tests.train.run_has_parent_id`
- **DCS-TRAIN-002** (MUST) — Trainer exposes step + _evolve
  - hats: `BE, MLE, FM`
  - test: `dcs.tests.train.trainer_has_step`
- **DCS-TRAIN-003** (MUST) — trans produces an edge chain
  - hats: `DIS, DE`
  - test: `dcs.tests.train.trans_produces_chain`
- **DCS-TRAIN-004** (MUST) — pollinate emits change deltas
  - hats: `DE, DS`
  - test: `dcs.tests.train.pollinate_reports_change`
- **DCS-TRAIN-005** (MUST) — CLI runs to completion
  - hats: `BE, TW, QA`
  - test: `dcs.tests.train.cli_runs`

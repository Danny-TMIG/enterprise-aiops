# Stdlib Mastery Report

- Interpreter stdlib modules: **202**
- Parsed files: **6601**
- Stdlib modules used in tree: **52**
- Unused: **150**

## Used modules, ranked by import count

| Module | Files | Imports | Aliases | Shadowed? |
|---|---:|---:|---|---|
| `dataclasses` | 4217 | 12466 | — | — |
| `json` | 5659 | 5660 | _json | — |
| `time` | 4136 | 4139 | — | — |
| `hashlib` | 4135 | 4138 | — | — |
| `pathlib` | 1607 | 1609 | — | — |
| `typing` | 274 | 293 | — | — |
| `sys` | 89 | 91 | _s | — |
| `collections` | 78 | 90 | — | — |
| `os` | 53 | 55 | — | — |
| `re` | 41 | 41 | _re | — |
| `datetime` | 18 | 35 | — | — |
| `random` | 29 | 31 | — | — |
| `subprocess` | 28 | 28 | — | — |
| `sqlite3` | 20 | 27 | — | — |
| `ast` | 26 | 27 | _ast | — |
| `importlib` | 20 | 20 | — | — |
| `argparse` | 18 | 18 | — | — |
| `concurrent` | 10 | 14 | cf | — |
| `threading` | 14 | 14 | — | — |
| `hmac` | 10 | 10 | — | — |
| `shutil` | 9 | 9 | — | — |
| `asyncio` | 8 | 8 | — | — |
| `builtins` | 8 | 8 | — | — |
| `itertools` | 7 | 7 | — | — |
| `tempfile` | 6 | 6 | — | — |
| `base64` | 6 | 6 | — | — |
| `uuid` | 6 | 6 | — | — |
| `struct` | 6 | 6 | — | — |
| `socket` | 5 | 5 | — | — |
| `inspect` | 5 | 5 | — | — |
| `enum` | 5 | 5 | — | — |
| `statistics` | 3 | 5 | — | — |
| `signal` | 3 | 4 | — | — |
| `urllib` | 4 | 4 | — | — |
| `html` | 3 | 3 | — | — |
| `functools` | 3 | 3 | — | — |
| `textwrap` | 2 | 2 | — | — |
| `py_compile` | 2 | 2 | — | — |
| `contextlib` | 2 | 2 | — | — |
| `secrets` | 2 | 2 | — | — |
| `types` | 2 | 2 | — | — |
| `platform` | 2 | 2 | — | nested (1) |
| `traceback` | 2 | 2 | — | — |
| `unittest` | 1 | 1 | — | — |
| `warnings` | 1 | 1 | — | — |
| `pkgutil` | 1 | 1 | — | — |
| `logging` | 1 | 1 | — | — |
| `io` | 1 | 1 | — | — |
| `difflib` | 1 | 1 | — | — |
| `tarfile` | 1 | 1 | — | — |
| `multiprocessing` | 1 | 1 | mp | — |
| `string` | 1 | 1 | — | — |

## Detailed usage

### `dataclasses`

- imported in 4217 files
- 12466 import statements

Sample imports:
- `meta_glasses_integration/meta_glasses_integration.py:7` — `from dataclasses import dataclass`
- `meta_glasses_integration/meta_glasses_integration.py:7` — `from dataclasses import field`
- `meta_glasses_integration/meta_glasses_integration.py:7` — `from dataclasses import asdict`
- `migrations/migrations.py:7` — `from dataclasses import dataclass`
- `migrations/migrations.py:7` — `from dataclasses import field`

### `json`

- imported in 5659 files
- 5660 import statements
- aliases: _json

Sample imports:
- `bridge_sovereign_nexus.py:9` — `import json`
- `constitutional_state_machine.py:7` — `import json`
- `generative_sdlc_universe.py:7` — `import json`
- `cs_coordinate_matrix.py:8` — `import json`
- `sovereign_matrix_refinement.py:7` — `import json`

### `time`

- imported in 4136 files
- 4139 import statements

Sample imports:
- `bridge_sovereign_nexus.py:10` — `import time`
- `constitutional_state_machine.py:8` — `import time`
- `generative_sdlc_universe.py:8` — `import time`
- `reality_engine.py:9` — `import time`
- `kernel_bootstrap.py:1` — `import time`

### `hashlib`

- imported in 4135 files
- 4138 import statements

Sample imports:
- `bridge_sovereign_nexus.py:11` — `import hashlib`
- `reality_engine.py:8` — `import hashlib`
- `meta_glasses_integration/meta_glasses_integration.py:4` — `import hashlib`
- `migrations/migrations.py:4` — `import hashlib`
- `whisper_cpp_bindings/whisper_cpp_bindings.py:4` — `import hashlib`

### `pathlib`

- imported in 1607 files
- 1609 import statements

Sample imports:
- `conftest.py:5` — `from pathlib import Path`
- `setup_repo.py:2` — `from pathlib import Path`
- `bridge_sovereign_nexus.py:13` — `from pathlib import Path`
- `dcs_codeql/pycheck.py:7` — `from pathlib import Path`
- `dcs_codeql/dyncheck.py:15` — `from pathlib import Path`

### `typing`

- imported in 274 files
- 293 import statements

Sample imports:
- `constitutional_state_machine.py:9` — `from typing import Dict`
- `constitutional_state_machine.py:9` — `from typing import Any`
- `constitutional_state_machine.py:9` — `from typing import List`
- `constitutional_state_machine.py:9` — `from typing import Optional`
- `reality_engine.py:10` — `from typing import List`

### `sys`

- imported in 89 files
- 91 import statements
- aliases: _s

Sample imports:
- `conftest.py:4` — `import sys`
- `setup_repo.py:1` — `import sys`
- `bridge_sovereign_nexus.py:7` — `import sys`
- `discover_coverage.py:2` — `import sys`
- `scaffold_matrix.py:3` — `import sys`

### `collections`

- imported in 78 files
- 90 import statements

Sample imports:
- `app/localmodel.py:30` — `from collections.abc import Callable`
- `app/manifold.py:4` — `from collections.abc import Callable`
- `dcs/breadth.py:5` — `from collections import defaultdict`
- `dcs/coalesce.py:14` — `from collections import Counter`
- `dcs/coalesce.py:15` — `from collections.abc import Callable`

### `os`

- imported in 53 files
- 55 import statements

Sample imports:
- `run.py:1` — `import os`
- `conftest.py:2` — `import os`
- `bridge_sovereign_nexus.py:8` — `import os`
- `discover_coverage.py:1` — `import os`
- `scaffold_matrix.py:2` — `import os`

### `re`

- imported in 41 files
- 41 import statements
- aliases: _re

Sample imports:
- `tools/gen_type_constructors.py:5` — `import re`
- `tools/auto_fill_attrs.py:2` — `import re`
- `tools/auto_fill.py:2` — `import re`
- `tools/post_regen.py:3` — `import re`
- `tools/gen_grammar_spec.py:17` — `import re`

### `datetime`

- imported in 18 files
- 35 import statements

Sample imports:
- `app/main.py:1` — `import datetime`
- `enterprise_aiops/inference_bridge.py:3` — `from datetime import datetime`
- `enterprise_aiops/inference_bridge.py:3` — `from datetime import timezone`
- `dcs/oscal.py:17` — `from datetime import UTC`
- `dcs/oscal.py:17` — `from datetime import datetime`

### `random`

- imported in 29 files
- 31 import statements

Sample imports:
- `dcs/apop.py:4` — `import random`
- `dcs/hats/qt.py:3` — `import random`
- `dcs/hats/so.py:3` — `import random`
- `dcs/nature/flocking.py:4` — `import random`
- `dcs/nature/stigmergy.py:4` — `import random`

### `subprocess`

- imported in 28 files
- 28 import statements

Sample imports:
- `conftest.py:3` — `import subprocess`
- `setup_repo.py:1` — `import subprocess`
- `kernel_bootstrap.py:1` — `import subprocess`
- `whisper_cpp_bindings/test_bindings.py:1` — `import subprocess`
- `tools/auto_fill_attrs.py:3` — `import subprocess`

### `sqlite3`

- imported in 20 files
- 27 import statements

Sample imports:
- `bridge_sovereign_nexus.py:12` — `import sqlite3`
- `scripts/stability.py:251` — `import sqlite3`
- `scripts/stability.py:275` — `import sqlite3`
- `scripts/stability.py:299` — `import sqlite3`
- `scripts/build_capabilities.py:9` — `import sqlite3`

### `ast`

- imported in 26 files
- 27 import statements
- aliases: _ast

Sample imports:
- `dcs_codeql/pycheck.py:5` — `import ast`
- `tools/post_regen.py:2` — `import ast`
- `tools/gen_grammar_spec.py:15` — `import ast`
- `scripts/stability.py:21` — `import ast`
- `dcs/hats/cmp.py:3` — `import ast as _ast`

### `importlib`

- imported in 20 files
- 20 import statements

Sample imports:
- `app/shape.py:213` — `import importlib`
- `tests/test_codeql.py:1` — `import importlib`
- `tests/test_puzzles.py:1` — `import importlib`
- `tests/test_proof.py:1` — `import importlib`
- `tests/test_canon.py:1` — `import importlib`

### `argparse`

- imported in 18 files
- 18 import statements

Sample imports:
- `app/cli.py:4` — `import argparse`
- `app/shape_cli.py:4` — `import argparse`
- `scripts/autoheal.py:18` — `import argparse`
- `dcs/cli.py:12` — `import argparse`
- `dcs/mesh/__main__.py:3` — `import argparse`

### `concurrent`

- imported in 10 files
- 14 import statements
- aliases: cf

Sample imports:
- `tools/gen_type_constructors.py:7` — `from concurrent.futures import ProcessPoolExecutor`
- `tools/gen_type_constructors.py:7` — `from concurrent.futures import as_completed`
- `app/main.py:183` — `from concurrent.futures import ThreadPoolExecutor`
- `dcs/core/difference_engine.py:3` — `from concurrent.futures import ThreadPoolExecutor`
- `dcs/hats/hpc.py:3` — `from concurrent.futures import ThreadPoolExecutor`

### `threading`

- imported in 14 files
- 14 import statements

Sample imports:
- `dcs/laws.py:374` — `import threading`
- `dcs/crosscut/concurrency.py:3` — `import threading`
- `app/octet/backrooms.py:3` — `import threading`
- `app/core/streaming_substrate.py:12` — `import threading`
- `app/core/ram_substrate.py:19` — `import threading`

### `hmac`

- imported in 10 files
- 10 import statements

Sample imports:
- `scripts/sign_sbom.py:7` — `import hmac`
- `scripts/verify_sbom.py:6` — `import hmac`
- `scripts/build_higher.py:19` — `import hmac`
- `dcs/evidence_chain.py:2` — `import hmac`
- `dcs/verify.py:5` — `import hmac`

### `shutil`

- imported in 9 files
- 9 import statements

Sample imports:
- `setup_repo.py:1` — `import shutil`
- `app/localmodel.py:28` — `import shutil`
- `scripts/autoheal.py:20` — `import shutil`
- `app/mesh/codeql_runner.py:4` — `import shutil`
- `app/meta/staging.py:5` — `import shutil`

### `asyncio`

- imported in 8 files
- 8 import statements

Sample imports:
- `app/moa_cluster.py:1` — `import asyncio`
- `enterprise_aiops/orchestrator.py:1` — `import asyncio`
- `tests/test_grammar.py:1` — `import asyncio`
- `app/mesh/convergence.py:4` — `import asyncio`
- `app/grammar/engine.py:1` — `import asyncio`

### `builtins`

- imported in 8 files
- 8 import statements

Sample imports:
- `app/proof/usefulness.py:14` — `import builtins`
- `app/proof/quality.py:5` — `import builtins`
- `app/proof/sheaf_proof.py:13` — `import builtins`
- `app/proof/grade.py:15` — `import builtins`
- `app/origami/resolve.py:13` — `import builtins`

### `itertools`

- imported in 7 files
- 7 import statements

Sample imports:
- `tools/gen_type_constructors.py:4` — `import itertools`
- `dcs/hats/fmtl.py:3` — `from itertools import product`
- `dcs/equilibrium/templates.py:453` — `from itertools import product`
- `dcs/equilibrium/meta.py:36` — `from itertools import product`
- `app/math/graph.py:5` — `from itertools import combinations`

### `tempfile`

- imported in 6 files
- 6 import statements

Sample imports:
- `dcs_codeql/dyncheck.py:13` — `import tempfile`
- `scripts/stability.py:56` — `import tempfile`
- `dcs/tests/test_triad_full.py:4` — `import tempfile`
- `app/proof/grade.py:20` — `import tempfile`
- `app/combinator/substrate.py:19` — `import tempfile`

### `base64`

- imported in 6 files
- 6 import statements

Sample imports:
- `scripts/sign_sbom.py:5` — `import base64`
- `scripts/verify_sbom.py:4` — `import base64`
- `dcs/intoto.py:18` — `import base64`
- `sovereign-bounded-matrix/platform/app/core/security.py:4` — `import base64`
- `app/proof/grade.py:110` — `import base64`

### `uuid`

- imported in 6 files
- 6 import statements

Sample imports:
- `dcs/oscal.py:16` — `import uuid`
- `app/core/catch_release.py:6` — `import uuid`
- `app/botnetmastery/server.py:2` — `import uuid`
- `app/botnetmastery/models.py:5` — `import uuid`
- `app/supply/sbom.py:7` — `import uuid`

### `struct`

- imported in 6 files
- 6 import statements

Sample imports:
- `kernel/sovereign_kernel.py:4` — `import struct`
- `kernel/master_microkernel.py:4` — `import struct`
- `dcs/hats/au.py:3` — `import struct`
- `dcs/hats/fw.py:3` — `import struct`
- `dcs/hats/re.py:3` — `import struct`

### `socket`

- imported in 5 files
- 5 import statements

Sample imports:
- `dcs_codeql/dyncheck.py:11` — `import socket`
- `dcs/hats/net.py:3` — `import socket`
- `dcs/equilibrium/security.py:120` — `import socket`
- `dcs/equilibrium/templates.py:332` — `import socket`
- `app/proof/offline.py:12` — `import socket`

### `inspect`

- imported in 5 files
- 5 import statements

Sample imports:
- `dcs/generate.py:11` — `import inspect`
- `dcs/tests/test_smoke.py:3` — `import inspect`
- `app/proof/vendor.py:4` — `import inspect`
- `app/proof/regulatory.py:4` — `import inspect`
- `app/core/streaming_substrate.py:11` — `import inspect`

### `enum`

- imported in 5 files
- 5 import statements

Sample imports:
- `dcs/sources/__init__.py:12` — `from enum import Enum`
- `_self/ql/prism.py:3` — `from enum import Enum`
- `app/delta/delta.py:5` — `from enum import Enum`
- `app/core/state_machine.py:5` — `from enum import Enum`
- `app/dispatch/models/base.py:1` — `from enum import Enum`

### `statistics`

- imported in 3 files
- 5 import statements

Sample imports:
- `dcs/equilibrium/systems.py:235` — `import statistics`
- `dcs/equilibrium/systems.py:250` — `import statistics`
- `dcs/equilibrium/systems.py:263` — `import statistics`
- `app/core/observatory.py:11` — `import statistics`
- `app/moat/merge.py:17` — `from statistics import mean`

### `signal`

- imported in 3 files
- 4 import statements

Sample imports:
- `app/mlx_omni_engine.py:24` — `import signal`
- `scripts/stability.py:55` — `import signal`
- `dcs/equilibrium/systems.py:307` — `import signal`
- `dcs/equilibrium/systems.py:351` — `import signal`

### `urllib`

- imported in 4 files
- 4 import statements

Sample imports:
- `scripts/smoke.py:1` — `import urllib.request`
- `dcs/sources/github.py:7` — `import urllib.request`
- `app/murmur/connectors.py:36` — `import urllib.request`
- `app/codeql/runner.py:16` — `import urllib.request`

### `html`

- imported in 3 files
- 3 import statements

Sample imports:
- `dcs/hats/fe.py:3` — `from html.parser import HTMLParser`
- `dcs/equilibrium/security.py:85` — `import html`
- `dcs/equilibrium/templates.py:251` — `from html.parser import HTMLParser`

### `functools`

- imported in 3 files
- 3 import statements

Sample imports:
- `app/core/catch_release.py:10` — `from functools import wraps`
- `app/sacred/constants.py:14` — `from functools import cache`
- `app/puzzles/rubik.py:7` — `from functools import lru_cache`

### `textwrap`

- imported in 2 files
- 2 import statements

Sample imports:
- `setup_repo.py:1` — `import textwrap`
- `app/proof/grade.py:21` — `import textwrap`

### `py_compile`

- imported in 2 files
- 2 import statements

Sample imports:
- `scripts/stability.py:24` — `import py_compile`
- `scripts/selfrun.py:19` — `import py_compile`

### `contextlib`

- imported in 2 files
- 2 import statements

Sample imports:
- `scripts/stability.py:252` — `from contextlib import closing`
- `app/meta/observer.py:4` — `import contextlib`

### `secrets`

- imported in 2 files
- 2 import statements

Sample imports:
- `scripts/build_higher.py:21` — `import secrets`
- `app/supply/sign.py:6` — `import secrets`

## Unused stdlib (not imported anywhere)

- `_abc`
- `_ast`
- `_codecs`
- `_collections`
- `_contextvars`
- `_datetime`
- `_functools`
- `_imp`
- `_io`
- `_locale`
- `_opcode`
- `_operator`
- `_signal`
- `_sre`
- `_stat`
- `_string`
- `_suggestions`
- `_symtable`
- `_sysconfig`
- `_thread`
- `_tokenize`
- `_tracemalloc`
- `_types`
- `_typing`
- `_warnings`
- `_weakref`
- `abc`
- `annotationlib`
- `antigravity`
- `atexit`
- `bdb`
- `bisect`
- `bz2`
- `cProfile`
- `calendar`
- `cmd`
- `code`
- `codecs`
- `codeop`
- `colorsys`
- `compileall`
- `compression`
- `configparser`
- `contextvars`
- `copy`
- `copyreg`
- `csv`
- `ctypes`
- `curses`
- `dbm`
- `decimal`
- `dis`
- `doctest`
- `email`
- `encodings`
- `ensurepip`
- `errno`
- `faulthandler`
- `filecmp`
- `fileinput`
- `fnmatch`
- `fractions`
- `ftplib`
- `gc`
- `genericpath`
- `getopt`
- `getpass`
- `gettext`
- `glob`
- `graphlib`
- `gzip`
- `heapq`
- `http`
- `idlelib`
- `imaplib`
- `ipaddress`
- `keyword`
- `linecache`
- `locale`
- `lzma`
- `mailbox`
- `marshal`
- `mimetypes`
- `modulefinder`
- `netrc`
- `ntpath`
- `nturl2path`
- `numbers`
- `opcode`
- `operator`
- `optparse`
- `pdb`
- `pickle`
- `pickletools`
- `plistlib`
- `poplib`
- `posix`
- `posixpath`
- `pprint`
- `profile`
- `pstats`
- `pty`
- `pwd`
- `pyclbr`
- `pydoc`
- `pydoc_data`
- `queue`
- `quopri`
- `reprlib`
- `rlcompleter`
- `runpy`
- `sched`
- `selectors`
- `shelve`
- `shlex`
- `site`
- `smtplib`
- `socketserver`
- `sre_compile`
- `sre_constants`
- `sre_parse`
- `ssl`
- `stat`
- `stringprep`
- `symtable`
- `sysconfig`
- `tabnanny`
- `test`
- `this`
- `timeit`
- `tkinter`
- `token`
- `tokenize`
- `tomllib`
- `trace`
- `tracemalloc`
- `tty`
- `turtle`
- `turtledemo`
- `venv`
- `wave`
- `weakref`
- `webbrowser`
- `wsgiref`
- `xml`
- `xmlrpc`
- `zipapp`
- `zipfile`
- `zipimport`
- `zoneinfo`
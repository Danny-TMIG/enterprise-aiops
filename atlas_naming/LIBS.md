# Library Mastery Report

- stdlib modules: **227**
- parsed files: **43078**
- venvs found: **9**
- installed packages across all venvs: **484**
- distinct import roots in tree: **1082**
- declared in requirements/pyproject: **19**

## Category counts

| Category | Import statements |
|---|---:|
| third-party | 130192 |
| stdlib | 114073 |
| relative | 87467 |
| unresolved | 10559 |
| local | 843 |

## Third-party dependencies (used)

| Package | Files | Statements | Installed versions | Venvs |
|---|---:|---:|---|---|
| `numpy` | 6157 | 8720 | `2.5.3` | current, .venv, .lanes/ml |
| `torch` | 5376 | 17771 | `2.14.1` | .venv |
| `pytest` | 3658 | 3851 | `9.1.1` | current, .venv, .lanes/ml |
| `pandas` | 1789 | 7144 | `3.0.6` | current, .venv |
| `sympy` | 1678 | 15533 | `1.14.0` | current, .venv |
| `huggingface_hub` | 1613 | 1924 | `1.33.0`, `2.2.0` | current, .venv, .lanes/ml |
| `pip` | 1600 | 8664 | `26.2.1` | current, .venv, .lanes/test, .lanes/web, .lanes/netsec, .lanes/viz, .lanes/ml, .lanes/data, .lanes/quantum |
| `scipy` | 1443 | 3041 | `1.18.1` | current, .venv |
| `networkx` | 1147 | 2571 | `3.7` | current, .venv, .lanes/ml |
| `typing_extensions` | 1027 | 1113 | `4.16.0` | current, .venv, .lanes/ml |
| `mlflow` | 946 | 6642 | `3.16.1` | .venv |
| `cirq` | 941 | 2446 | `1.7.0` | .venv |
| `statsmodels` | 675 | 2547 | `0.15.0` | .venv |
| `pygments` | 634 | 1776 | `2.21.0` | current, .venv, .lanes/ml |
| `django` | 631 | 3077 | `6.1.1` | .venv |
| `transformers` | 567 | 793 | `5.18.0`, `5.19.0` | current, .venv, .lanes/ml |
| `qiskit` | 551 | 2263 | `2.5.2` | .venv |
| `jax` | 550 | 4639 | `0.11.2` | .venv |
| `sklearn` | 538 | 3699 | `?` | .venv |
| `matplotlib` | 449 | 1745 | `3.11.2` | current, .venv |
| `google` | 436 | 1810 | `?` | current, .venv, .lanes/ml |
| `nltk` | 398 | 1420 | `3.10.3` | .venv |
| `PIL` | 367 | 398 | `?` | current, .venv |
| `mlx` | 344 | 794 | `0.32.3` | current, .venv, .lanes/ml |
| `packaging` | 278 | 319 | `26.3` | current, .venv, .lanes/test, .lanes/web, .lanes/netsec, .lanes/viz, .lanes/ml, .lanes/data, .lanes/quantum |
| `peft` | 245 | 545 | `0.21.1` | .venv |
| `hypothesis` | 240 | 1328 | `6.168.3` | .venv, .lanes/ml |
| `mypy` | 224 | 1357 | `2.3.1` | .venv |
| `fontTools` | 221 | 895 | `?` | current, .venv |
| `pydantic` | 215 | 567 | `2.13.5` | current, .venv, .lanes/ml |
| `sqlalchemy` | 207 | 921 | `2.1.1` | .venv |
| `cirq_google` | 189 | 590 | `1.7.0` | .venv |
| `spacy` | 188 | 633 | `3.8.16` | .venv |
| `pyarrow` | 187 | 565 | `25.0.1` | .venv |
| `opentelemetry` | 180 | 629 | `?` | current, .venv, .lanes/ml |
| `cryptography` | 179 | 625 | `50.0.2` | current, .venv, .lanes/ml |
| `redis` | 178 | 882 | `8.1.0` | .venv, .lanes/ml |
| `clickhouse_connect` | 165 | 989 | `1.10.0`, `1.9.0` | current, .venv, .lanes/ml |
| `thinc` | 160 | 255 | `8.3.13` | .venv |
| `narwhals` | 153 | 1183 | `2.26.0` | .venv |
| `openpyxl` | 148 | 655 | `3.1.5` | .venv |
| `rich` | 146 | 333 | `15.0.0` | current, .venv, .lanes/ml |
| `pyasn1` | 146 | 508 | `0.6.4` | .venv |
| `tokenizers` | 141 | 299 | `0.23.2`, `0.23.3` | current, .venv, .lanes/ml |
| `starlette` | 138 | 462 | `1.7.0` | current, .venv, .lanes/ml |
| `accelerate` | 124 | 273 | `1.15.0` | .venv |
| `mpmath` | 124 | 191 | `1.3.0` | current, .venv |
| `requests` | 123 | 162 | `2.34.2` | current, .venv |
| `fastapi` | 116 | 358 | `0.142.2`, `0.143.0` | current, .venv, .lanes/ml |
| `mypyc` | 115 | 688 | `?` | .venv |
| `pyasn1_modules` | 111 | 199 | `0.4.2` | .venv |
| `click` | 105 | 123 | `8.5.0` | current, .venv, .lanes/ml |
| `srsly` | 105 | 270 | `2.5.4` | .venv |
| `alembic` | 98 | 125 | `1.20.0` | .venv |
| `botocore` | 97 | 328 | `1.43.106` | .venv |
| `databricks` | 96 | 444 | `?` | .venv |
| `Cython` | 94 | 216 | `?` | current, .venv, .lanes/ml |
| `yaml` | 91 | 107 | `?` | current, .venv, .lanes/ml |
| `tqdm` | 89 | 92 | `4.70.0`, `4.70.1` | current, .venv, .lanes/ml |
| `coverage` | 85 | 459 | `7.16.2` | .venv, .lanes/ml |
| `IPython` | 84 | 137 | `?` | current |
| `pydantic_core` | 84 | 115 | `2.46.5` | current, .venv, .lanes/ml |
| `docutils` | 79 | 246 | `0.21.2`, `0.23` | current, .venv |
| `fsspec` | 78 | 212 | `2026.9.0` | current, .venv, .lanes/ml |
| `regex` | 74 | 86 | `2026.9.29` | current, .venv, .lanes/ml |
| `safetensors` | 72 | 92 | `0.8.0` | current, .venv, .lanes/ml |
| `cython` | 72 | 103 | `3.3.0` | current, .venv, .lanes/ml |
| `joblib` | 71 | 130 | `1.6.0` | .venv |
| `uvicorn` | 70 | 224 | `0.54.0` | current, .venv, .lanes/ml |
| `grpc` | 70 | 203 | `?` | .venv |
| `setuptools` | 60 | 111 | `84.0.0`, `?` | current, .venv |
| `dateutil` | 60 | 85 | `?` | current, .venv |
| `torchgen` | 58 | 252 | `?` | .venv |
| `diffusers` | 57 | 81 | `0.40.0` | .venv |
| `hvac` | 57 | 168 | `2.4.0` | .venv |
| `backports` | 56 | 92 | `?` | .venv, .lanes/ml |
| `pyquil` | 55 | 225 | `4.21.0` | .venv |
| `wasabi` | 53 | 56 | `1.1.3` | .venv |
| `six` | 52 | 57 | `1.17.0` | current, .venv |
| `zmq` | 50 | 132 | `?` | current, .venv |
| `httpx` | 45 | 46 | `0.28.1` | current, .venv, .lanes/ml |
| `huey` | 45 | 242 | `3.4.0` | .venv |
| `jaxlib` | 44 | 155 | `0.11.2` | .venv |
| `gunicorn` | 42 | 118 | `26.2.0` | .venv |
| `typer` | 41 | 48 | `0.27.2`, `0.27.3` | current, .venv, .lanes/ml |
| `dill` | 40 | 67 | `0.4.1` | .venv |
| `urllib3` | 38 | 98 | `2.7.0`, `2.8.0` | current, .venv, .lanes/ml |
| `graphql` | 37 | 54 | `?` | .venv |
| `anyio` | 35 | 61 | `4.15.1` | current, .venv, .lanes/ml |
| `git` | 35 | 209 | `?` | current, .venv |
| `formulaic` | 34 | 92 | `1.2.2` | .venv |
| `filelock` | 33 | 55 | `3.32.7`, `4.0.7` | current, .venv, .lanes/ml |
| `asgiref` | 33 | 33 | `3.12.1` | .venv |
| `duet` | 33 | 40 | `0.2.9` | .venv |
| `gitdb` | 33 | 99 | `4.0.12` | current, .venv |
| `annotated_doc` | 32 | 32 | `0.0.5` | current, .venv, .lanes/ml |
| `psutil` | 32 | 40 | `7.2.2` | current, .venv |
| `boto3` | 32 | 83 | `1.43.106` | .venv |
| `mpl_toolkits` | 31 | 50 | `?` | current, .venv |
| `patsy` | 31 | 151 | `1.0.3` | .venv |
| `opt_einsum` | 30 | 73 | `3.4.0` | .venv |
| `attr` | 29 | 33 | `?` | current, .venv |
| `qcs_sdk` | 28 | 49 | `?` | .venv |
| `seaborn` | 27 | 95 | `0.13.2` | .venv |
| `skops` | 27 | 75 | `0.16.0` | .venv |
| `functorch` | 26 | 32 | `?` | .venv |
| `markupsafe` | 25 | 38 | `3.0.3` | current, .venv, .lanes/ml |
| `ruamel` | 25 | 119 | `?` | current, .venv |
| `jinja2` | 24 | 49 | `3.1.6` | current, .venv, .lanes/ml |
| `typing_inspection` | 24 | 34 | `0.4.4` | current, .venv, .lanes/ml |
| `sqlparse` | 24 | 54 | `0.6.0` | .venv |
| `cirq_ionq` | 24 | 43 | `1.7.0` | .venv |
| `sphinx` | 23 | 31 | `8.2.3` | current |
| `cffi` | 22 | 44 | `2.1.1` | current, .venv, .lanes/ml |
| `bs4` | 22 | 24 | `?` | current |
| `mako` | 22 | 65 | `1.4.3` | .venv |
| `graphene` | 22 | 33 | `3.4.3` | .venv |
| `mlx_lm` | 21 | 55 | `0.31.3`, `0.32.0` | current, .venv, .lanes/ml |
| `proto` | 21 | 30 | `?` | .venv |
| `werkzeug` | 20 | 61 | `3.1.9` | .venv |
| `stevedore` | 20 | 43 | `5.9.1` | .venv |
| `h2` | 19 | 65 | `4.4.1` | current |
| `lz4` | 19 | 23 | `4.4.5` | current, .venv, .lanes/ml |
| `markdown_it` | 19 | 23 | `?` | current, .venv, .lanes/ml |
| `sentencepiece` | 19 | 21 | `0.2.2` | current, .venv, .lanes/ml |
| `attrs` | 19 | 20 | `26.1.0` | current, .venv |
| `yarl` | 19 | 19 | `1.25.1` | .venv |
| `multidict` | 19 | 19 | `6.9.1` | .venv |
| `rustworkx` | 19 | 22 | `0.18.1` | .venv |
| `tunits` | 19 | 23 | `?` | .venv |
| `pyflakes` | 18 | 42 | `4.0.1` | .venv |
| `aiohttp` | 17 | 32 | `3.14.3` | .venv |
| `pluggy` | 17 | 25 | `1.6.0` | current, .venv, .lanes/ml |
| `tabulate` | 17 | 20 | `0.10.0` | current |
| `annotated_types` | 16 | 24 | `0.8.0` | current, .venv, .lanes/ml |
| `colorama` | 16 | 16 | `0.4.6` | current |
| `brotli` | 16 | 16 | `1.2.0` | current |
| `s3transfer` | 16 | 52 | `0.19.2` | .venv |
| `jaraco` | 16 | 19 | `?` | current, .venv |
| `mypy_extensions` | 16 | 16 | `1.1.0` | .venv |
| `certifi` | 15 | 17 | `2026.7.22` | current, .venv, .lanes/ml |
| `xdist` | 15 | 54 | `?` | .venv |
| `pathspec` | 15 | 46 | `1.1.1` | .venv |
| `contourpy` | 15 | 49 | `1.4.0` | current, .venv |
| `quil` | 15 | 22 | `0.18.0` | .venv |
| `weasel` | 15 | 23 | `1.0.0` | .venv |
| `ipywidgets` | 14 | 20 | `8.1.9` | current |
| `idna` | 14 | 14 | `3.19`, `3.20` | current, .venv, .lanes/ml |
| `librt` | 14 | 15 | `0.16.0` | .venv |
| `jmespath` | 13 | 22 | `1.1.0` | .venv |
| `flask` | 13 | 13 | `3.1.3` | .venv |
| `defusedxml` | 13 | 17 | `0.7.1` | current, .venv |
| `cirq_pasqal` | 13 | 21 | `1.7.0` | .venv |
| `smart_open` | 13 | 35 | `8.0.2` | .venv |
| `rpcq` | 13 | 27 | `3.11.0` | .venv |
| `more_itertools` | 13 | 14 | `11.1.0` | current, .venv |
| `twine` | 13 | 31 | `7.0.0` | .venv |
| `cloudpickle` | 13 | 17 | `3.1.2` | .venv |
| `keyring` | 12 | 15 | `25.7.0` | current, .venv |
| `execnet` | 12 | 27 | `2.1.2` | .venv |
| `cirq_aqt` | 12 | 18 | `1.7.0` | .venv |
| `deprecated` | 12 | 14 | `1.3.1` | .venv |
| `tomli` | 11 | 11 | `2.4.1` | current |
| `catalogue` | 11 | 12 | `2.0.10` | .venv |
| `cirq_web` | 11 | 16 | `1.7.0` | .venv |
| `cycler` | 11 | 11 | `0.12.1` | current, .venv |
| `cachetools` | 11 | 12 | `7.2.0` | .venv |
| `docker` | 11 | 19 | `7.2.0` | .venv |
| `hf_xet` | 10 | 12 | `1.6.0`, `1.7.0` | current, .venv, .lanes/ml |
| `threadpoolctl` | 10 | 12 | `3.7.0` | .venv |
| `tornado` | 10 | 22 | `6.5.10` | current |
| `uvloop` | 9 | 12 | `0.23.0` | current |
| `pyparsing` | 9 | 9 | `3.3.3` | current, .venv |
| `mdurl` | 8 | 16 | `0.1.2` | current, .venv, .lanes/ml |
| `h11` | 8 | 18 | `0.16.0` | current, .venv, .lanes/ml |
| `importlib_metadata` | 8 | 8 | `9.0.1` | current, .venv |
| `sage` | 8 | 10 | `?` | current |
| `confection` | 7 | 8 | `1.3.3` | .venv |
| `gmpy2` | 7 | 7 | `2.4.0a1` | current |
| `cloudpathlib` | 7 | 8 | `0.25.0` | .venv |
| `graphql_relay` | 7 | 7 | `3.2.0` | .venv |
| `sniffio` | 6 | 6 | `1.3.1` | current |
| `httpcore` | 6 | 14 | `1.0.9` | current, .venv, .lanes/ml |
| `dotenv` | 6 | 7 | `?` | current, .venv |
| `iniconfig` | 6 | 8 | `2.3.0`, `2.3.1` | current, .venv, .lanes/ml |
| `websockets` | 6 | 34 | `17.2` | current |
| `charset_normalizer` | 6 | 9 | `3.5.1`, `3.5.2` | current, .venv |
| `pyngrok` | 6 | 17 | `8.1.2` | .venv |
| `ml_dtypes` | 6 | 45 | `0.6.0` | .venv |
| `pexpect` | 5 | 5 | `4.9.0` | current |
| `zipp` | 5 | 5 | `4.1.0` | current, .venv |
| `preshed` | 5 | 6 | `3.0.13` | .venv |
| `smmap` | 5 | 8 | `5.0.3` | current, .venv |
| `grpc_interceptor` | 5 | 12 | `0.15.4` | .venv |
| `shellingham` | 4 | 4 | `1.5.4` | current, .venv, .lanes/ml |
| `httptools` | 4 | 4 | `0.9.0` | current |
| `sortedcontainers` | 4 | 4 | `2.4.0` | .venv, .lanes/ml |
| `wrapt` | 4 | 5 | `2.5.0` | .venv |
| `interface_meta` | 4 | 4 | `2.0.1` | .venv |
| `quax` | 4 | 4 | `?` | .venv |
| `spacy_legacy` | 4 | 7 | `3.0.12` | .venv |
| `watchfiles` | 3 | 3 | `1.3.0` | current |
| `lark` | 3 | 9 | `1.3.1` | current |
| `itsdangerous` | 3 | 6 | `2.2.0` | .venv |
| `termcolor` | 3 | 3 | `3.3.0` | .venv |
| `aiosignal` | 3 | 3 | `1.4.0` | .venv |
| `propcache` | 3 | 3 | `0.5.4` | .venv |
| `qcs_api_client_common` | 3 | 4 | `0.22.1` | .venv |
| `platformdirs` | 3 | 7 | `4.11.6` | current |
| `spacy_loggers` | 3 | 3 | `1.0.5` | .venv |
| `wheel` | 3 | 4 | `0.48.0` | .lanes/test, .lanes/web, .lanes/netsec, .lanes/viz, .lanes/ml, .lanes/data, .lanes/quantum |
| `murmurhash` | 3 | 3 | `1.0.15` | .venv |
| `pycparser` | 2 | 6 | `3.0`, `3.11` | current, .venv, .lanes/ml |
| `httpx2` | 2 | 4 | `2.13.1` | current |
| `pyximport` | 2 | 2 | `?` | current, .venv, .lanes/ml |
| `readme_renderer` | 2 | 4 | `46.0` | .venv |
| `frozenlist` | 2 | 2 | `1.8.0` | .venv |
| `wcwidth` | 2 | 4 | `0.9.1`, `0.9.2` | current, .venv |
| `cymem` | 2 | 2 | `2.0.13` | .venv |
| `requests_toolbelt` | 2 | 2 | `1.0.0` | .venv |
| `traitlets` | 2 | 2 | `5.16.1` | current |
| `prettytable` | 2 | 3 | `3.18.0` | .venv |
| `blis` | 2 | 4 | `1.3.3` | .venv |
| `ipykernel` | 2 | 2 | `7.4.0` | current |
| `babel` | 2 | 2 | `2.18.0` | current |
| `prometheus_client` | 1 | 1 | `0.26.0` | current |
| `blinker` | 1 | 1 | `1.9.0` | .venv |
| `ruff` | 1 | 1 | `0.16.9` | .venv |
| `nh3` | 1 | 1 | `0.3.7` | .venv |
| `aiohappyeyeballs` | 1 | 2 | `2.7.1` | .venv |
| `ast_serialize` | 1 | 1 | `0.11.2` | .venv |
| `kiwisolver` | 1 | 1 | `1.5.1` | current, .venv |
| `msgpack` | 1 | 1 | `1.2.2`, `1.2.3` | current, .venv |
| `id` | 1 | 2 | `1.6.1` | .venv |
| `rfc3986` | 1 | 1 | `2.0.0` | .venv |
| `pytest_timeout` | 1 | 1 | `2.4.0` | .venv |
| `et_xmlfile` | 1 | 1 | `2.0.0` | .venv |
| `tzdata` | 1 | 1 | `2026.5` | current |
| `flask_cors` | 1 | 1 | `6.0.5` | .venv |
| `jupyter_core` | 1 | 1 | `5.9.1` | current |
| `grpc_status` | 1 | 1 | `?` | .venv |
| `pycosat` | 1 | 1 | `0.6.6` | current |
| `websocket` | 1 | 1 | `?` | current |
| `nbconvert` | 1 | 2 | `7.17.2` | current |
| `nbformat` | 1 | 1 | `5.11.1` | current |

## Stdlib dependencies (used)

| Module | Files | Statements | Aliases |
|---|---:|---:|---|
| `typing` | 12735 | 15649 | T, _t, _typing, t, te, ty |
| `__future__` | 12165 | 12168 | — |
| `dataclasses` | 7050 | 7124 | _dataclasses, dataclasses, dc |
| `collections` | 7033 | 8353 | _collections, _collections_abc, c, cabc, collections_abc |
| `json` | 6854 | 6881 | _builtin_json, _json, _py_json, jd, js, jsonlib, py_json |
| `time` | 5208 | 5247 | _time, mod_time, time_mod |
| `sys` | 4759 | 4871 | _s, _sys |
| `hashlib` | 4449 | 4463 | mod |
| `os` | 3940 | 4243 | _os, _osp, op, osp |
| `pathlib` | 3041 | 3079 | — |
| `functools` | 3015 | 3132 | _functools |
| `re` | 2970 | 3035 | _re, sre, sre_parse |
| `warnings` | 2699 | 2826 | _warnings |
| `logging` | 2559 | 2652 | _logging, std_logging |
| `itertools` | 2006 | 2094 | _itertools, it, itl |
| `contextlib` | 1551 | 1625 | — |
| `inspect` | 1345 | 1441 | _py_inspect |
| `datetime` | 1284 | 1344 | DT, dt, pydt |
| `types` | 1246 | 1329 | _types, builtin_types, python_types |
| `io` | 1230 | 1296 | _io, cStringIO |
| `enum` | 1013 | 1036 | — |
| `operator` | 1010 | 1043 | op |
| `copy` | 969 | 986 | _copy, copymodule, python_copy |
| `abc` | 878 | 889 | — |
| `threading` | 851 | 876 | — |
| `importlib` | 839 | 1047 | _importlib, _meta, im, importlib_metadata, importlib_resources, metadata, resources |
| `urllib` | 612 | 798 | ul, url, urllib2, urllib_parse, urllib_request |
| `shutil` | 573 | 602 | — |
| `tempfile` | 541 | 550 | — |
| `subprocess` | 516 | 541 | sp |
| `textwrap` | 505 | 515 | — |
| `random` | 469 | 488 | _random, random_module |
| `unittest` | 367 | 407 | mock |
| `weakref` | 353 | 367 | — |
| `argparse` | 351 | 374 | — |
| `platform` | 342 | 346 | _platform, pl, py_platform |
| `numbers` | 338 | 348 | nums |
| `pickle` | 332 | 370 | cpickle |
| `socket` | 319 | 355 | pysocket |
| `asyncio` | 317 | 362 | async_timeout |
| `ssl` | 293 | 347 | _ssl |
| `struct` | 292 | 296 | — |
| `traceback` | 290 | 309 | tb, tb_lib |
| `uuid` | 275 | 278 | — |
| `email` | 272 | 446 | — |
| `base64` | 256 | 258 | — |
| `ctypes` | 247 | 412 | ct |
| `http` | 241 | 304 | http_client, httplib |
| `optparse` | 237 | 254 | — |
| `zipfile` | 220 | 244 | — |
| `ast` | 212 | 221 | _ast, ast3 |
| `sysconfig` | 206 | 208 | — |
| `builtins` | 205 | 208 | __builtin__, _builtins, m |
| `concurrent` | 200 | 226 | cf |
| `string` | 194 | 199 | — |
| `decimal` | 192 | 205 | _decimal |
| `errno` | 178 | 186 | errno_mod |
| `multiprocessing` | 160 | 211 | _util, mp, python_multiprocessing, util |
| `glob` | 148 | 157 | fileglob, glob_module |
| `codecs` | 139 | 139 | — |
| `stat` | 134 | 138 | — |
| `html` | 129 | 161 | htmlentitydefs |
| `gc` | 117 | 134 | — |
| `queue` | 115 | 121 | Queue, q, queue_module |
| `posixpath` | 108 | 109 | _posix_flavour |
| `shlex` | 107 | 109 | — |
| `signal` | 103 | 109 | — |
| `gzip` | 101 | 107 | — |
| `atexit` | 97 | 98 | — |
| `bisect` | 95 | 96 | — |
| `configparser` | 93 | 93 | cp |
| `ipaddress` | 92 | 104 | — |
| `contextvars` | 88 | 90 | — |
| `locale` | 83 | 93 | — |
| `fnmatch` | 83 | 83 | — |
| `mimetypes` | 78 | 78 | — |
| `pprint` | 77 | 80 | — |
| `keyword` | 74 | 74 | kw |
| `csv` | 72 | 73 | csvlib |
| `fractions` | 72 | 74 | — |
| `xml` | 72 | 118 | ET, ETree, dom, etree, foobar |
| `heapq` | 68 | 70 | — |
| `difflib` | 61 | 65 | — |
| `zoneinfo` | 61 | 65 | — |
| `doctest` | 59 | 82 | pdoctest |
| `bz2` | 58 | 62 | — |
| `tokenize` | 55 | 55 | — |
| `tarfile` | 53 | 53 | — |
| `calendar` | 52 | 53 | — |
| `sqlite3` | 48 | 65 | — |
| `getpass` | 48 | 48 | _getpass_mod |
| `pkgutil` | 46 | 54 | — |
| `secrets` | 41 | 41 | — |
| `colorsys` | 40 | 42 | — |
| `linecache` | 36 | 36 | — |
| `hmac` | 35 | 35 | — |
| `site` | 34 | 34 | — |
| `copyreg` | 33 | 33 | _copy_reg, copy_reg |
| `compression` | 31 | 31 | _compression |
| `lzma` | 31 | 34 | — |
| `gettext` | 31 | 39 | gettext_module |
| `reprlib` | 29 | 29 | — |
| `dis` | 27 | 28 | — |
| `timeit` | 27 | 27 | — |
| `xmlrpc` | 25 | 37 | xmlrpclib |
| `tomllib` | 22 | 22 | toml_, tomllib |
| `annotationlib` | 22 | 26 | — |
| `tkinter` | 22 | 62 | tk, ttk |
| `zipimport` | 21 | 21 | — |
| `ntpath` | 15 | 15 | — |
| `pydoc` | 15 | 15 | — |
| `py_compile` | 14 | 14 | — |
| `runpy` | 14 | 14 | — |
| `encodings` | 14 | 16 | — |
| `_thread` | 14 | 19 | — |
| `statistics` | 14 | 16 | — |
| `webbrowser` | 13 | 13 | — |
| `netrc` | 12 | 12 | — |
| `pwd` | 12 | 14 | — |
| `pty` | 10 | 10 | — |
| `_imp` | 10 | 10 | — |
| `venv` | 10 | 10 | — |
| `tty` | 10 | 10 | — |
| `pdb` | 10 | 14 | — |
| `faulthandler` | 10 | 18 | — |
| `_osx_support` | 9 | 10 | — |
| `plistlib` | 9 | 9 | — |
| `marshal` | 9 | 9 | — |
| `tracemalloc` | 9 | 9 | — |
| `selectors` | 9 | 9 | — |
| `_aix_support` | 8 | 8 | — |
| `compileall` | 8 | 8 | — |
| `cProfile` | 8 | 8 | — |
| `pstats` | 8 | 9 | — |
| `pickletools` | 7 | 7 | — |
| `token` | 5 | 5 | — |
| `code` | 5 | 5 | — |
| `filecmp` | 4 | 4 | — |
| `bdb` | 4 | 4 | — |
| `ftplib` | 4 | 5 | — |
| `socketserver` | 4 | 4 | — |
| `graphlib` | 4 | 4 | — |
| `trace` | 3 | 3 | — |
| `rlcompleter` | 3 | 3 | — |
| `_ast` | 3 | 33 | — |
| `_collections_abc` | 3 | 3 | — |
| `getopt` | 3 | 3 | — |
| `wsgiref` | 3 | 3 | — |
| `_collections` | 3 | 3 | — |
| `_string` | 2 | 2 | — |
| `sre_constants` | 2 | 2 | sre |
| `sre_parse` | 2 | 2 | — |
| `fileinput` | 2 | 2 | — |
| `opcode` | 2 | 2 | — |
| `_codecs` | 2 | 2 | — |
| `_compat_pickle` | 2 | 2 | — |
| `symtable` | 2 | 2 | — |
| `shelve` | 2 | 2 | — |
| `_pyio` | 2 | 2 | — |
| `_warnings` | 2 | 2 | — |
| `wave` | 2 | 2 | — |
| `profile` | 2 | 2 | — |
| `curses` | 1 | 1 | — |
| `dbm` | 1 | 1 | dbm |
| `_contextvars` | 1 | 1 | — |
| `smtplib` | 1 | 1 | — |
| `cmd` | 1 | 1 | — |
| `posix` | 1 | 1 | — |
| `_io` | 1 | 1 | — |
| `_operator` | 1 | 1 | — |

## Local imports

| Name | Files | Statements |
|---|---:|---:|
| `app` | 236 | 593 |
| `dcs` | 138 | 231 |
| `aiops_platform` | 16 | 17 |
| `pimeyes_integration` | 1 | 1 |
| `meta_glasses_integration` | 1 | 1 |

## Unresolved imports

These names are not stdlib, not third-party in any venv, and not local.
They are dead imports, missing dependencies, or typos.

| Name | Files | First site |
|---|---:|---|
| `math` | 2607 | `reality_engine.py:7` — `math` |
| `_pytest` | 1541 | `.lanes/ml/lib/python3.12/site-packages/_hypothesis_pytestplugin.py:34` — `_pytest.junitxml` |
| `torchvision` | 346 | `.lanes/ml/lib/python3.12/site-packages/transformers/image_utils.py:54` — `torchvision.io` |
| `torch_xla` | 320 | `.lanes/ml/lib/python3.12/site-packages/transformers/pytorch_utils.py:227` — `torch_xla` |
| `cutlass` | 281 | `.venv/lib/python3.12/site-packages/torch/_inductor/utils.py:2190` — `cutlass.operators.utils.dtype` |
| `distutils` | 280 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/distlib/util.py:1991` — `distutils` |
| `triton` | 164 | `.venv/lib/python3.12/site-packages/torch/_utils_internal.py:247` — `triton.testing` |
| `_typeshed` | 134 | `.lanes/quantum/lib/python3.12/site-packages/wheel/wheelfile.py:18` — `_typeshed` |
| `pyspark` | 129 | `.venv/lib/python3.12/site-packages/narwhals/dependencies.py:22` — `pyspark.sql` |
| `unicodedata` | 108 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/pygments/unistring.py:111` — `unicodedata` |
| `zlib` | 105 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/cachecontrol/adapter.py:8` — `zlib` |
| `array` | 104 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/idna/uts46data.py:3` — `array` |
| `deepspeed` | 95 | `.lanes/ml/lib/python3.12/site-packages/transformers/modeling_utils.py:1445` — `deepspeed` |
| `dask` | 84 | `.lanes/ml/lib/python3.12/site-packages/tqdm/dask.py:3` — `dask.callbacks` |
| `binascii` | 72 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/urllib3/filepost.py:3` — `binascii` |
| `openai` | 72 | `.lanes/ml/lib/python3.12/site-packages/transformers/cli/serving/transcription.py:28` — `openai.types.audio.transcription_create_params` |
| `tensorflow` | 63 | `.lanes/ml/lib/python3.12/site-packages/tqdm/keras.py:10` — `tensorflow` |
| `jnius` | 54 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/platformdirs/android.py:223` — `jnius` |
| `torchao` | 53 | `.lanes/ml/lib/python3.12/site-packages/transformers/trainer_optimizer.py:466` — `torchao.optim` |
| `mmap` | 52 | `kernel/sovereign_kernel.py:2` — `mmap` |
| `llama_index` | 51 | `.venv/lib/python3.12/site-packages/mlflow/llama_index/serialize_objects.py:7` — `llama_index.core` |
| `bitsandbytes` | 49 | `.lanes/ml/lib/python3.12/site-packages/transformers/trainer_optimizer.py:253` — `bitsandbytes.optim` |
| `ftfy` | 48 | `.lanes/ml/lib/python3.12/site-packages/transformers/models/pp_formulanet/modular_pp_formulanet.py:240` — `ftfy` |
| `checks` | 48 | `.lanes/ml/lib/python3.12/site-packages/numpy/_core/tests/test_cython.py:87` — `checks` |
| `cupy` | 48 | `.venv/lib/python3.12/site-packages/thinc/compat.py:6` — `cupy` |
| `polars` | 45 | `.lanes/ml/lib/python3.12/site-packages/clickhouse_connect/driver/options.py:63` — `polars` |
| `OpenSSL` | 44 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/requests/help.py:27` — `OpenSSL` |
| `langchain_core` | 43 | `.venv/lib/python3.12/site-packages/mlflow/types/responses.py:138` — `langchain_core.messages` |
| `cmath` | 41 | `.lanes/ml/lib/python3.12/site-packages/numpy/_core/tests/test_umath.py:4532` — `cmath` |
| `winreg` | 40 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/requests/utils.py:101` — `winreg` |
| `numba` | 38 | `.lanes/ml/lib/python3.12/site-packages/numpy/random/tests/test_extending.py:28` — `numba` |
| `cutlass_library` | 38 | `.venv/lib/python3.12/site-packages/torch/_inductor/codegen/cutlass/gemm_template.py:690` — `cutlass_library.library` |
| `datasets` | 36 | `.lanes/ml/lib/python3.12/site-packages/transformers/trainer_seq2seq.py:36` — `datasets` |
| `litellm` | 35 | `.venv/lib/python3.12/site-packages/mlflow/crewai/autolog.py:91` — `litellm` |
| `lxml` | 34 | `.lanes/ml/lib/python3.12/site-packages/networkx/conftest.py:196` — `lxml` |
| `exceptiongroup` | 34 | `.lanes/ml/lib/python3.12/site-packages/starlette/_utils.py:25` — `exceptiongroup` |
| `torchaudio` | 33 | `.lanes/ml/lib/python3.12/site-packages/transformers/audio_utils.py:58` — `torchaudio` |
| `gevent` | 33 | `.lanes/ml/lib/python3.12/site-packages/coverage/collector.py:139` — `gevent` |
| `psycopg` | 33 | `.venv/lib/python3.12/site-packages/huey/storage.py:31` — `psycopg` |
| `tensorboard` | 33 | `.venv/lib/python3.12/site-packages/torch/utils/tensorboard/_pytorch_graph.py:6` — `tensorboard.compat.proto.config_pb2` |
| `duckdb` | 32 | `.lanes/ml/lib/python3.12/site-packages/huggingface_hub/_dataset_viewer.py:26` — `duckdb` |
| `kernels` | 32 | `.lanes/ml/lib/python3.12/site-packages/transformers/modeling_utils.py:150` — `kernels.layer.mode` |
| `executorch` | 32 | `.lanes/ml/lib/python3.12/site-packages/transformers/exporters/exporter_executorch.py:81` — `executorch.backends.xnnpack.partition.xnnpack_partitioner` |
| `select` | 30 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/urllib3/util/wait.py:3` — `select` |
| `pyodide` | 30 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/emscripten/fetch.py:46` — `pyodide.ffi` |
| `langchain` | 29 | `.venv/lib/python3.12/site-packages/mlflow/langchain/model.py:253` — `langchain` |
| `sqlframe` | 28 | `.venv/lib/python3.12/site-packages/narwhals/_native.py:133` — `sqlframe.base.dataframe` |
| `ibis` | 27 | `.venv/lib/python3.12/site-packages/narwhals/dependencies.py:17` — `ibis` |
| `_ssl` | 26 | `.lanes/quantum/lib/python3.12/site-packages/pip/_vendor/truststore/_api.py:10` — `_ssl` |
| `dspy` | 26 | `.venv/lib/python3.12/site-packages/mlflow/dspy/save.py:126` — `dspy` |

## Declared but unused

Requirements list these, but no file imports them.

- `1.0.0`
- `3.11`
- `aiops_platform`
- `auto`
- `mit`
- `py311`
- `pytest_asyncio`
- `readme.md`
- `setuptools.build_meta`
- `tests`

## Used but undeclared

Files import these, but requirements.txt / pyproject.toml do not list them.

- `Cython`
- `IPython`
- `PIL`
- `accelerate`
- `aiohappyeyeballs`
- `aiohttp`
- `aiosignal`
- `alembic`
- `annotated_doc`
- `annotated_types`
- `anyio`
- `asgiref`
- `ast_serialize`
- `attr`
- `attrs`
- `babel`
- `backports`
- `blinker`
- `blis`
- `boto3`
- `botocore`
- `brotli`
- `bs4`
- `cachetools`
- `catalogue`
- `certifi`
- `cffi`
- `charset_normalizer`
- `cirq`
- `cirq_aqt`
- `cirq_google`
- `cirq_ionq`
- `cirq_pasqal`
- `cirq_web`
- `click`
- `clickhouse_connect`
- `cloudpathlib`
- `cloudpickle`
- `colorama`
- `confection`
- `contourpy`
- `coverage`
- `cryptography`
- `cycler`
- `cymem`
- `cython`
- `databricks`
- `dateutil`
- `defusedxml`
- `deprecated`
- `diffusers`
- `dill`
- `django`
- `docker`
- `docutils`
- `dotenv`
- `duet`
- `et_xmlfile`
- `execnet`
- `filelock`
- `flask`
- `flask_cors`
- `fontTools`
- `formulaic`
- `frozenlist`
- `fsspec`
- `functorch`
- `git`
- `gitdb`
- `gmpy2`
- `google`
- `graphene`
- `graphql`
- `graphql_relay`
- `grpc`
- `grpc_interceptor`
- `grpc_status`
- `gunicorn`
- `h11`
- `h2`

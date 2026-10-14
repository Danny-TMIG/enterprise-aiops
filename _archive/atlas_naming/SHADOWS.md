# Stdlib Shadow Action List

Runtime resolution executed in subprocess with `cwd=repo root`.
`SHADOW` means the name resolves inside the repo, breaking stdlib imports.

| Shadowed | Origin | Status | Files |
|---|---|:---:|---:|
| `dis` | `/Users/metadusa/miniforge3/lib/python3.14/dis.py` | clean | 4 |
| `platform` | `/Users/metadusa/miniforge3/lib/python3.14/platform.py` | clean | 13 |

## Detail
### `dis`

- runtime origin: `/Users/metadusa/miniforge3/lib/python3.14/dis.py`
- as package: 4 files
  - `app/dis/dis.py`
  - `app/dis/__init__.py`
  - `app/dis/models/__init__.py`
  - `app/dis/models/local_mlx.py`

### `platform`

- runtime origin: `/Users/metadusa/miniforge3/lib/python3.14/platform.py`
- as package: 13 files
  - `sovereign-bounded-matrix/platform/__init__.py`
  - `sovereign-bounded-matrix/platform/platform.py`
  - `sovereign-bounded-matrix/platform/app/__init__.py`
  - `sovereign-bounded-matrix/platform/app/app.py`
  - `sovereign-bounded-matrix/platform/app/core/security.py`

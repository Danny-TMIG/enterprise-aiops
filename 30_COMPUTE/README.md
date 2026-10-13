# 30_COMPUTE

Hardware-specific compute modules. Each subfolder targets a specific
accelerator or runtime.

## Subfolders

- mlx_bridge/   Apple Silicon MLX runtime bridge

## 30_COMPUTE/mlx_bridge/

Bridges the AIOps stack to MLX for on-device inference on Apple Silicon.

## 30_COMPUTE/mlx_bridge/hardware_init.py

- Imports: platform, subprocess, sys
- Detects chip family and available unified memory
- Not imported by aiops_platform at runtime; invoked as a standalone probe

## Note

The `import platform` here refers to the Python stdlib module and is
correct. Do not rename.

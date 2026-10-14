# app

Auxiliary applications and integrations. Not part of the aiops_platform
installable package.

## Subfolders

- codeql/   CodeQL semantic code analysis runner and queries

## app/codeql/

Runs CodeQL scans against the repository. Produces SARIF output for
security review.

## app/codeql/runner.py

- Imports: platform, subprocess, sys
- Invokes CodeQL CLI on configured query packs
- Not invoked by aiops_platform; standalone tool

## Note

The `import platform` at app/codeql/runner.py refers to the Python
stdlib module and is correct. Do not rename.

# Operations

## Run

    make install-dev
    make serve

## Test

    make test

## SBOM

    make sbom        # writes SBOM.json
    make sign        # writes SBOM.sig
    make verify      # verifies signature

## CodeQL

    make codeql      # writes .codeql-results/results.sarif

## Logs

- uvicorn: `uvicorn.log`
- botnet:  `data/botnet.db`
- seed:    in-memory (per-process)

# Publishing dcs

The `dcs` package is the license standard. It installs standalone.

## As a PyPI package

    cd ~/enterprise_aiops
    python -m build
    twine upload dist/dcs-0.5.0*

## As a git-installable package

    pip install git+https://github.com/<user>/enterprise_aiops.git

## As a wheel anyone can verify

    pip install dcs-0.5.0-py3-none-any.whl
    dcs attest                  # 8/8 PASS
    dcs license issue --holder my-system
    dcs license verify --file license_my-system.json --log dcs_ct_log.json

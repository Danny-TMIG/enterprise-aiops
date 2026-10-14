# Threat Model

Generated: 2026-10-01T17:52:03.353255+00:00
Method: STRIDE

| File | SHA256 |
|---|---|
| dcs/verify.py | 3cd6413efe38561a96e20c6d091e0f120a75b4cde0dafcf3709fdca3d56c8ef4 |
| dcs/verify_intoto.py | af27a95c98d1f9608fa7df5ebc933ea2b1b0b6ae599dd042f517daf6971f122a |
| dcs/self.py | db35b659612b7babd6990a2a6b354c2792da77e0d82a1f5a499e530a13ae535b |
| dcs/sdlc_engine.py | 6c76a45ac734c699b0ed5b83b302bf69bc0e9391894402776683e6b9e595ae0d |
| dcs/mesh/behavior.py | 8c8187354b6e5cdb823e1baf70cb65092eb9ea404cd493a30984cd0802c3ee1d |

| Threat | Control | SDLC | Standard |
|---|---|---|---|
| Tampering | CT + SHA256 | SDLC-0001 | NIST 800-53 |
| Spoofing | in-toto + SLSA | SDLC-0002 | SLSA 1.0 |
| Supply chain | SBOM (221) | SDLC-0003 | OpenSSF |
| Repudiation | Signed commits | SDLC-0004 | Sigstore |
| Info disclosure | Data policy | SDLC-0005 | GDPR |
| DoS | Rate limiting | SDLC-0006 | OWASP ASVS |
| Elevation | Least privilege | SDLC-0007 | NIST 800-207 |

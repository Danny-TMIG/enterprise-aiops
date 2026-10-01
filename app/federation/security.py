from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

SPIFFE_HEADER = APIKeyHeader(name="X-Spiffe-ID", auto_error=False)
MTLS_FINGERPRINT_HEADER = APIKeyHeader(name="X-Client-Cert-Sha256", auto_error=False)


async def verify_federated_node(
    spiffe_id: str = Security(SPIFFE_HEADER),
    cert_fp: str = Security(MTLS_FINGERPRINT_HEADER),
) -> str:
    if not spiffe_id or not spiffe_id.startswith("spiffe://enterprise.mesh/ns/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing SPIFFE ID for federated trust domain.",
        )
    if not cert_fp or len(cert_fp) != 64:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing cryptographic mTLS client certificate fingerprint.",
        )
    return spiffe_id

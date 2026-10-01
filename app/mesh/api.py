from fastapi import APIRouter

router = APIRouter()

@router.get("/mesh/status")
def mesh_status():
    return {"status": "active", "mesh": "healthy"}

import os

import uvicorn

if __name__ == "__main__":
    print("[+] Launching Enterprise AIOps Engine in Production Mode (Single Worker, No Reload)...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run with reload=False to prevent double-initialization memory spikes on Apple Silicon
    uvicorn.run(
        "inference_bridge:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        workers=1,
        log_level="info"
    )

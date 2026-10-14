from fastapi import FastAPI
from ax.sovereign_client import AetherSovereignClient

app = FastAPI()
sovereign_client = AetherSovereignClient()

@app.post("/api/v1/execute")
async def execute_task(payload: dict):
    prompt = payload.get("prompt", "Generate status report for local sovereign node.")
    temperature = payload.get("temperature", 0.2)

    try:
        result = sovereign_client.query(prompt, temperature=temperature)
        ai_response = result["choices"][0]["message"]["content"]
    except Exception as e:
        ai_response = f"[ERROR] Local inference failed: {str(e)}"

    return {
        "status": "success",
        "node": "aether-core-asgi",
        "acceleration_layer": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "response": ai_response
    }

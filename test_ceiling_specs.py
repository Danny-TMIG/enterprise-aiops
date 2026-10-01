import asyncio
import time

from app.mlx_omni_engine import orchestrator


async def benchmark_ceiling():
    start = time.time()
    dummy_text = "Enterprise balance sheet Q3 2026 revenue: $450,000,000 net profit: $120,000,000."
    metadata = {"bbox": [0, 0, 100, 100]}

    tasks = [
        orchestrator.process_request(document_text=dummy_text, layout_metadata=metadata)
        for _ in range(10)
    ]
    _ = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    print(
        f"Ceiling Benchmark: 10 concurrent multi-agent MoA pipelines resolved in {elapsed:.2f}s"
    )


if __name__ == "__main__":
    asyncio.run(benchmark_ceiling())

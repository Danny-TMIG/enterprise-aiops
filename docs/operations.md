# Operations

Start:

    python3 -m aiops_platform.app.asgi

Kill port 8000:

    lsof -ti:8000 | xargs -r kill -9

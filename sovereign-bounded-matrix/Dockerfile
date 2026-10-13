FROM python:3.11-slim AS builder
WORKDIR /app
COPY platform/ requirements.txt* ./
RUN pip install --no-cache-dir fastapi uvicorn pydantic pandas openpyxl mlx mlx-lm

FROM python:3.11-slim
WORKDIR /app
RUN useradd -u 10001 asfuser
USER asfuser
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app/
EXPOSE 8000
CMD ["uvicorn", "platform.app.__main__:app", "--host", "0.0.0.0", "--port", "8000"]

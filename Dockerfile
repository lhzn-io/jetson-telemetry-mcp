FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY assets /app/assets/
COPY src /app/src/

RUN pip install --no-cache-dir -e .

EXPOSE 8765
ENV PORT=8765
ENV HOST=0.0.0.0

CMD ["python", "-m", "jetson_telemetry_mcp.server"]
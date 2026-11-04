# Runs the json-shaper-lite MCP server over stdio (used by Glama's build checks).
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir . && useradd -m app
USER app
ENTRYPOINT ["json-shaper-lite-mcp"]

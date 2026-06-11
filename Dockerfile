FROM python:3.12-slim

# Node.js 22 — the agent's hands are the MongoDB MCP server, spawned via stdio
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Warm the MCP server so the first agent cycle doesn't wait on npm
RUN npm install -g mongodb-mcp-server@latest

COPY app ./app
COPY web ./web

ENV PORT=8080
EXPOSE 8080
CMD exec uvicorn app.server:app --host 0.0.0.0 --port ${PORT}

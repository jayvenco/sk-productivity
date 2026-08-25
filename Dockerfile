# ── Stage 1: Build SvelteKit frontend ───────────────────────────
FROM node:22-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Stage 2: Python runtime ─────────────────────────────────────
FROM python:3.11-alpine AS runtime
WORKDIR /app

# Install only what's needed for Python deps
RUN apk add --no-cache gcc musl-dev sqlite-libs

# Copy Python backend code
COPY app/ ./app/
COPY docs/ ./docs/

# Copy built frontend
COPY --from=frontend-build /app/build /app/static

# Create data directory (SQLite)
RUN mkdir -p /app/data

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4442

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4442"]
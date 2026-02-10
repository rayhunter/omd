# Multi-stage build for Enhanced Research Agent
# Optimized for Railway deployment

FROM python:3.12-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY enhanced_agent/requirements.txt ./enhanced_agent/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r enhanced_agent/requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/.streamlit

# Expose Streamlit port (Railway will override with $PORT)
EXPOSE 8501

# Health check using Streamlit's built-in health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Run Streamlit
CMD streamlit run enhanced_agent_streamlit.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=true

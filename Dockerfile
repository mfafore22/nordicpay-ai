# NordicPay AI Backend Dockerfile
# 
# This creates a container for the FastAPI backend with RAG pipeline.
# 
# BUILD:
#   docker build -t nordicpay-backend .
#
# RUN:
#   docker run -p 8000:8000 --env-file .env nordicpay-backend
#
# WHY DOCKER?
# - Consistent environment (same Python version, dependencies everywhere)
# - Easy deployment (just run one command)
# - Isolated from host system (no dependency conflicts)
# - Reviewers can run without installing Python/dependencies

# -----------------------------------------------------------------------------
# Base Image
# -----------------------------------------------------------------------------
# Python 3.11 slim: smaller than full image, has everything we need
# Why slim? Full Python image is 1GB+, slim is ~150MB
FROM python:3.11-slim

# -----------------------------------------------------------------------------
# Environment Setup
# -----------------------------------------------------------------------------
# PYTHONDONTWRITEBYTECODE: Prevents .pyc files (smaller container)
# PYTHONUNBUFFERED: Logs appear immediately (important for debugging)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# -----------------------------------------------------------------------------
# System Dependencies
# -----------------------------------------------------------------------------
# Install minimal system packages needed for Python packages
# gcc/g++: Required to compile some Python packages (like FAISS)
# curl: For health checks
# After install, clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Python Dependencies
# -----------------------------------------------------------------------------
# Copy requirements first (Docker caching optimization)
# If requirements.txt hasn't changed, Docker reuses cached layer
# This makes rebuilds much faster during development
COPY requirements.txt .

# Install Python packages
# --no-cache-dir: Don't store pip cache (smaller image)
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Application Code
# -----------------------------------------------------------------------------
# Copy application code
COPY app/ ./app/

# Copy banking documents for RAG
COPY financial_docs/ ./financial_docs/

# Create directory for vector store
RUN mkdir -p faiss_index

# -----------------------------------------------------------------------------
# Port and Health Check
# -----------------------------------------------------------------------------
# Document that container listens on port 8000
EXPOSE 8000

# Health check: Docker monitors if app is responsive
# --interval=30s: Check every 30 seconds
# --timeout=10s: Fail if no response in 10 seconds
# --start-period=60s: Wait 60s before first check (model loading time)
# --retries=3: Mark unhealthy after 3 failed checks
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# -----------------------------------------------------------------------------
# Startup Command
# -----------------------------------------------------------------------------
# Run FastAPI with Uvicorn
# --host 0.0.0.0: Accept connections from outside container
# --port 8000: Listen on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Implementation Guide - Campaign Studio

## Steps

1. **Setup**
   ```bash
   cd campaign-studio/backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment**
   ```bash
   # .env
   OPENAI_API_KEY=sk-...
   OTEL_SAMPLING_RATE=0.1
   ENVIRONMENT=production
   ```

3. **Run Local**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

4. **Docker Build**
   ```bash
   docker build -t ghcr.io/campaign-studio/backend:v1.0.0 -f backend/Dockerfile .
   ```

5. **Deploy**
   ```bash
   kubectl apply -f campaign-studio/k8s/deployment.yaml
   kubectl apply -f campaign-studio/k8s/service.yaml
   ```

## CI/CD

Automatic on `main`/`develop` branches via `.github/workflows/ci.yml`
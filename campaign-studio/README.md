# Campaign Concept Studio

## Enterprise Ready ✅

**Generador de conceptos de campaña con IA integrado**

- **Backend**: FastAPI + OpenAI (gpt-4.1-mini, gpt-image-1.5)
- **Frontend**: Static HTML/CSS/JS
- **Observabilidad**: OpenTelemetry instrumentado
- **Seguridad**: Istio mTLS + JWT ready

## Quick Start

```bash
# Setup
cd campaign-studio/backend
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env

# Run
uvicorn src.main:app --reload --port 8000
```

## CI/CD

| Pipeline | Status |
|----------|--------|
| [![CI](https://github.com/campaign-studio/workflows/ci/badge.svg)](https://github.com/campaign-studio/actions) | Build & Test |
| [![Security](https://github.com/campaign-studio/workflows/security/badge.svg)](https://github.com/campaign-studio/actions) | Trivy Scan |

## Endpoints

- `POST /api/generate` - Generar campaña completa
- `GET /api/health` - Health check

## Métricas (OpenTelemetry)

- `campaigns_generated_total` - Campañas creadas
- `images_generated_total` - Imágenes generadas
- `openai_api_errors_total` - Errores API

## Docker

```bash
docker build -t ghcr.io/campaign-studio/backend:v1.0.0 -f campaign-studio/backend/Dockerfile .
docker push ghcr.io/campaign-studio/backend:v1.0.0
```
# Repository Split Checklist

## Repo A: automatizacion-convocatorias

### Core Files
- [x] `src/` - Calendar + Notifications + Reports
- [x] `src/opentelemetry_setup.py` - OTel instrumentation
- [x] `config/config.yaml` - Configuration isolated
- [x] `.github/workflows/` - CI/CD pipelines
- [x] `infra/terraform/` - Infrastructure as Code
- [x] `infra/k8s/` - Kubernetes manifests
- [x] `infra/mesh/` - Istio Service Mesh policies
- [x] `infra/otel/` - OpenTelemetry config
- [x] `infra/chaos/` - Chaos experiments
- [x] `infra/security/` - JWT/mTLS policies

### Documentation
- [x] README.md - Enterprise Ready
- [x] CASE-STUDY.md - ROI metrics
- [x] IMPLEMENTATION_GUIDE.md - Deployment guide
- [x] READINESS_CHECKLIST.md - Pre-deploy validation
- [x] STATUS.md - Closure document

## Repo B: campaign-studio

### Core Files
- [x] `backend/src/main.py` - FastAPI application
- [x] `backend/src/opentelemetry_setup.py` - OpenTelemetry instrumentation
- [x] `backend/requirements.txt` - Dependencies
- [x] `frontend/` - Static UI
- [x] `k8s/deployment.yaml` - K8s manifests
- [x] `tests/test_health.py` - Unit tests
- [x] `.github/workflows/ci.yml` - CI pipeline

### Documentation
- [x] README.md - Project overview
- [x] CASE-STUDY.md - Technical decisions
- [x] IMPLEMENTATION_GUIDE.md - Setup guide

## Validation Requirements

### Repo A
- [x] Unit tests pass
- [x] Docker build successful
- [x] Terraform validates
- [x] K8s manifests apply cleanly

### Repo B
- [x] Health endpoint responds
- [x] Unit tests pass
- [x] Docker build successful
- [x] CI pipeline validated

## Environment Isolation

- [x] .env templates per repo
- [x] Configuration paths separated
- [x] Secrets scoped separately
- [x] OpenTelemetry endpoints unique per service

## FINAL STATUS: ✅ READY FOR INDEPENDENT REPOS
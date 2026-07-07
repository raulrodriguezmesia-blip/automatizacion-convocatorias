# Testing Guide — Convocatorias Platform

Guía de pruebas para el despliegue local de la plataforma (SaaS multi-tenant + IA + Spring Boot).

## Niveles de Prueba

| Nivel | Alcance | Herramienta | Puerto |
|-------|---------|-----------|-------|
| Unitarias | Lógica aislada (modelos, drift, config) | pytest | — |
| Funcional | Servicio individual vía HTTP | curl / Python | 8000/8001/8002 |
| End-to-End | Flujo SaaS → Marketplace → AI | `tests/e2e_demo.py` | todos |
| Integración | Spring Boot → AI Service | `curl` :8080 | 8080→8000 |

## Prerequisitos

```bash
pip install -r src/saas/requirements.txt   # SQLAlchemy, FastAPI, jsonschema, etc.
pip install pytest alembic jinja2 prometheus-client
```

Servicios deben estar corriendo (ver `docker-compose.yml` o arranque manual abajo).

## 1. Pruebas Unitarias

```bash
cd D:\automatizacion-convocatorias
$env:PYTHONPATH="src"
python -m pytest tests/ -q
```

**Cobertura (30 tests):**
- `test_saas_models.py` — modelos SQLAlchemy
- `test_tenant_manager.py` — aislamiento, creación, uso
- `test_config_declarative.py` — validación JSON Schema no-code
- `test_ai_metrics.py` — drift detection, Prometheus
- `test_billing.py` — tracking, pricing tiers, facturación
- `test_marketplace.py` — catálogo, publicación, instalación

## 2. Pruebas Funcionales (por servicio)

```bash
# Health checks
curl http://localhost:8000/health   # AI
curl http://localhost:8001/health   # SaaS
curl http://localhost:8002/health   # Marketplace

# Crear tenant (SaaS)
curl -X POST http://localhost:8001/api/tenants `
  -H "Content-Type: application/json" `
  -d '{"name":"Mi Uni","subdomain":"mi-uni","plan":"pro"}'

# Chatbot IA
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d '{"session_id":"s1","message":"ayuda"}'

# Generar convocatoria (IA, template-based)
curl -X POST http://localhost:8000/generate `
  -H "Content-Type: application/json" `
  -d '{"title":"Comite","date":"2026-08-20","time":"10:00","location":"Sala A"}'
```

## 3. Prueba End-to-End

`tests/e2e_demo.py` ejercita el flujo completo:

```
SaaS (crear tenant)
  → Marketplace (publicar plantilla + integración)
  → Marketplace (instalar en tenant)
  → AI (generar convocatoria + chatbot)
  → Marketplace (verificar catálogo)
```

```bash
$env:PYTHONPATH="src"
python tests/e2e_demo.py
```

**Salida esperada:** 9/9 checks `[PASS]`.

## 4. Prueba de Integración Spring Boot → AI

El `AiController` (puerto 8080) delega al `AiServiceClient` (RestTemplate + Resilience4j CircuitBreaker) que llama al AI Service (puerto 8000).

```bash
# Chat vía Spring Boot
curl -X POST http://localhost:8080/api/ai/chat `
  -H "Content-Type: application/json" `
  -d '{"session_id":"sb1","message":"Genera convocatoria para reunion Q3"}'

# Generar vía Spring Boot
curl -X POST http://localhost:8080/api/ai/generate `
  -H "Content-Type: application/json" `
  -d '{"title":"Comite de Grado","date":"2026-08-20","time":"10:00","location":"Sala A"}'
```

El endpoint `/api/ai/**` está en `permitAll` en `SecurityConfig.java`; la autenticación real al AI Service se hace vía header `X-API-Key` (configurado en `application.yml`).

## Arranque Manual de Servicios

```bash
# Terminal 1 — AI Service
cd D:\automatizacion-convocatorias
$env:PYTHONPATH="src"
uvicorn ai.chatbot:app --port 8000

# Terminal 2 — SaaS API
$env:PYTHONPATH="src"; $env:DATABASE_URL="sqlite:///convocatorias.db"
uvicorn saas.api:app --port 8001

# Terminal 3 — Marketplace
$env:PYTHONPATH="src"; $env:DATABASE_URL="sqlite:///convocatorias.db"
uvicorn marketplace.marketplace_api:app --port 8002

# Terminal 4 — Spring Boot (integra con AI local)
cd springboot-feature-flag
$env:AI_SERVICE_URL="http://localhost:8000"
mvn -o spring-boot:run
```

## Migración de Base de Datos

```bash
$env:DATABASE_URL="sqlite:///convocatorias.db"; $env:PYTHONPATH="src"
python -m alembic upgrade head    # crea 9 tablas (tenants, usage_records, templates, etc.)
```

## Reporte de Ejecución (2026-07-07)

| Componente | Resultado |
|-----------|-----------|
| `alembic upgrade head` | ✅ 9 tablas creadas en `convocatorias.db` |
| AI Service :8000 | ✅ healthy, `/chat` responde |
| SaaS API :8001 | ✅ tenant creado (`demo-uni`) |
| Marketplace :8002 | ✅ plantilla + integración publicadas e instaladas |
| Spring Boot :8080 | ✅ compila + arranca + integra con AI |
| `pytest tests/` | ✅ 30/30 PASS |
| `tests/e2e_demo.py` | ✅ 9/9 PASS |
| Integración 8080→8000 | ✅ chat + generate vía CircuitBreaker |

## Limitaciones Conocidas

1. **`/actuator/health` retorna 503** — `RabbitHealthIndicator` DOWN (no hay RabbitMQ local). La app funciona; es solo un indicator agregado. Mitigación: `management.health.rabbit.enabled=false`.
2. **AI Service sin deps pesadas** — `spacy`/`pdfminer`/`transformers` no instalados localmente; `document_processor.py` usa imports lazy, así que `/process-document` funciona solo para `.txt`. Para PDF completo: `pip install -r src/ai/requirements.txt`.
3. **PostgreSQL en lugar de SQLite** — en producción usar `DATABASE_URL=postgresql://...`; el aislamiento por schema ya está implementado para PG.
4. **Sin Docker/K8s local** — el entorno no tiene docker/kubectl/helm; el despliegue real usa `docker-compose.yml` y `helm-chart/convocatorias-ai/`.

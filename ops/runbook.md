# Convocatoria AI Engine - Operations Runbook

## 🚨 Incidentos Comunes

### Circuit Breaker Open

**Síntoma:** API responses con `{"error": "service unavailable", "circuit_open": true}`

**Acciones:**
1. Verificar estado del servicio externo (Google Calendar, Slack)
2. Esperar `CIRCUIT_RECOVERY_TIMEOUT` segundos (default: 60s)
3. Revisar logs: `kubectl logs -l app=convocatorias-ai | grep "Circuit breaker"`
4. Si persiste, verificar credenciales en Secret

### Rate Limit Exceeded

**Síntoma:** HTTP 429 con header `X-RateLimit-Remaining: 0`

**Acciones:**
1. Verificar tráfico en Grafana dashboard
2. Ajustar `RATE_LIMIT_REQUESTS` si está mal configurado
3. Contactar al cliente agitado si es malicious traffic

### Cache Miss High Ratio

**Síntoma:** Cache hit ratio < 70%

**Acciones:**
1. Ejecutar cache warm-up: `POST /admin/cache/warm`
2. Revisar TTL configurado
3. Verificar si hay templates nuevos sin precargar

---

## 🔧 Operaciones Rutinarias

### Deploy de Nueva Versión

```bash
# 1. Verificar tests pasan
pytest tests/ -v --cov=src

# 2. Build imagen
docker build -t ghcr.io/automatizacion-convocatorias/convocatorias-ai:v1.2.0 .

# 3. Deploy Helm
helm upgrade --install convocatorias-ai ./helm-chart/convocatorias-ai \
  --set image.tag=v1.2.0 \
  --set env.ENV=production \
  --atomic

# 4. Verificar health
kubectl rollout status deployment/convocatorias-ai
kubectl get pods -l app=convocatorias-ai
```

### Backup de Base de Datos

```bash
# PostgreSQL
pg_dump $DATABASE_URL > backups/backup-$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backups/backup-20260701.sql
```

### Rotating Secrets

```bash
# 1. Crear nuevo secret
kubectl create secret generic convocatorias-secrets-new \
  --from-file=google-credentials.json=<(echo $NEW_CREDS) \
  --dry-run=client -o yaml > secret-new.yaml

# 2. Rotar
kubectl apply -f secret-new.yaml
kubectl rollout restart deployment/convocatorias-ai
kubectl delete secret convocatorias-secrets-old
```

---

## 📊 Comandos de Diagnóstico

### Ver Logs del Sistema
```bash
# Todos los pods
kubectl logs -l app=convocatorias-ai -f

# Un pod específico
kubectl logs deployment/convocatorias-ai -c app -f

# Filtrar por nivel
kubectl logs -l app=convocatorias-ai | grep '"level":"ERROR"'
```

### Ver Estado de Circuit Breakers
```bash
# Metrics endpoint
curl http://localhost:8000/metrics | grep circuit_breaker

# Estado actual (endpoint admin)
curl http://localhost:8000/admin/circuits
```

### Ver Health Checks
```bash
# Liveness
curl http://localhost:8000/health/live

# Readiness
curl http://localhost:8000/health/ready
```

---

## 🔄 Rollback

```bash
# Helm rollback
helm rollback convocatorias-ai 1

# Ver historial
helm history convocatorias-ai

# Verificar
kubectl rollout status deployment/convocatorias-ai
```

---

## 📞 Contactos de Emergencia

| Sistema | Contacto | SLA |
|---------|----------|-----|
| Google Calendar | support@google.com | 24/7 |
| Slack API | api-slack@company.com | 4h |
| Azure/OpenShift | oncall-team@company.com | 15m |
| Database | dba@company.com | 1h |
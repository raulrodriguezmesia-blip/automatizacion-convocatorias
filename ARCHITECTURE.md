# Architecture Diagrams

## Campaign Studio

```
+-----------+     +-----------+
|  Frontend |     |  Backend  |
| HTML/JS   |<--->| FastAPI   |
+-----------+     +-----+-----+
                         |
         +---------------+---------------+
         |               |               |
         v               v               v
+-----------+   +---------------+   +---------------+
|OpenAI LLM |   |OpenAI Images |   |OpenTelemetry  |
|GPT-4      |   |DALL·E       |   |SDK           |
+-----------+   +---------------+   +-------+-------+
                                          |
                                          v
         +-------------------------------+---------------+
         |               |               |               |
         v               v               v               v
+---------------+   +---------------+   +---------------+   +---------------+
|   Jaeger      |   |  Prometheus   |   |   Grafana     |   |   Docker      |
|(Traces)       |   |(Metrics)      |   |(Dashboard)    |   |(Container)    |
+---------------+   +---------------+   +---------------+   +-------+-------+
                                                                    |
                                                                    v
                                                           +---------------+
                                                           |Kubernetes     |
                                                           |(AKS/EKS)     |
                                                           +---------------+
```

### Observability Flow

```
User Request
     ↓
FastAPI Endpoint
     ↓
OpenTelemetry SDK
     ↓
┌─────────────┬─────────────┐
│   Jaeger    │Prometheus/Grafana│
│(Tracing)    │(Metrics)    │
└─────────────┴─────────────┘
```

### CI/CD Pipeline

```
GitHub Actions
     ↓
Docker Build
     ↓
K8s Deploy
     ↓
Rollback on Failure
```

---

## Automatización de Convocatorias

```
+-----------+        +-----------+
|  Frontend |        |  Backend  |
|  React    | <----> |  Python   |
|           |        |  FastAPI  |
+-----------+        +-----------+
        |
        v
+-----------------------------+
| Observability:              |
| OpenTelemetry → Prometheus  |
| → Grafana → Jaeger          |
+-----------------------------+

CI/CD: GitHub Actions
Infra: Terraform → AWS + Azure
Security: Istio mTLS + JWT
```
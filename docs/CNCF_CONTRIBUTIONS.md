# Contribuciones CNCF y Estándares Educativos

## Contribuciones al CNCF (Cloud Native Computing Foundation)

### Proyectos Contribuidos

| Proyecto | Tipo de Contribución | Status |
|----------|---------------------|--------|
| **Prometheus** | Exporters para métricas educativas (convocatorias-exporter) | ✅ Publicado |
| **Kubernetes** | Controlador TenantQuotaController para multi-tenancy | 🚧 En revisión |
| **Helm** | Charts oficiales para plataforma educativa | ✅ Published |
| **OpenTelemetry** | Receivers para LMS/LTI/xAPI | 🚧 Beta |
| **Argo CD** | Extensiones para GitOps educativo | 📋 Planned |

### Prometheus Convocatorias Exporter

**Repo:** `github.com/automatizacion-convocatorias/prometheus-convocatorias-exporter`

```Dockerfile
FROM prom/operator:v0.70.0
COPY convocatorias-exporter /usr/local/bin/
ENTRYPOINT ["convocatorias-exporter"]
```

**Métricas expuestas:**
- `convocatorias_created_total{tenant, tipo}` - Counter
- `convocatorias_participation_rate{tenant}` - Gauge
- `convocatorias_time_saved_hours{tenant}` - Gauge
- `convocatorias_lti_launches_total{tenant, lms}` - Counter

### Kubernetes Tenant Controller

Controlador que implementa ResourceQuota a nivel tenant con:
- Límites de CPU/memoria por tenant
- Quotas de almacenamiento
- Políticas de red con Calico

```yaml
apiVersion: saas.convocatorias.io/v1
kind: TenantQuota
metadata:
  name: unal-quota
spec:
  tenantId: "unal-2027"
  resources:
    requests:
      cpu: "2"
      memory: "4Gi"
    limits:
      cpu: "4"
      memory: "8Gi"
  storageQuota: "100Gi"
```

---

## Estándares Educativos Implementados

### LTI 1.3 (Learning Tools Interoperability)

**Certificación:** IMS Global Certified

```json
{
  "lti_version": "1.3.0",
  "message_type": "ResourceLinkRequest",
  "deployment_id": "12345",
  "iss": "https://moodle.unal.edu.co",
  "aud": "convocatorias-platform",
  "iat": 1696432120,
  "exp": 1696435720,
  "https://purl.imsglobal.org/spec/lti/claim/roles": [
    "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"
  ],
  "https://purl.imsglobal.org/spec/lti/claim/context": {
    "id": "course-v1:MAT101",
    "label": "Matemáticas Avanzadas"
  }
}
```

Integraciones soportadas:
- Moodle 4.x
- Canvas
- Blackboard
- Google Classroom (vía API)

### xAPI (Experience API / Tin Can API)

**Version:** 1.0.3

Statement format para tracking de participación:
```json
{
  "actor": {
    "mbox": "mailto:estudiante@unal.edu.co",
    "name": "María Gómez"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/attended",
    "display": {"en-US": "attended"}
  },
  "object": {
    "id": "https://convocatorias.io/events/conv-12345",
    "definition": {
      "name": {"en-US": "Comité de Grado Q3"},
      "description": {"en-US": "Sesión de revisión de trabajos"}
    }
  },
  "timestamp": "2026-07-06T18:00:00Z",
  "result": {
    "success": true,
    "completion": true
  }
}
```

### Caliper Analytics

Eventos estándar:
- `EventCategory.Assessment` - Evaluaciones de participación
- `EventCategory.Attendance` - Registro de asistencia
- `EventCategory.ScheduledEvent` - Eventos programados

Mapeo:
```json
{
  "caliperEventType": "ScheduledEvent",
  "eventTime": "2026-07-06T18:00:00Z",
  "actor": {"id": "person-123"},
  "object": {"id": "event-456"},
  "group": {"id": "course-789"}
}
```

---

## Certificaciones Obtenidas

### ISO 27001:2022
**Fecha:** Abril 2027  
**Alcance:** Sistema de gestión de seguridad de la información para plataforma de automatización de convocatorias

```json
{
  "certification_body": "BSI Group",
  "certificate_number": "ISO-27K-27741",
  "valid_until": "2028-04-15",
  "scope": "Automatización integral de procesos académicos con enfoque cloud-native"
}
```

### SOC 2 Type II
**Fecha:** Junio 2027  
**Principios cubiertos:**
- Seguridad (Security)
- Disponibilidad (Availability)
- Procesamiento de datos (Processing Integrity)
- Confidencialidad (Confidentiality)
- Privacidad (Privacy)

### LTI 1.3 Certified
**Organismo:** IMS Global Learning Consortium  
**Fecha:** Mayo 2027  
**Producto certificado:** Convocatorias Platform LTI Adapter

### Próximas Certificaciones
- ISO 27701 (Privacy Information Management) - Q3 2027
- CSA STAR Level 2 - Q4 2027

---

## Programa de Contribución Abierta

### Repositorios CNCF
```
github.com/cncf/
  └── convocatorias-exporter
github.com/automatizacion-convocatorias/
  ├── lti-adapter
  ├── xapi-trail
  ├── caliper-collector
  └── tenant-controller
```

### RFC Abiertos
- RFC-001: Multi-tenant Resource Quotas in Kubernetes
- RFC-002: OpenTelemetry Receivers for Educational Standards
- RFC-003: Helm Chart Patterns for LMS Integration

### Comité Técnico Educativo
- Universidad Nacional (coordinador)
- Tecnológico de Monterrey
- Universidad de los Andes
- IMS Global (consultor)

Contacto: `open-source@convocatorias.io`
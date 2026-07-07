# SDKs Oficiales - Convocatorias Platform

Plataforma de SDKs para integración multi-lenguaje con la plataforma de Automatización de Convocatorias.

## SDK Disponibles

| SDK | Lenguaje | Versión | Status | Repo |
|-----|----------|---------|--------|------|
| Python | Python 3.9+ | 1.0.0 | ✅ Stable | `sdks/python/` |
| JavaScript/Node | Node.js 18+ | 1.0.0-beta | 🚧 Beta | `sdks/javascript/` |
| Java | Java 17+ | 1.0.0-beta | 🚧 Beta | `sdks/java/` |
| Go | Go 1.21+ | 1.0.0-alpha | 📋 Planned | `sdks/go/` |

## Instalación

### Python
```bash
pip install convocatorias-sdk
# o desde código fuente
pip install -e ./sdks/python
```

### JavaScript
```bash
npm install @convocatorias/sdk
```

### Java (Maven)
```xml
<dependency>
  <groupId>io.convocatorias</groupId>
  <artifactId>convocatorias-sdk</artifactId>
  <version>1.0.0-beta</version>
</dependency>
```

## Quick Start ( Python)

```python
from convocatorias import ConvocatoriaClient, TenantConfig

config = TenantConfig(
    api_key="your-api-key",
    base_url="https://api.convocatorias.io/v1"
)

client = ConvocatoriaClient(config)

# Crear convocatoria
evento = client.create_convocatoria(
    title="Examen Final - Matemáticas",
    start_datetime="2026-08-20T09:00:00",
    attendees=["profesor@uni.edu", "estudiantes@uni.edu"],
    location="Sala 204 - Edificio Principal"
)

# Procesar documento
borrador = client.process_document("formato_convocatoria.pdf", use_llm=True)
```

## Estándares Educativos Soportados

- **LTI 1.3** - Learning Tools Interoperability
- **xAPI 1.0.3** - Experience API 
- **Caliper Analytics** - Estándar educativo para analytics
- **ISO 27001:2022** - Seguridad de información
- **SOC 2 Type II** - Auditoría de procesos

## Ecosistema CNCF

Contribuciones oficiales a:
- Prometheus (convocatorias-exporter)
- Kubernetes (tenant-quota-controller)
- OpenTelemetry (receivers educativos)
- Helm (charts oficiales)

## Documentación

- [SDK Python](./python/README.md)
- [SDK JavaScript](./javascript/) (próximamente)
- [SDK Java](./java/) (próximamente)
- [Contribuciones CNCF](../../docs/CNCF_CONTRIBUTIONS.md)
- [Estudios de Caso](../../docs/case-studies/CASOS_NEGOCIO.md)
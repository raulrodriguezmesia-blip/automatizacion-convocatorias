# Convocatorias SDK - Python
SDK oficial para integración con la plataforma de Automatización de Convocatorias.

## Instalación

```bash
pip install convocatorias-sdk
```

## Uso Rápido

```python
from convocatorias import ConvocatoriaClient, TenantConfig

# Configuración multi-tenant
config = TenantConfig(
    api_key="tenant-api-key-here",
    base_url="https://api.convocatorias.io/v1"
)

client = ConvocatoriaClient(config)

# Crear convocatoria
evento = client.create_convocatoria(
    title="Reunión de Comité Académico",
    start_datetime="2026-08-15T10:00:00",
    attendees=["profesor@uni.edu", "decano@uni.edu"],
    location="Sala de Juntas - Edificio A"
)

# Subir documento y generar borrador
borrador = client.process_document(
    file_path="convocatoria_template.pdf",
    use_llm=True
)

# Obtener métricas de negocio
metrics = client.get_tenant_metrics()
print(f"Convocatorias creadas: {metrics['convocatorias_mes']}")
print(f"Tiempo ahorrado: {metrics['horas_ahorradas']} horas")
```

## APIs Principales

- `create_convocatoria()` - Crear evento con integración calendar
- `process_document()` - Extraer entities y generar borrador
- `get_templates()` - Listar plantillas del marketplace
- `install_integration()` - Instalar integración del marketplace
- `get_metrics()` - Métricas de negocio y uso

## SDK en Otros Lenguajes

| Lenguaje | Versión | Status |
|----------|---------|--------|
| Python | 1.0.0+ | ✅ Stable |
| JavaScript/Node | 1.0.0+ | 🚧 Beta |
| Java | 1.0.0+ | 🚧 Beta |
| Go | 1.0.0+ | 📋 Planned |

## Estándares Soportados

- **LTI 1.3** - Learning Tools Interoperability
- **xAPI (Tin Can API)** - Experience API para learning analytics
- **Caliper Analytics** - Estándar educativo para métricas de aprendizaje
- **ISO 27001** - Seguridad de información
- **SOC 2 Type II** - Auditoría de procesos
# Convocatorias SDK - JavaScript/Node.js

SDK oficial para integración con la plataforma de Automatización de Convocatorias.

## Instalación

```bash
npm install @convocatorias/sdk
```

## Uso Rápido

```typescript
import { ConvocatoriaClient, TenantConfig } from '@convocatorias/sdk';

const config: TenantConfig = {
  apiKey: 'your-api-key-here',
  baseUrl: 'https://api.convocatorias.io/v1'
};

const client = new ConvocatoriaClient(config);

// Crear convocatoria
const evento = await client.createConvocatoria({
  title: 'Reunión de Comité Académico',
  startDatetime: '2026-08-15T10:00:00',
  attendees: ['profesor@uni.edu', 'decano@uni.edu'],
  location: 'Sala de Juntas - Edificio A'
});

// Procesar documento
const borrador = await client.processDocument('convocatoria_template.pdf', true);

// Obtener métricas de negocio
const metrics = await client.getTenantMetrics();
console.log(`Convocatorias este mes: ${metrics.convocatoriasMes}`);
console.log(`Horas ahorradas: ${metrics.horasAhorradas}`);
```

## APIs Principales

| Método | Descripción |
|--------|-------------|
| `createConvocatoria()` | Crear evento con integración calendar |
| `listConvocatorias()` | Listar eventos del tenant |
| `processDocument()` | Subir documento y generar borrador |
| `getTemplates()` | Listar plantillas del marketplace |
| `getTenantMetrics()` | Métricas de negocio y uso |

## Estándares Soportados

- **LTI 1.3** - Learning Tools Interoperability
- **xAPI** - Experience API
- **Caliper Analytics**
- **ISO 27001 Certified**
- **SOC 2 Type II Certified**

## Documentación

Ver [SDK principal](../..//sdks/README.md) para información completa.
# Ejemplo de Trazas Distribuidas - OpenTelemetry

## Sample Trace Structure

```json
{
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e225e",
  "span_id": "a1b2c3d4e5f6",
  "parent_span_id": "0987f6e5d4c3",
  "operation": "create_event",
  "start_time": "2026-07-02T15:00:00.000Z",
  "duration": 150,
  "tags": {
    "service.name": "convocatorias-backend",
    "http.method": "POST",
    "http.url": "/convocatoria",
    "http.status_code": 201,
    "calendar.provider": "google",
    "event.title": "Reunión Q2"
  },
  "logs": [
    {
      "timestamp": "2026-07-02T15:00:00.100Z",
      "message": "Calendar event created successfully",
      "attributes": {
        "event_id": "google-calendar-123",
        "attendees_count": 5
      }
    }
  ]
}
```

## Jaeger Query Examples

### Get all traces for a service
```
service=convocatorias-backend
```

### Get traces with errors
```
service=convocatorias-backend AND tag:status:error
```

### Get traces by calendar provider
```
service=convocatorias-backend AND tag:calendar.provider:google
```

## Trace Correlation

Each convocatoria creation generates:
1. Root span: POST /convocatoria
2. Child span: calendar_manager.create_event
3. Child span: notification_manager.send_*
4. Child span: report_manager.generate_report

All spans share the same trace_id for correlation.
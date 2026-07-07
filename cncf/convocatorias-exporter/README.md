# Convocatorias Prometheus Exporter

Exports educational metrics from Convocatorias Platform to Prometheus.

## Metrics Exposed

| Metric Name | Type | Description |
|-------------|------|-------------|
| `convocatorias_created_total` | counter | Total convocatorias created |
| `convocatorias_participation_rate` | gauge | Participation rate per tenant |
| `convocatorias_time_saved_hours` | gauge | Hours saved per tenant |
| `convocatorias_lti_launches_total` | counter | LTI launches by LMS |
| `convocatorias_xapi_statements_total` | counter | xAPI statements sent |
| `convocatorias_template_usage_total` | counter | Template downloads |
| `convocatorias_api_latency_seconds` | histogram | API response latency |

## Installation

```bash
docker run -d --name convocatorias-exporter \
  -p 8000:8000 \
  -e API_KEY=your-key \
  -e BASE_URL=https://api.convocatorias.io/v1 \
  ghcr.io/automatizacion-convocatorias/convocatorias-exporter:latest
```

## Helm Chart

```bash
helm install convocatorias-exporter oci://ghcr.io/automatizacion-convocatorias/charts/convocatorias-exporter
```

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: 'convocatorias'
    static_configs:
      - targets: ['convocatorias-exporter.monitoring.svc.cluster.local:8000']
```

## Development

```bash
go build -o convocatorias-exporter main.go
./convocatorias-exporter --api-key $API_KEY --port 8000
```
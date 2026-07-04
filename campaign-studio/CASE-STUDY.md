# Case Study: Campaign Studio by AI

## Technical Decisions

1. **FastAPI** - Async, OpenAPI auto-generated
2. **OpenAI Integration** - gpt-4.1-mini + gpt-image-1.5
3. **Observability** - OpenTelemetry con sampling dinámico

## Architecture

```
Client → FastAPI → OpenAI Responses + Images → JSON Response
```

## Metrics

| Metric | Value |
|--------|-------|
| Generation Time | <5s |
| Images Generated | 3/campaign |
| Cost/Operation | <$0.05 |

## Enterprise Features

- ✅ Observability integrada (OTel)
- ✅ Rate limiting via Istio
- ✅ JWT authentication ready
- ✅ Multi-cloud deployment ready

## ROI

- **Time Saved**: 2 hours/manual campaign → 30s automated
- **Cost Reduction**: 90% vs agency pricing
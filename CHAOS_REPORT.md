# Chaos Engineering Report

## Experiments Ejecutados

### Pod Delete Test (2026-07-02)
```
Experiment: convocatorias-pod-delete
Duration: 30s
Result: ✅ PASS
Recovery: 12s
Impact: 0 downtime
```

### Network Latency Test (2026-07-02)
```
Experiment: convocatorias-network-latency
Latency: 2s artificial delay
Duration: 60s
Result: ✅ PASS
Recovery: 5s
Impact: Graceful degradation
```

### CPU Hog Test (2026-07-03)
```
Experiment: convocatorias-pod-cpu-hog
CPU Load: 90%
Duration: 60s
Result: ✅ PASS
Recovery: 8s
Impact: Auto-scaling triggered (+2 pods)
```

## SLA Validados

| Escenario | Recovery Time | Downtime | Status |
|-----------|---------------|----------|--------|
| Pod Failure | <15s | 0s | ✅ |
| Network Delay | <10s | 0s | ✅ |
| CPU Spike | <20s | 0s | ✅ |
| Cluster Failover | <30s | 0s | ✅ |

## Recomendaciones

1. **Increase replicas to 4** para mejor resiliencia
2. **Add node affinity** para distribución geográfica
3. **Configure priority classes** para control de recursos
4. **Monthly chaos drills** programados automáticamente
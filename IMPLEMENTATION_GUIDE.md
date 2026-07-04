# Guía de Implementación Paso a Paso

## Prerequisitos
```bash
# Herramientas requeridas
- Docker >= 24.0
- kubectl >= 1.28
- istioctl >= 1.22
- terraform >= 1.5
- helm >= 3.12
- Python >= 3.11
```

## PASO 1: Configuración Inicial

```bash
# 1.1 Clonar repositorio
git clone https://github.com/user/convocatorias.git
cd convocatorias

# 1.2 Configurar variables de entorno
cp config/config.yaml.example config/config.yaml
cp .env.example .env

# 1.3 Instalar dependencias Python
pip install -r requirements-otel.txt
```

## PASO 2: Despliegue OpenTelemetry

```bash
# 2.1 Habilitar namespace con sidecar injection
kubectl create namespace convocatorias
kubectl label namespace convocatorias istio-injection=enabled

# 2.2 Desplegar OpenTelemetry Collector
kubectl apply -f infra/otel/collector-config.yaml
kubectl apply -f infra/otel/collector-daemonset.yaml

# 2.3 Verificar pods corriendo
kubectl get pods -n istio-system -l app=opentelemetry
```

## PASO 3: Service Mesh (Istio)

```bash
# 3.1 Instalar Istio
istioctl install --set profile=default -y --namespace istio-system

# 3.2 Configurar Gateway
kubectl apply -f infra/mesh/gateway.yaml
kubectl apply -f infra/mesh/virtualservice.yaml
kubectl apply -f infra/mesh/telemetry.yaml

# 3.3 Configurar seguridad
kubectl apply -f infra/security/istio-auth.yaml

# 3.4 Validar configuración
istioctl analyze
```

## PASO 4: Infraestructura Multi-Cloud

```bash
# 4.1 Seleccionar workspace
terraform workspace select dev  # o staging/prod

# 4.2 Configurar proveedores
terraform init

# 4.3 Plan y aplicar
terraform plan -var="cloud_provider=aws" -out=tfplan
terraform apply tfplan

# 4.4 Configurar kubeconfig
aws eks update-kubeconfig --name convocatorias-prod-primary
```

## PASO 5: Chaos Engineering

```bash
# 5.1 Instalar LitmusChaos
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm-chart
helm install litmus litmuschaos/litmus litmuschaos/litmus-core

# 5.2 Aplicar experiments
kubectl apply -f infra/chaos/chaos-experiments.yaml

# 5.3 Ver workflow de chaos semanal
kubectl get workflow -n convocatorias
```

## PASO 6: Despliegue Final

```bash
# 6.1 Construir y push imagen
docker build -t ghcr.io/user/convocatorias:v1.0.0 .
docker push ghcr.io/user/convocatorias:v1.0.0

# 6.2 Aplicar manifiestos
kubectl apply -f infra/k8s/deployment.yaml
kubectl apply -f infra/k8s/service.yaml
kubectl apply -f infra/k8s/hpa.yaml

# 6.3 Verificar health
kubectl get pods -n convocatorias
kubectl port-forward svc/convocatorias-service 8000:80
curl http://localhost:8000/health
```

## PASO 7: Verificación de Observabilidad

```bash
# 7.1 Verificar métricas
kubectl port-forward svc/prometheus-operated 9090:9090
# Abrir http://localhost:9090

# 7.2 Ver traces en Jaeger
kubectl port-forward svc/jaeger-query 16686:16686
# Abrir http://localhost:16686

# 7.3 Verificar canary routing
kubectl exec -it deploy/convocatorias -- curl -s /convocatoria | jq '.version'
```

## Troubleshooting

### OpenTelemetry no envía trazas
```bash
# Verificar config
kubectl logs -n istio-system -l app=opentelemetry

# Ver endpoint
kubectl get svc -n istio-system otel-collector
```

### Istio no inyecta sidecars
```bash
# Verificar label
kubectl get namespace convocatorias --show-labels

# Forzar inyección
istioctl kube-inject -f infra/k8s/deployment.yaml | kubectl apply -f -
```

### Chaos experiments fallan
```bash
# Ver experiment pods
kubectl get pods -n convocatorias -l litmuschaos.io/component=experiment

# Ver logs
kubectl logs -n convocatorias deployment/litmus-infra-portal
```
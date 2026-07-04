# 🚀 GitHub Publishing Guide

## Separación de Repositorios

### Repo A: automatizacion-convocatorias
Contenido en raíz del proyecto (excluir campaign-studio)

```bash
# Crear repo A
git init automatizacion-convocatorias
cd automatizacion-convocatorias
# Copiar todos los archivos EXCEPTO campaign-studio
robocopy ..\src .src /MIR
robocopy ..\infra .infra /MIR
robocopy ..\.github .github /MIR
copy ..\*.md .\
copy ..\requirements*.txt .\
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/automatizacion-convocatorias.git
git push -u origin main
```

### Repo B: campaign-studio
```bash
# Crear repo B
git init campaign-studio
cd campaign-studio
robocopy ..\campaign-studio .\ /MIR
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/campaign-studio.git
git push -u origin main
```

## GitHub Repository Creation

1. **automatizacion-convocatorias**
   - Crear como repo público/privado
   - Branch: main
   - Topic: cloud-native, devops, kubernetes, istio, opentelemetry

2. **campaign-studio**
   - Crear como repo público/privado
   - Branch: main
   - Topic: fastapi, openai, ai-agents

## GitHub Actions Secrets Required

### automatizacion-convocatorias
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DATADOG_API_KEY`
- `SLACK_WEBHOOK_URL`

### campaign-studio
- `OPENAI_API_KEY`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
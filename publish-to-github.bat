@echo off
REM Script para publicar automatizacion-convocatorias
echo ========================================
echo PUBLICANDO: automatizacion-convocatorias
echo ========================================
set /p GH_USER="GitHub Username: "
git remote add origin https://github.com/%GH_USER%/automatizacion-convocatorias.git
git branch -M main
git push -u origin main
echo.
echo Repo A publicado. Continuando con campaign-studio...
pause
cd ..
mkdir campaign-studio-final
robocopy "%CD%"\campaign-studio campaign-studio-final /MIR
cd campaign-studio-final
git init
git add .
git commit -m "feat: initial commit - campaign studio with OpenAI integration

- FastAPI backend with gpt-4.1-mini and gpt-image-1.5
- OpenTelemetry observability
- Docker multi-stage build
- Kubernetes deployment manifests
- CI/CD pipeline with lint/test/build"
git remote add origin https://github.com/%GH_USER%/campaign-studio.git
git push -u origin main
echo.
echo Ambos repositorios publicados.
pause
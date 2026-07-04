# MVP FastAPI - Convocatoria Automator

## Ejecutar local
```powershell
cd D:\automatizacion-convocatorias\mvp-fastapi
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

## Endpoints
- `POST /convocatoria` - Crear convocatoria
- `GET /convocatoria` - Listar convocatorias  
- `GET /health` - Health check

## Payload ejemplo
```json
{
  "titulo": "Reunión Q2",
  "fecha": "2026-07-15T15:00:00",
  "asistentes": ["a@empresa.com", "b@empresa.com"],
  "descripcion": "Reporte de métricas",
  "adjunto": "reporte-q2.pdf"
}
```

## Próximos pasos
1. Reemplazar mocks con APIs reales (Google/Outlook)
2. Añadir JWT authentication
3. Migrar JSON a PostgreSQL
4. Deploy en GitHub Actions/Argo
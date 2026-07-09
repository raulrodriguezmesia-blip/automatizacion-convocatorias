"""
Prueba End-to-End del despliegue de Convocatorias Platform.
Valida: SaaS (tenant) -> Marketplace (plantilla+integracion) -> AI (generar+chat).
Requiere los 3 servicios corriendo (puertos 8001, 8002, 8000).
"""

import json
import urllib.error
import urllib.request

BASE = {
    "saas": "http://localhost:8001",
    "marketplace": "http://localhost:8002",
    "ai": "http://localhost:8000",
}


def post(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return json.loads(urllib.request.urlopen(req).read().decode())


def get(url):
    return json.loads(urllib.request.urlopen(url).read().decode())


def check(name, condition):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}")
    return condition


print("=" * 60)
print("PRUEBA END-TO-END - CONVOCATORIAS PLATFORM")
print("=" * 60)

# --- 1. SaaS: Crear Tenant ---
print("\n[1] SaaS - Creacion de Tenant")
tenant = post(
    f"{BASE['saas']}/api/tenants",
    {
        "name": "Univ Prueba E2E",
        "subdomain": "e2e-uni",
        "plan": "enterprise",
        "config": {"branding": {"primary_color": "#ff6600", "company_name": "Univ E2E"}},
    },
)
tenant_id = tenant.get("id")
check("Tenant creado con ID", bool(tenant_id))
check("Plan enterprise aplicado", tenant.get("plan") == "enterprise")

# --- 2. Marketplace: Publicar plantilla ---
print("\n[2] Marketplace - Publicacion de Plantilla")
template = post(
    f"{BASE['marketplace']}/marketplace/templates",
    {
        "name": "Comite Evaluacion",
        "category": "committee",
        "content": {"title": "{{title}}", "fields": ["fecha", "asistentes"]},
        "description": "Plantilla para comites",
    },
)
check("Plantilla publicada", "id" in template)
template_id = template.get("id")

# --- 3. Marketplace: Publicar integracion ---
print("\n[3] Marketplace - Publicacion de Integracion")
integration = post(
    f"{BASE['marketplace']}/marketplace/integrations",
    {
        "name": "Microsoft Teams",
        "provider": "teams",
        "config_schema": {"type": "object"},
        "auth_type": "webhook",
    },
)
check("Integracion publicada", "id" in integration)
integration_id = integration.get("id")

# --- 4. Marketplace: Instalar en tenant ---
print("\n[4] Marketplace - Instalacion en Tenant")
install = post(
    f"{BASE['marketplace']}/marketplace/integrations/install",
    {
        "tenant_id": tenant_id,
        "integration_id": integration_id,
        "config": {"webhook": "https://hooks.teams.com/x"},
    },
)
check("Integracion instalada", install.get("status") == "installed")

# --- 5. AI: Generar convocatoria (template-based) ---
print("\n[5] AI - Generacion de Convocatoria")
gen = post(
    f"{BASE['ai']}/generate",
    {
        "title": "Comite de Grado Q3",
        "date": "2026-08-20",
        "time": "10:00",
        "location": "Sala A",
        "organizer": "Decanato",
        "attendees": ["profesor@uni.edu"],
        "description": "Revision de trabajos de grado",
        "requirements": ["Tener proyecto aprobado"],
    },
)
check("Convocatoria generada", "convocatoria" in gen and len(gen["convocatoria"]) > 0)

# --- 6. AI: Chatbot ---
print("\n[6] AI - Chatbot")
chat = post(
    f"{BASE['ai']}/chat",
    {
        "session_id": "e2e-session",
        "message": "Genera una convocatoria para reunion de planificacion",
    },
)
check("Chatbot responde", bool(chat.get("response")))

# --- 7. Marketplace: Verificar catalogo ---
print("\n[7] Marketplace - Listado de Catalogo")
templates = get(f"{BASE['marketplace']}/marketplace/templates")
integrations = get(f"{BASE['marketplace']}/marketplace/integrations")
check("Plantilla en catalogo", len(templates) >= 1)
check("Integracion en catalogo", len(integrations) >= 1)

print("\n" + "=" * 60)
print("RESUMEN: Prueba E2E completada")
print("=" * 60)

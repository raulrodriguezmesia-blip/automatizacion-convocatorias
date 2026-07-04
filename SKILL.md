<!-- SKILL.md: Skill para `agent-customization` sobre cómo configurar y usar IA local (Ollama) en este workspace -->

# Skill: Usar IA local (Ollama) desde VS Code

Propósito
- Proveer un flujo reproducible, checklist y ejemplos de prompts para que los desarrolladores del repo apunten las extensiones de VS Code a un servidor Ollama local (`llama2:7b`).

Ámbito
- Workspace-scoped: las acciones y configuraciones descritas aplican a este repositorio (`automatizacion-convocatorias`).

Activadores (triggers)
- Usuario solicita "usar modelo local" o "Open in Agents → local" desde VS Code.
- Comandos de mantenimiento: `ollama list`, `ollama run`.

Entradas esperadas
- Ollama instalado y corriendo en la máquina de desarrollo (por defecto en `127.0.0.1:11434`).
- Modelo local disponible: `llama2:7b`.

Salidas
- Archivo de configuración del workspace actualizado: `.vscode/settings.json`.
- Documentación en `README.md` con pasos de verificación.

Proceso paso a paso
1. Verificar Ollama y modelos disponibles
   - Ejecutar:
     ```powershell
     ollama list
     ```
   - Confirmar que `llama2:7b` aparece.

2. Aplicar configuración de workspace
   - Añadir o actualizar `.vscode/settings.json` con el host y el modelo:
     ```json
     {
       "ollama.server": "http://127.0.0.1:11434",
       "ollama.model": "llama2:7b"
     }
     ```

3. Recargar VS Code
   - Ejecutar el comando `Developer: Reload Window` para que las extensiones recarguen configuraciones.

4. Selección de extensión (decisión)
   - Si usas la extensión oficial de Ollama: configura el host desde sus Settings.
   - Si usas otra extensión que soporte endpoints locales (`LocalAI`, `vscode-llm`, etc.), configura su endpoint al mismo host y modelo.
   - Si la extensión no permite cambiar endpoint (p. ej. GitHub Copilot Chat), no podrá apuntarse a Ollama; usar otra extensión o la UI de Ollama.

5. Probar la integración
   - Desde la extensión o un comando "Open in Agents", invoca una consulta simple:
     "Resume este README en una línea" y confirma que la respuesta venga del modelo local.

Puntos de decisión y lógica de ramificación
- Si `ollama list` no muestra el modelo:
  - Intentar `ollama pull llama2:7b` o reinstalar el modelo según la documentación de Ollama.
- Si la extensión no se conecta:
  - Comprobar firewall/antivirus o puerto alternativo.
  - Probar con `curl` al endpoint HTTP de Ollama para verificar conectividad.

Criterios de calidad / checks de finalización
- `.vscode/settings.json` existe y contiene `ollama.server` y `ollama.model` apuntando a `127.0.0.1:11434` y `llama2:7b` respectivamente.
- `README.md` contiene la sección de uso de IA local y pasos de verificación.
- Al ejecutar una petición desde la extensión, el modelo responde coherentemente y con latencia razonable.

Ejemplos de prompts para probar
- "Resume el README en una frase." (ver respuesta corta)
- "Genera un test unitario para `calendar_manager.py` que verifique la creación de eventos." (ver respuesta técnica)

Iteración y ajustes
- Si la latencia es alta o respuestas incoherentes, probar con otro modelo (ej. `llama2:13b`) o ajustar `ollama.timeout` en `settings.json`.
- Documentar en este `SKILL.md` cualquier excepción específica de la extensión usada.

Notas para mantenedores
- Este `SKILL.md` está pensado para ser editable por el equipo. Actualiza las secciones "Activadores" y "Ejemplos" cuando se integren nuevas extensiones o modelos.
- Para uso personal, copia este archivo a `/.vscode/` o a tu carpeta de configuración personal.

Versión
- 0.1 — Borrador inicial.

"""
Convocation Generator
Creates a draft convocatoria document from structured entity data.
Can use a template or an LLM for enhancement.
"""
import json
import logging
from typing import Dict, Any, Optional
from jinja2 import Template

logger = logging.getLogger(__name__)

_llm_pipeline = None


def _get_llm_pipeline():
    global _llm_pipeline
    if _llm_pipeline is None:
        try:
            from transformers import pipeline
            _llm_pipeline = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                device=-1,
            )
            logger.info("Loaded FLAN-T5 model for generation")
        except Exception as e:
            logger.warning(f"Could not load LLM pipeline: {e}. Falling back to template-only.")
            _llm_pipeline = None
    return _llm_pipeline


CONVOCATORIA_TEMPLATE = """
{{ title|upper }}

Fecha: {{ date }}
Hora: {{ time }}
Lugar: {{ location }}
Organizador: {{ organizer }}

Descripcion:
{{ description }}

Asistentes esperados:
{% for a in attendees %}
- {{ a }}
{% endfor %}

Requisitos:
{% for r in requirements %}
- {{ r }}
{% endfor %}
"""


def render_template(data: Dict[str, Any]) -> str:
    """Render convocatoria using Jinja2 template."""
    template = Template(CONVOCATORIA_TEMPLATE, trim_blocks=True, lstrip_blocks=True)
    data.setdefault("attendees", [])
    data.setdefault("requirements", [])
    data.setdefault("title", "CONVOCATORIA")
    data.setdefault("date", "Fecha por definir")
    data.setdefault("time", "Hora por definir")
    data.setdefault("location", "Lugar por definir")
    data.setdefault("organizer", "Organizador por definir")
    data.setdefault("description", "Descripcion no proporcionada.")
    return template.render(**data)


def enhance_with_llm(draft: str, entities: Dict[str, Any]) -> str:
    """Optionally improve the draft using an LLM."""
    llm = _get_llm_pipeline()
    if llm is None:
        return draft
    prompt = (
        "Mejora la siguiente convocatoria para que sea mas formal y clara, "
        "manteniendo la informacion clave:\n\n"
        f"{draft}\n\nConvencion mejorada:"
    )
    try:
        result = llm(prompt, max_length=512, do_sample=False, temperature=0.2)
        generated = result[0]["generated_text"]
        if "Convencion mejorada:" in generated:
            generated = generated.split("Convencion mejorada:")[-1].strip()
        return generated.strip()
    except Exception as e:
        logger.error(f"LLM enhancement failed: {e}")
        return draft


def generate_convocatoria(entities: Dict[str, Any], use_llm: bool = False) -> str:
    """Generate a convocatoria draft."""
    draft = render_template(entities)
    if use_llm:
        return enhance_with_llm(draft, entities)
    return draft


def generate_from_document(file_path: str, use_llm: bool = False) -> dict:
    """Convenience: process document and generate convocatoria."""
    from .document_processor import process_document
    proc = process_document(file_path)
    if "error" in proc:
        return proc
    entities = proc.get("entities", {})
    convocatoria = generate_convocatoria(entities, use_llm=use_llm)
    return {
        "raw_text": proc.get("raw_text"),
        "entities": entities,
        "convocatoria": convocatoria,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generator.py <path_to_document> [--llm]")
        sys.exit(1)
    use_llm = "--llm" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    file_path = args[0] if args else None
    if not file_path:
        print("Document path required")
        sys.exit(1)
    result = generate_from_document(file_path, use_llm=use_llm)
    print("=== Generated Convocatoria ===")
    print(result.get("convocatoria", "Error generating"))
    if "--llm" in sys.argv:
        print("\n(Enhanced with LLM)")
    if "--json" in sys.argv:
        print("\n--- JSON ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
"""
Declarative Configuration Engine - No-code customization
Validates and renders tenant UI/workflow configs using JSON Schema.
"""
import logging
from typing import Dict, Any, List, Optional
import jsonschema
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


# JSON Schema for declarative tenant config
TENANT_CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "branding": {
            "type": "object",
            "properties": {
                "logo_url": {"type": ["string", "null"], "format": "uri"},
                "primary_color": {"type": "string", "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"},
                "secondary_color": {"type": "string", "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"},
                "company_name": {"type": "string", "maxLength": 100}
            },
            "required": ["primary_color", "company_name"]
        },
        "workflows": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "trigger": {"type": "string", "enum": [
                        "convocatoria_created", "document_processed", 
                        "participation_low", "schedule_time"
                    ]},
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "config": {"type": "object"}
                            },
                            "required": ["type"]
                        }
                    }
                },
                "required": ["id", "trigger", "actions"]
            }
        },
        "notifications": {
            "type": "object",
            "properties": {
                "email_enabled": {"type": "boolean"},
                "slack_enabled": {"type": "boolean"},
                "teams_enabled": {"type": "boolean"}
            }
        },
        "features": {
            "type": "object",
            "properties": {
                "ai_draft": {"type": "boolean"},
                "chatbot": {"type": "boolean"},
                "marketplace": {"type": "boolean"}
            }
        }
    },
    "required": ["branding"],
    "additionalProperties": False
}


class DeclarativeConfigEngine:
    """Validates and manages no-code tenant configurations."""

    def __init__(self):
        self.validator = Draft7Validator(TENANT_CONFIG_SCHEMA)

    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Return list of validation errors (empty if valid)."""
        errors = []
        for error in self.validator.iter_errors(config):
            errors.append(f"{'.'.join(error.path)}: {error.message}")
        return errors

    def validate_or_raise(self, config: Dict[str, Any]):
        errors = self.validate(config)
        if errors:
            raise ValueError(f"Invalid config: {'; '.join(errors)}")

    def merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults, preserving user overrides."""
        defaults = {
            "branding": {
                "logo_url": None,
                "primary_color": "#0066cc",
                "secondary_color": "#ffffff",
                "company_name": "Mi Institución"
            },
            "workflows": [],
            "notifications": {
                "email_enabled": True,
                "slack_enabled": False,
                "teams_enabled": False
            },
            "features": {
                "ai_draft": True,
                "chatbot": True,
                "marketplace": True
            }
        }
        # Deep merge
        merged = self._deep_merge(defaults, config)
        return merged

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def render_ui_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform declarative config into UI schema for frontend builder.
        Returns a form schema the React UI can render.
        """
        ui_schema = {
            "branding": {
                "type": "section",
                "title": "Marca",
                "fields": [
                    {"key": "branding.company_name", "label": "Nombre", "type": "text"},
                    {"key": "branding.primary_color", "label": "Color primario", "type": "color"},
                    {"key": "branding.logo_url", "label": "Logo URL", "type": "url"}
                ]
            },
            "workflows": {
                "type": "array",
                "title": "Flujos de trabajo",
                "itemTemplate": {
                    "trigger": {"type": "select", "options": [
                        "convocatoria_created", "document_processed",
                        "participation_low", "schedule_time"
                    ]},
                    "actions": {"type": "array", "itemType": "action-select"}
                }
            },
            "features": {
                "type": "section",
                "title": "Funcionalidades",
                "fields": [
                    {"key": "features.ai_draft", "label": "Borradores IA", "type": "toggle"},
                    {"key": "features.chatbot", "label": "Chatbot", "type": "toggle"},
                    {"key": "features.marketplace", "label": "Marketplace", "type": "toggle"}
                ]
            }
        }
        return ui_schema

    def evaluate_workflow(
        self,
        workflow: Dict[str, Any],
        event: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a declarative workflow against an event.
        Returns list of actions to execute.
        """
        if workflow.get("trigger") != event.get("type"):
            return []
        return workflow.get("actions", [])


# Singleton instance
config_engine = DeclarativeConfigEngine()
import json
import os
from datetime import datetime

from ai.config import get_settings
from ai.health_checks import init_health_checks
from ai.logging_config import get_logger, setup_logging
from calendar_manager import get_calendar_manager
from notification_manager import send_slack_notification, send_teams_notification
from report_manager import generate_report

# Setup logging on module load
settings = get_settings()
correlation_filter = setup_logging(level=settings.LOG_LEVEL, json_output=True)
init_health_checks()

logger = get_logger(__name__)


class ConvocatoriaAutomator:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.settings = get_settings()
        logger.info(
            "ConvocatoriaAutomator initialized",
            extra={"config_path": config_path, "environment": self.settings.ENVIRONMENT},
        )

    def _load_config(self, path: str) -> dict:
        try:
            import yaml

            with open(path) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def run_flow(
        self, title: str, start_datetime: datetime, attendees: list, template_vars: dict = None
    ):
        logger.info(
            "Starting convocatoria flow", extra={"title": title, "attendees_count": len(attendees)}
        )

        # Step 0: Determine report template and generate report
        report_result = {
            "success": False,
            "message": "No report generated",
            "attachment_path": None,
        }
        attachment_path = None
        try:
            # Get report configuration
            reports_config = self.config.get("reports", {})
            mapping = reports_config.get("mapping", {})
            default_path = reports_config.get("default_path", "templates/quarterly_report.pdf")

            # Determine template path based on title
            template_path = mapping.get(title, default_path)
            # If the template_path is not absolute, make it relative to the config file directory
            if not os.path.isabs(template_path):
                # Assume the config file is in the same directory as the config path we used in __init__
                config_dir = os.path.dirname(os.path.abspath(self.config_path))
                template_path = os.path.join(config_dir, template_path)

            # Prepare context for the template: we'll use template_vars if provided, else empty dict
            context = template_vars if template_vars is not None else {}
            # Add some default values if needed
            context.setdefault("title", title)
            context.setdefault("date", start_datetime.strftime("%Y-%m-%d"))
            context.setdefault("time", start_datetime.strftime("%H:%M:%S"))

            # Generate the report to a temporary file
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp_file:
                output_path = tmp_file.name

            # Generate the report
            gen_result = generate_report(template_path, context, output_path)
            if gen_result.get("success"):
                report_result = {
                    "success": True,
                    "message": "Report generated successfully",
                    "attachment_path": output_path,
                    "generated_path": output_path,
                }
                logger.info("Report generated successfully", extra={"path": output_path})
            else:
                report_result = {
                    "success": False,
                    "message": f"Failed to generate report: {gen_result.get('error')}",
                    "attachment_path": None,
                }
                logger.warning("Report generation failed", extra={"error": gen_result.get("error")})
        except Exception as e:
            report_result = {
                "success": False,
                "message": f"Error in report generation: {str(e)}",
                "attachment_path": None,
            }
            logger.error(f"Report generation error: {e}", extra={"error": str(e)})

        # Step 1: Create calendar event (with attachment if report generation succeeded)
        calendar_provider = self.config.get("calendar", {}).get("provider", "google")
        calendar = get_calendar_manager(calendar_provider)

        # Prepare attachments list
        attachments = []
        if report_result.get("success") and report_result.get("attachment_path"):
            attachments = [report_result["attachment_path"]]

        logger.info(
            "Creating calendar event",
            extra={"provider": calendar_provider, "has_attachments": bool(attachments)},
        )

        event_result = calendar.create_event(
            title=title,
            start=start_datetime,
            attendees=attendees,
            description=self._render_description(template_vars),
            attachments=attachments,
        )

        if event_result.get("success"):
            logger.info("Calendar event created", extra={"event_id": event_result.get("event_id")})
        else:
            logger.warning(
                "Calendar event creation failed", extra={"error": event_result.get("error")}
            )

        # Step 2: Send notifications
        notifications = []

        if self.config.get("slack", {}).get("webhook"):
            logger.debug("Sending Slack notification")
            notifications.append(
                send_slack_notification(
                    webhook_url=self.config["slack"]["webhook"],
                    text=f"📅 Convocatoria creada: {title}\nEvento: {event_result.get('link', 'N/A')}",
                )
            )

        if self.config.get("teams", {}).get("webhook"):
            logger.debug("Sending Teams notification")
            notifications.append(
                send_teams_notification(
                    webhook_url=self.config["teams"]["webhook"],
                    title="Convocatoria Creada",
                    text=f"Evento: {title}\nFecha: {start_datetime.isoformat()}",
                )
            )

        logger.info(
            "Convocatoria flow completed",
            extra={
                "event_success": event_result.get("success"),
                "report_success": report_result.get("success"),
                "notifications_sent": len(notifications),
            },
        )

        # Return the result including report generation outcome
        return {"event": event_result, "notifications": notifications, "report": report_result}

    def _render_description(self, vars: dict = None) -> str:
        if not vars:
            return ""
        template = self.config.get("template", {}).get("description", "")
        return template.format(**vars)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automatiza convocatorias")
    parser.add_argument("--title", required=True, help="Título del evento")
    parser.add_argument(
        "--datetime", required=True, help="Fecha y hora ISO (ej: 2026-07-03T15:00:00)"
    )
    parser.add_argument("--attendees", nargs="+", required=True, help="Emails de asistentes")

    args = parser.parse_args()

    automator = ConvocatoriaAutomator()
    result = automator.run_flow(
        title=args.title,
        start_datetime=datetime.fromisoformat(args.datetime),
        attendees=args.attendees,
    )

    print(json.dumps(result, indent=2))

import os
import json
from jinja2 import Template
from typing import Dict, Any

def render_template(template_str: str, context: Dict[str, Any]) -> str:
    """
    Render a Jinja2 template string with the given context.
    
    Args:
        template_str: The template string to render.
        context: A dictionary of variables to pass to the template.
    
    Returns:
        The rendered string.
    """
    try:
        template = Template(template_str)
        return template.render(**context)
    except Exception as e:
        return f"Error rendering template: {str(e)}"

def generate_report(template_path: str, context: Dict[str, Any], output_path: str) -> Dict[str, Any]:
    """
    Generate a report by rendering a template file and saving it to output_path.
    
    Args:
        template_path: Path to the template file.
        context: A dictionary of variables to pass to the template.
        output_path: Path where the generated report will be saved.
    
    Returns:
        A dictionary with keys 'success' (bool), 'message' (str), and optionally 'output_path'.
    """
    try:
        # Check if template file exists
        if not os.path.exists(template_path):
            return {
                'success': False,
                'error': f'Template file not found: {template_path}'
            }
        
        # Read the template file
        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()
        
        # Render the template
        rendered_content = render_template(template_str, context)
        
        # Check if rendering returned an error string
        if rendered_content.startswith('Error'):
            return {
                'success': False,
                'error': rendered_content
            }
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write the rendered content to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)
        
        return {
            'success': True,
            'message': 'Report generated successfully',
            'output_path': output_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating report: {str(e)}'
        }

def attach_report_to_event(attachment_path: str, event_id: str, service) -> Dict[str, Any]:
    """
    Attach a report file to a calendar event.
    
    This function is a placeholder and should be implemented according to the specific
    calendar service (Google or Outlook) being used.
    
    Args:
        attachment_path: Path to the file to attach.
        event_id: The ID of the event to attach the file to.
        service: The authenticated service object (Google Calendar or Outlook).
    
    Returns:
        A dictionary with keys 'success' (bool) and optionally 'message' or 'error'.
    """
    # This is a placeholder implementation.
    # In a real implementation, you would use the service's API to attach the file.
    # For Google Calendar, you would use the Google Drive API to upload the file and
    # then attach it to the event.
    # For Outlook, you would use the Microsoft Graph API to attach the file.
    
    # For now, we'll just check if the file exists and return success.
    try:
        if not os.path.exists(attachment_path):
            return {
                'success': False,
                'error': f'Attachment file not found: {attachment_path}'
            }
        
        # In a real implementation, you would attach the file to the event here.
        # Since we don't have the service implementation details, we'll simulate success.
        return {
            'success': True,
            'message': f'Attachment {attachment_path} would be attached to event {event_id}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error attaching report: {str(e)}'
        }
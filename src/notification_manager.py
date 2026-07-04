import os
import json
from typing import Optional

def send_slack_notification(webhook_url: str = None, text: str = "") -> dict:
    webhook = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
    if not webhook:
        return {'success': False, 'error': 'No webhook URL provided'}
    
    try:
        import requests
        response = requests.post(
            webhook,
            json={'text': text},
            headers={'Content-Type': 'application/json'}
        )
        return {'success': response.ok, 'status_code': response.status_code}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def send_teams_notification(webhook_url: str = None, title: str = "", text: str = "") -> dict:
    webhook = webhook_url or os.getenv('TEAMS_WEBHOOK_URL')
    if not webhook:
        return {'success': False, 'error': 'No webhook URL provided'}
    
    try:
        import requests
        response = requests.post(
            webhook,
            json={'title': title, 'text': text},
            headers={'Content-Type': 'application/json'}
        )
        return {'success': response.ok, 'status_code': response.status_code}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def send_email_notification(smtp_config: dict = None, to_emails: list = None, subject: str = "", body: str = "") -> dict:
    if not smtp_config or not to_emails:
        return {'success': False, 'error': 'Missing SMTP config or recipients'}
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('sender')
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_config.get('host'), smtp_config.get('port', 587))
        server.starttls()
        server.login(smtp_config.get('user'), smtp_config.get('password'))
        server.send_message(msg)
        server.quit()
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}
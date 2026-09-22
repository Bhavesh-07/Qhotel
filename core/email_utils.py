import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.database import get_settings

def send_smtp_email(subject, body, placeholders=None):
    s = get_settings()
    # Check if SMTP is configured
    required = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'email_to']
    if not all(s.get(k) for k in required):
        print("SMTP not fully configured. Skipping email.")
        return False

    # Use template if available
    template = s.get('email_template')
    if template and placeholders:
        try:
            body = template.format(**placeholders)
        except Exception as e:
            print(f"Template parsing failed: {e}")

    try:
        msg = MIMEMultipart()
        msg['From'] = s.get('email_from', s.get('smtp_user'))
        msg['To'] = s['email_to']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(s['smtp_host'], int(s['smtp_port']))
        server.starttls()
        server.login(s['smtp_user'], s['smtp_pass'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        import traceback
        print(f"FAILED TO SEND EMAIL. Error: {e}")
        traceback.print_exc()
        return False

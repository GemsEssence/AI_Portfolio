import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_report_email(recipient: str, subject: str, body: str, preview: bool = True):
    """
    Sends an email or returns a preview.

    Args:
        recipient (str): Email address of recipient.
        subject (str): Email subject.
        body (str): Email body content.
        preview (bool): If True, return preview instead of sending.

    Returns:
        dict or str: If preview=True, returns dict with email content.
                     If preview=False, returns string status of sending.
    """

    # PREVIEW MODE: just return the email content
    if preview:
        return {"to": recipient, "subject": subject, "body": body}

    # ACTUAL SEND
    host = os.getenv("EMAIL_SMTP_HOST")
    port = int(os.getenv("EMAIL_SMTP_PORT"))
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    try:
        msg = MIMEMultipart()
        msg["From"] = user
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect and send
        server = smtplib.SMTP(host, port)
        server.ehlo()           # handshake
        server.starttls()       # secure connection
        server.ehlo()
        server.login(user, password)
        server.send_message(msg)
        server.quit()

        return "Email sent successfully!"

    except Exception as e:
        return f"Email failed: {e}"

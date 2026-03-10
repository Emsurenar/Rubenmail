import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def send_email(html_content, subject_prefix="Dagens lärdom"):
    sender_email = os.getenv("EMAIL_SENDER", "").strip().replace('\n', '').replace('\r', '')
    receiver_email = os.getenv("EMAIL_RECEIVER", "").strip().replace('\n', '').replace('\r', '')
    password = os.getenv("EMAIL_PASSWORD", "").strip().replace('\n', '').replace('\r', '')

    print(f"Sender: {sender_email}")
    print(f"Receiver: {receiver_email}")
    print(f"Password length: {len(password)}")

    if not all([sender_email, receiver_email, password]):
        print("Missing email credentials in environment variables.")
        return False

    msg = MIMEMultipart("alternative")
    
    # Custom subject with date
    today = datetime.now().strftime("%Y-%m-%d")
    msg["Subject"] = f"{subject_prefix} - {today}"
    msg["From"] = sender_email
    
    # Process receiver_email as a CSV list
    receivers = [email.strip() for email in receiver_email.split(",") if email.strip()]
    msg["To"] = ", ".join(receivers)

    # Add HTML part
    part = MIMEText(html_content, "html", "utf-8")
    msg.attach(part)

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receivers, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

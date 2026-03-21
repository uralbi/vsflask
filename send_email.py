#!/var/www/user118263/data/myenv/bin/python
"""
Usage: python send_email.py <to_email> <code>
"""
import smtplib
import sys
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

if len(sys.argv) < 3:
    print("Usage: send_email.py <to_email> <code>")
    sys.exit(1)

to_email = sys.argv[1]
code = sys.argv[2]

smtp_host = os.getenv("MAIL_SERVER")
smtp_port = int(os.getenv("MAIL_PORT"))
smtp_user = os.getenv("MAIL_USERNAME")
smtp_pass = os.getenv("MAIL_PASSWORD")
sender = os.getenv("MAIL_SENDER")

body = "Your verification code: {}\n\nEnter this code to activate your account.".format(code)
msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = "Account Verification Code"
msg["From"] = sender
msg["To"] = to_email

try:
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [to_email], msg.as_string())
    elif smtp_port == 25:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.sendmail(sender, [to_email], msg.as_string())
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [to_email], msg.as_string())
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)

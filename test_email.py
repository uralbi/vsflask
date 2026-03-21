import smtplib
import os
import sys
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

smtp_host = os.getenv("MAIL_SERVER")
smtp_port = int(os.getenv("MAIL_PORT"))
smtp_user = os.getenv("MAIL_USERNAME")
smtp_pass = os.getenv("MAIL_PASSWORD")
sender = os.getenv("MAIL_SENDER")
to_email = sys.argv[1] if len(sys.argv) > 1 else smtp_user

print("MAIL_SERVER  : {}".format(smtp_host))
print("MAIL_PORT    : {}".format(smtp_port))
print("MAIL_USERNAME: {}".format(smtp_user))
print("MAIL_SENDER  : {}".format(sender))
print("Sending to   : {}".format(to_email))
print("")

msg = MIMEText("Test email from VS Flask app.", "plain", "utf-8")
msg["Subject"] = "Test Email"
msg["From"] = sender
msg["To"] = to_email

try:
    if smtp_port == 465:
        print("Connecting via SMTP_SSL on port 465 ...")
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [to_email], msg.as_string())
    elif smtp_port == 25:
        print("Connecting via SMTP on port 25 (no auth) ...")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.sendmail(sender, [to_email], msg.as_string())
    else:
        print("Connecting via SMTP + STARTTLS on port {} ...".format(smtp_port))
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [to_email], msg.as_string())

    print("OK - email sent successfully.")
except Exception as e:
    print("FAILED: {}".format(e))

#!/var/www/user118263/data/myenv/bin/python
"""
Usage: python send_reset_email.py <to_email> <new_password>
"""
import smtplib
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

if len(sys.argv) < 3:
    print("Usage: send_reset_email.py <to_email> <new_password>")
    sys.exit(1)

to_email = sys.argv[1]
new_password = sys.argv[2]

smtp_host = os.getenv("MAIL_SERVER")
smtp_port = int(os.getenv("MAIL_PORT"))
smtp_user = os.getenv("MAIL_USERNAME")
smtp_pass = os.getenv("MAIL_PASSWORD")
sender = os.getenv("MAIL_SENDER")

plain_body = "Your new password: {}\n\nUse this password to sign in. Please change it after logging in.".format(new_password)

html_body = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;">

          <!-- Header -->
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <span style="font-size:28px;font-weight:700;color:#18181b;letter-spacing:-0.5px;">VS</span>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background:#ffffff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.07);padding:48px 40px;">

              <!-- Icon -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:28px;">
                    <div style="display:inline-block;background:#f0f9ff;border-radius:50%;width:64px;height:64px;line-height:64px;text-align:center;">
                      <span style="font-size:28px;">&#128274;</span>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Title -->
              <h1 style="margin:0 0 8px;font-size:22px;font-weight:700;color:#18181b;text-align:center;">
                Password Reset
              </h1>
              <p style="margin:0 0 32px;font-size:14px;color:#71717a;text-align:center;line-height:1.5;">
                We received a request to reset your password.<br>Here is your new temporary password:
              </p>

              <!-- Password box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                <tr>
                  <td align="center">
                    <div style="display:inline-block;background:#f4f4f5;border:1.5px dashed #d4d4d8;border-radius:8px;padding:14px 32px;">
                      <span style="font-family:'Courier New',Courier,monospace;font-size:22px;font-weight:700;color:#18181b;letter-spacing:3px;">{password}</span>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Divider -->
              <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 28px;">

              <!-- Note -->
              <p style="margin:0;font-size:13px;color:#71717a;text-align:center;line-height:1.6;">
                Sign in with this password and change it in your account settings.<br>
                If you did not request a password reset, you can safely ignore this email.
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding-top:24px;">
              <p style="margin:0;font-size:12px;color:#a1a1aa;">&copy; 2025 VS &mdash; All rights reserved</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
""".format(password=new_password)

msg = MIMEMultipart("alternative")
msg["Subject"] = "Password Reset"
msg["From"] = sender
msg["To"] = to_email
msg.attach(MIMEText(plain_body, "plain", "utf-8"))
msg.attach(MIMEText(html_body, "html", "utf-8"))

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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# 1️⃣ Your email + app password
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("APP_PASSWORD")

# 2️⃣ Receiver email
# receiver_email = os.getenv("RECEIVER_EMAIL")
receiver_email = ["malayj1234@gmail.com"]

# 3️⃣ Build email headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = ", ".join(receiver_email)
message["Subject"] = "Hello from Python!"

# # 4️⃣ Email body (plain text)
# body = "This email was sent automatically using Python 🙂"
# message.attach(MIMEText(body, "plain"))

# 4️⃣ Email body (HTML)
html = """
<h2>Hello 👋</h2>
<p>This email was sent using <b>Python</b>.</p>
"""
message.attach(MIMEText(html, "html"))

try:
    # 5️⃣ Connect to Gmail SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)

    # 6️⃣ Secure the connection
    server.starttls()

    # 7️⃣ Login
    server.login(sender_email, sender_password)

    # 8️⃣ Send email
    server.sendmail(sender_email, receiver_email, message.as_string())

    print("Email sent successfully!")

except Exception as e:
    print("Error:", e)

finally:
    server.quit()

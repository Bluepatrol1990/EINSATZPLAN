import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    # Deine Zugangsdaten (sollten sicher verwahrt werden)
    sender_email = "deine_email@beispiel.de"
    password = "dein_passwort"

    # Die Empfänger aus deinen Vorgaben
    recipients = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

    # Erstellung der Nachricht
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Verbindung zum Server (Beispiel Gmail: smtp.gmail.com)
        with smtplib.SMTP("smtp.beispiel.de", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipients, message.as_string())
        print("E-Mail erfolgreich an beide Adressen gesendet.")
    except Exception as e:
        print(f"Fehler beim Senden: {e}")

# Beispielaufruf
send_email("Test-Betreff", "Dies ist eine automatisierte Nachricht.")

import subprocess
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser

# Konfigurationsdatei einlesen
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# E-Mail-Konfiguration
SMTP_SERVER = config['Email']['SMTP_SERVER']
SMTP_PORT = int(config['Email']['SMTP_PORT'])
SMTP_USERNAME = config['Email']['SMTP_USERNAME']
SMTP_PASSWORD = config['Email']['SMTP_PASSWORD']
RECIPIENT_EMAIL = config['Notifications']['RECIPIENT_EMAIL']
EMAIL_SUBJECT = config['Notifications']['SUBJECT']
EMAIL_MESSAGE_BODY = config['Notifications']['MESSAGE_BODY']

# Netzwerk-Konfiguration
IP_LIST = config['Network']['IP_LIST'].split(',')

def send_email(recipient, unreachable_ip):
    message = EMAIL_MESSAGE_BODY.format(ip=unreachable_ip)
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header(EMAIL_SUBJECT, 'utf-8')
    msg['From'] = SMTP_USERNAME
    msg['To'] = recipient

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, recipient, msg.as_string())
        server.quit()
        print(f"E-Mail erfolgreich gesendet wegen Nichterreichbarkeit von {unreachable_ip}.")
    except smtplib.SMTPException as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

def ping(hosts):
    ttl_bytes = b'TTL'
    for ip in hosts:
        ip = ip.strip()
        output = subprocess.Popen(f"ping {ip} -n 1", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = output.stdout.read()
        if ttl_bytes in data:
            print(f"{ip} : Successful Ping")
        else:
            print(f"{ip} : Failed Ping")
            send_email(RECIPIENT_EMAIL, ip)

def main():
    ping(IP_LIST)

if __name__ == '__main__':
    main()

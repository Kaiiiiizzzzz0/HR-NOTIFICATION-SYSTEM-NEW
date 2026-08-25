import os
import os

from dotenv import load_dotenv


load_dotenv()


# config for the database connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "hr_notification_database")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


# config for the email server connection
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com") # change this to outlook
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "") # change this to the username it.intern@megaxcess.com
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "") # change this to the actual password
SMTP_FROM = os.getenv("SMTP_FROM", "") # change this to the username it.intern@megaxcess.com
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() in (
    "1", "true", "yes", "y")

# config for the email receiving server connection
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
IMAP_USER = os.getenv("IMAP_USER", "")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "")
from environs import Env
from pathlib import Path

DEBUG = True

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN", "")  # Забираем значение типа str
ADMINS = env.list("ADMINS", [])  # Тут у нас будет список из админов

I18N_DOMAIN = 'testbot'

LOCALES_DIR = 'locales'

DATABASE_URL_PG = "postgres://user:password@host/db_name"

"""
WEBHOOK

Quick'n'dirty SSL certificate generation:

openssl genrsa -out webhook_pkey.pem 2048
openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem

When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
with the same value in you put in WEBHOOK_HOST

"""
WEBHOOK_HOST = '18.159.52.208'  # '<ip/host where the bot is running>'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_URL_PATH = '/.ssl'  # Part of URL

# This options needed if you use self-signed SSL certificate
# Instructions: https://core.telegram.org/bots/self-signed
WEBHOOK_SSL_CERT = './.ssl/webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './.ssl/webhook_pkey.pem'  # Path to the ssl private key


WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_URL_PATH}"



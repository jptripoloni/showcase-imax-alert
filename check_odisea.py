import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import date

# URL exacta de La Odisea en IMAX Norcenter
URL = "https://entradas.todoshowcase.com/showcase/pelicula?filmid=5875&house_id=3250"

# Solo nos interesan funciones DESPUÉS de esta fecha
FECHA_LIMITE = date(2026, 7, 22)

# Credenciales desde GitHub Secrets
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
EMAIL_DEST = os.environ["EMAIL_DEST"]


def obtener_fechas_nuevas() -> list[str]:
    """
    Devuelve lista de fechas (strings 'YYYY-MM-DD') disponibles
    que sean posteriores a FECHA_LIMITE.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://entradas.todoshowcase.com/showcase/",
    }

    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    fechas_nuevas = []
    for btn in soup.find_all("button", class_="op_day"):
        valor = btn.get("value", "")  # formato: "2026-07-23"
        if not valor:
            continue
        try:
            anio, mes, dia = valor.split("-")
            fecha = date(int(anio), int(mes), int(dia))
            if fecha > FECHA_LIMITE:
                fechas_nuevas.append(btn.get_text(strip=True))  # ej: "Jue 23/07"
        except ValueError:
            continue

    return fechas_nuevas


def enviar_mail(fechas: list[str]):
    lista = "".join(f"<li>{f}</li>" for f in fechas)
    cuerpo = f"""
<h2>🎬 ¡Nuevas funciones de La Odisea en Showcase IMAX Norcenter!</h2>
<p>Aparecieron funciones <b>después del 22/07</b>:</p>
<ul>{lista}</ul>
<p>Comprá las entradas acá:<br>
<a href="{URL}">{URL}</a></p>
"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎬 ALERTA: La Odisea — nuevas funciones post 22/07 en IMAX"
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_DEST
    msg.attach(MIMEText(cuerpo, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, EMAIL_DEST, msg.as_string())

    print(f"[OK] Mail enviado a {EMAIL_DEST}")


def main():
    from datetime import datetime
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Revisando funciones...")

    try:
        fechas_nuevas = obtener_fechas_nuevas()
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    if fechas_nuevas:
        print(f"[!] Fechas nuevas encontradas: {fechas_nuevas}")
        enviar_mail(fechas_nuevas)
    else:
        print("[—] No hay funciones después del 22/07 todavía.")


if __name__ == "__main__":
    main()

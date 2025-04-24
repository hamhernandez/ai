#!/bin/bash

set -e

echo "[ENTRYPOINT] Comprobando pesos preentrenados..."

MODEL_DIR="/workspace/HunyuanVideo/ckpts"

if [ ! -d "$MODEL_DIR" ] || [ -z "$(ls -A $MODEL_DIR)" ]; then
    echo "[ENTRYPOINT] Pesos no encontrados. Descargando desde Hugging Face..."
    pip install "huggingface_hub[cli]"
    huggingface-cli download tencent/HunyuanVideo --local-dir "$MODEL_DIR"
else
    echo "[ENTRYPOINT] Pesos encontrados en $MODEL_DIR"
fi

# Lanza tu aplicación o servicio
echo "[ENTRYPOINT] Lanzando servidor o servicio principal..."
# Ejemplo:
# python3 app.py

# Para dejar corriendo SSH (por ejemplo si solo quieres acceso)
echo "[ENTRYPOINT] Lanzando SSH..."
/usr/sbin/sshd -D
#!/bin/bash

# Configurá tu URL de Modal (pegala desde el output de modal serve)
MODAL_URL="https://hamhernandez--hunyuan-web-app-run-server-dev.modal.run"

# Prompt de ejemplo
PROMPT="A futuristic city at sunset"

echo "🚀 Enviando solicitud POST para generar el video..."
curl -X POST "${MODAL_URL}/generate_video_web" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"${PROMPT}\"}"

echo ""
echo "⌛ Esperando 10 segundos para que el video se genere..."
sleep 10

echo "📥 Descargando video generado..."
curl -o generated_video.mp4 "${MODAL_URL}/download_video"

echo ""
echo "✅ Video descargado como generated_video.mp4"
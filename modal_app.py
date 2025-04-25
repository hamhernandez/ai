import modal
import subprocess
import shutil
from fastapi import Request
from fastapi.responses import StreamingResponse

# Construir la imagen Docker
image = modal.Image.from_dockerfile(
    "./Dockerfile",
    gpu="any",
    add_python="3.10",
)

# Crear la App
app = modal.App("hunyuan-video")

# Crear volumen persistente (opcional)
volume = modal.Volume.from_name("hunyuan-storage", create_if_missing=True)

# Funcion para generar el video
@modal.function(
        image=image,
        gpu="any",
        volumes={"vol": volume},
        timeout=60 * 10,
)
def generate_video(prompt: str):
    output_path = "/root/out/video.mp4"
    volume_path = "/vol/video.mp4"
    cmd = [
        "python3", "/workspace/HunyuanVideo/run_inference.py",
        "--prompt", prompt,
        "--output", output_path,
    ]
    subprocess.run(cmd, check=True)

    shutil.copy(output_path, volume_path)
    return volume_path

# Endpoint POST para generar el video a partir de un prompt
@modal.fastapi_endpoint(method="POST")
async def generate_video_web(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "A futuristic city at sunset")

    # Llamar a la funcion remota
    generate_video.remote(prompt)

    return {"message": "Generacion iniciada", "prompt": prompt}

# Endpoint GET para descargar el ultimo video generado
@modal.fastapi_endpoint(method="GET")
def download_video():
    with volume.open("video.mp4", "rb") as f:
        return StreamingResponse(f, media_type="video/mp4")
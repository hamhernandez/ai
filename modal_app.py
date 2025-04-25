import modal
import subprocess
import shutil
from fastapi import Request
from fastapi.responses import StreamingResponse

# Construir la imagen Docker
image = modal.Image.debian_slim(python_version="3.10").run_commands(
    "apt-get update && apt-get install -y git ffmpeg libgl1-mesa-glx python3-opencv openssh-server sudo",
    "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
    "git clone https://github.com/Tencent/HunyuanVideo.git /workspace/HunyuanVideo",
    "cd /workspace/HunyuanVideo && git submodule update --init --recursive",
    "pip install -r /workspace/HunyuanVideo/requirements.txt",
    "pip install huggingface_hub[cli]",
    "huggingface-cli download tencent/HunyuanVideo --local-dir /workspace/HunyuanVideo/ckpts",
    gpu="any",  # Esto moverá el argumento gpu al final
)

# Crear la App
app = modal.App("hunyuan-video")

# Crear volumen persistente (opcional)
volume = modal.Volume.from_name("hunyuan-storage", create_if_missing=True)

# Funcion para generar el video
@app.function(
    image=image,
    gpu="any",
    volumes={"/vol": volume},
    timeout=60 * 10,
)
def generate_video(prompt: str):
    weights_path = "/vol/hunyuanvideo_weights" # Para guardar los pesos del modelo
    output_path = "/root/out/video.mp4"
    volume_path = "/vol/video.mp4"

    # Comprobar si los pesos ya existen en el volumen
    if not volume.exists(weights_path + "/.done"):
        cmd_download = [
            "pip", "install", "huggingface_hub[cli]"
        ]
        subprocess.run(cmd_download, check=True)
        cmd_hf_download = [
            "huggingface-cli", "download", "tencent/HunyuanVideo",
            "--local-dir", weights_path
        ]
        subprocess.run(cmd_hf_download, check=True)
        # Crear un archivo para indicar que la descarga se completó
        with volume.open(weights_path + "/.done", "w") as f:
            f.write("descarga completada")
    else:
        print(f"Pesos encontrados en el volumen: {weights_path}")

    cmd = [
        "python3", "/workspace/HunyuanVideo/run_inference.py",
        "--prompt", prompt,
        "--output", output_path,
        "--weights_path", "/vol/hunyuanvideo_weights"  # La ruta en el volumen
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

# Importante: referencias explícitas
generate_video_web
download_video

if __name__ == "__main__":
    app.serve()
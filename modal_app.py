import subprocess
import modal
from fastapi import FastAPI, Request

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

# Función de inferencia dentro del contenedor
@app.function(image=image, gpu="any", timeout=60 * 60, volumes={"/root/out": volume})
def generate_video(prompt: str):
    output_path = "/root/out/video.mp4"
    cmd = [
        "python3", "/workspace/HunyuanVideo/run_inference.py",
        "--prompt", prompt,
        "--output", output_path,
    ]
    subprocess.run(cmd, check=True)
    return output_path

# App FastAPI
web_app = FastAPI()

@web_app.post("/generate")
async def generate_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "A futuristic city at sunset")
    output_path = generate_video.remote(prompt)
    return {"message": "Video en proceso", "output_path": output_path}

# Vincular FastAPI con Modal
@app.fastapi_endpoint()
def serve():
    return web_app
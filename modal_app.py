import subprocess
import modal

# Construir la imagen Docker
image = modal.Image.from_dockerfile(
    "./Dockerfile",
    gpu="any",
    add_python="3.10",
)

# Crear la App
app = modal.App("hunyuan-video")

# Crear volumen persistente (si aún no lo tienes creado)
volume = modal.SharedVolume().persist("hunyuan-storage")

# Endpoint web
@app.web_endpoint(method="POST")
@app.function(
    image=image,
    gpu="any",
    timeout=60 * 10,
    volumes={"/root/out": volume},
)
def generate_video_web(request):
    """
    Endpoint que genera un video a partir de un prompt.
    """
    data = request.json
    prompt = data.get("prompt", "A futuristic city at sunset")
    output_path = "/root/out/video.mp4"

    cmd = [
        "python3", "/workspace/HunyuanVideo/run_inference.py",
        "--prompt", prompt,
        "--output", output_path,
    ]
    subprocess.run(cmd, check=True)

    return {"message": "Video generado con éxito", "output_path": output_path}
import modal
import shutil
import subprocess

volume = modal.Volume.from_name("hunyuan-storage", create_if_missing=True)

image = modal.Image.debian_slim(python_version="3.10").run_commands(
    "apt-get update && apt-get install -y git ffmpeg libgl1-mesa-glx python3-opencv openssh-server sudo",
    "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
    "pip install fastapi uvicorn",
    "git clone https://github.com/Tencent/HunyuanVideo.git /workspace/HunyuanVideo",
    "cd /workspace/HunyuanVideo && git submodule update --init --recursive",
    "pip install -r /workspace/HunyuanVideo/requirements.txt",
    "pip install huggingface_hub[cli]",
    "huggingface-cli download tencent/HunyuanVideo --local-dir /workspace/HunyuanVideo/ckpts",
    gpu="any",
)

app = modal.App(name="hunyuan-worker-app")  # Solo funciones

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
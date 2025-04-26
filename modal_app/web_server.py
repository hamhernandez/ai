import modal
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

# Crear App Modal
app = modal.App(name="hunyuan-web-app")

# Crear App FastAPI
web_app = FastAPI()

volume = modal.Volume.from_name("hunyuan-storage", create_if_missing=True)

@web_app.post("/generate_video_web")
async def generate_video_web(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "A futuristic city at sunset")
    
    from modal_app.worker import generate_video
    generate_video.spawn(prompt)

    return {"message": "Generación iniciada", "prompt": prompt}

@web_app.get("/download_video")
async def download_video():
    try:
        with volume.open("video.mp4", "rb") as f:
            return StreamingResponse(f, media_type="video/mp4")
    except Exception as e:
        return {"error": str(e)}

# Esta función realmente inicia FastAPI
@app.function()
@modal.web_server(8000)
def run_server():
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
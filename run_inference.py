import argparse
import os
from HunyuanVideo.pipeline.pipeline import Text2VideoPipeline

def main():
    parser = argparse.ArgumentParser(description="Generar video a partir de texto")
    parser.add_argument("--prompt", type=str, required=True, help="Texto para generar el video")
    parser.add_argument("--output", type=str, required=True, help="Ruta de salida del video")
    args = parser.parse_args()

    pipeline = Text2VideoPipeline(
        pretrained_model_path="./HunyuanVideo/Hunyuan",  # ajusta si necesario
        dtype="float16"
    )

    print(f"Generando video para el prompt: {args.prompt}")
    pipeline.generate(
        prompt=args.prompt,
        output_path=args.output,
        seed=42  # puedes hacerlo configurable si lo deseas
    )
    print(f"Video guardado en {args.output}")

if __name__ == "__main__":
    main()
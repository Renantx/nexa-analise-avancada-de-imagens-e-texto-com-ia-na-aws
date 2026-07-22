import argparse
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_rekognition.type_defs import (
    CelebrityTypeDef,
    RecognizeCelebritiesResponseTypeDef,
)
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"
DEFAULT_PHOTOS = ("bbc.jpg", "msn.jpg", "neymar-torcedores.jpg")


def get_path(file_name: str) -> Path:
    return IMAGES_DIR / file_name


def load_font(size: int = 20):
    for font_name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def recognize_celebrities(
    photo: Path, region: str | None = None
) -> RecognizeCelebritiesResponseTypeDef:
    if not photo.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {photo}")

    client = boto3.client("rekognition", region_name=region)
    with open(photo, "rb") as image:
        return client.recognize_celebrities(Image={"Bytes": image.read()})


def draw_boxes(
    image_path: Path,
    output_path: Path,
    face_details: list[CelebrityTypeDef],
    confidence_threshold: float,
) -> None:
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = load_font()
    width, height = image.size

    for face in face_details:
        confidence = float(face.get("MatchConfidence", 0) or 0)
        if confidence <= confidence_threshold:
            continue

        box = face["Face"]["BoundingBox"]  # type: ignore[index]
        left = int(box["Left"] * width)  # type: ignore[index]
        top = int(box["Top"] * height)  # type: ignore[index]
        right = int((box["Left"] + box["Width"]) * width)  # type: ignore[index]
        bottom = int((box["Top"] + box["Height"]) * height)  # type: ignore[index]

        draw.rectangle([left, top, right, bottom], outline="red", width=3)

        text = face.get("Name", "") or ""
        position = (left, max(0, top - 20))
        bbox = draw.textbbox(position, text, font=font)
        draw.rectangle(bbox, fill="red")
        draw.text(position, text, font=font, fill="white")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    print(f"Imagem salva com resultados em: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconhece celebridades em imagens com Amazon Rekognition."
    )
    parser.add_argument(
        "--images",
        nargs="+",
        type=Path,
        default=[get_path(name) for name in DEFAULT_PHOTOS],
        help="Uma ou mais imagens para analisar",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=90.0,
        help="Confiança mínima para desenhar a caixa (padrão: 90)",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION"),
        help="Região AWS (padrão: AWS_DEFAULT_REGION / AWS_REGION)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        for photo_path in args.images:
            photo = photo_path.resolve()
            response = recognize_celebrities(photo, region=args.region)
            faces = response["CelebrityFaces"]
            if not faces:
                print(f"Não foram encontrados famosos para a imagem: {photo}")
                continue
            output_path = photo.with_name(f"{photo.stem}-resultado{photo.suffix}")
            draw_boxes(photo, output_path, faces, args.confidence)
        return 0
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except (ClientError, BotoCoreError) as exc:
        print(f"Erro ao chamar o Rekognition: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_rekognition.type_defs import CompareFacesMatchTypeDef
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"


def get_path(file_name: str) -> Path:
    return IMAGES_DIR / file_name


def load_font(size: int = 16):
    for font_name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def compare_faces(
    source_image_path: Path,
    target_image_path: Path,
    similarity_threshold: float = 80,
    region: str | None = None,
):
    for path in (source_image_path, target_image_path):
        if not path.is_file():
            raise FileNotFoundError(f"Imagem não encontrada: {path}")

    client = boto3.client("rekognition", region_name=region)
    with open(source_image_path, "rb") as source_image, open(
        target_image_path, "rb"
    ) as target_image:
        return client.compare_faces(
            SourceImage={"Bytes": source_image.read()},
            TargetImage={"Bytes": target_image.read()},
            SimilarityThreshold=similarity_threshold,
        )


def draw_boxes(
    image_path: Path,
    output_path: Path,
    face_details: list[CompareFacesMatchTypeDef],
) -> None:
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = load_font()
    width, height = image.size

    for face in face_details:
        box = face["Face"]["BoundingBox"]  # type: ignore[index]
        left = int(box["Left"] * width)  # type: ignore[index]
        top = int(box["Top"] * height)  # type: ignore[index]
        right = int((box["Left"] + box["Width"]) * width)  # type: ignore[index]
        bottom = int((box["Top"] + box["Height"]) * height)  # type: ignore[index]

        draw.rectangle([left, top, right, bottom], outline="red", width=3)

        similarity = float(face["Similarity"])  # type: ignore[arg-type]
        label = f"{similarity:.1f}%"
        position = (left, max(0, top - 14))
        draw.text(position, label, fill="red", font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    print(f"Imagem salva com resultados em: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compara rostos entre duas imagens com Amazon Rekognition."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=get_path("neymar.jpg"),
        help="Imagem de origem (rosto de referência)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=get_path("msn.jpg"),
        help="Imagem alvo onde procurar o rosto",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Caminho da imagem anotada (padrão: resultado_<target>)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Similaridade mínima (padrão: 80)",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION"),
        help="Região AWS (padrão: AWS_DEFAULT_REGION / AWS_REGION)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    target = args.target.resolve()
    output = (
        args.output.resolve()
        if args.output
        else target.with_name(f"resultado_{target.name}")
    )

    try:
        response = compare_faces(
            source,
            target,
            similarity_threshold=args.threshold,
            region=args.region,
        )

        if response["FaceMatches"]:
            print("Rostos encontrados:")
            for match in response["FaceMatches"]:
                print(f"- Similaridade: {match['Similarity']:.2f}")  # type: ignore[index]
            draw_boxes(target, output, response["FaceMatches"])
        else:
            print("Nenhum rosto correspondente foi encontrado.")
        return 0
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except (ClientError, BotoCoreError) as exc:
        print(f"Erro ao chamar o Rekognition: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

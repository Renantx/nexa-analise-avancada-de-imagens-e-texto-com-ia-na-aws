import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_textract.type_defs import BlockTypeDef

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGE = BASE_DIR / "images" / "lista-material-escolar.jpeg"
CACHE_PATH = BASE_DIR / "response.json"


def detect_file_text(
    file_path: Path,
    cache_path: Path,
    region: str | None = None,
) -> dict[str, Any]:
    if not file_path.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {file_path}")

    client = boto3.client("textract", region_name=region)
    with open(file_path, "rb") as file:
        document_bytes = file.read()

    response = client.detect_document_text(Document={"Bytes": document_bytes})
    cache_path.write_text(json.dumps(response), encoding="utf-8")
    print(f"Resposta salva em: {cache_path}")
    return response


def extract_lines(blocks: list[BlockTypeDef]) -> list[str]:
    return [
        block["Text"]
        for block in blocks
        if block.get("BlockType") == "LINE" and "Text" in block
    ]


def get_lines(
    file_path: Path,
    cache_path: Path,
    *,
    force: bool = False,
    region: str | None = None,
) -> list[str]:
    if force or not cache_path.is_file():
        response = detect_file_text(file_path, cache_path, region=region)
        return extract_lines(response["Blocks"])

    with open(cache_path, encoding="utf-8") as file:
        data = json.loads(file.read())
    return extract_lines(data["Blocks"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai linhas de texto de uma imagem com Amazon Textract."
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE,
        help=f"Caminho da imagem (padrão: {DEFAULT_IMAGE.name})",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION"),
        help="Região AWS (padrão: AWS_DEFAULT_REGION / AWS_REGION)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignora o cache local e chama a API novamente",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        lines = get_lines(
            args.image.resolve(),
            CACHE_PATH,
            force=args.force,
            region=args.region,
        )
        if not lines:
            print("Nenhuma linha de texto encontrada.")
            return 0
        for line in lines:
            print(line)
        return 0
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except (ClientError, BotoCoreError) as exc:
        print(f"Erro ao chamar o Textract: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

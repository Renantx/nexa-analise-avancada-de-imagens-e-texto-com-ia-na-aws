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
DEFAULT_IMAGE = BASE_DIR / "images" / "cnh.png"
CACHE_PATH = BASE_DIR / "response.json"


def get_document_data(file_name: Path) -> bytes:
    if not file_name.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {file_name}")
    with open(file_name, "rb") as file:
        data = file.read()
    print(f"Imagem carregada: {file_name}")
    return data


def analyze_document(
    file_path: Path,
    cache_path: Path,
    region: str | None = None,
) -> dict[str, Any]:
    client = boto3.client("textract", region_name=region)
    doc_bytes = get_document_data(file_path)
    response = client.analyze_document(
        Document={"Bytes": doc_bytes},
        FeatureTypes=["FORMS"],
    )
    cache_path.write_text(json.dumps(response), encoding="utf-8")
    print(f"Resposta salva em: {cache_path}")
    return response


def load_blocks(
    file_path: Path,
    cache_path: Path,
    *,
    force: bool = False,
    region: str | None = None,
) -> list[BlockTypeDef]:
    if force or not cache_path.is_file():
        response = analyze_document(file_path, cache_path, region=region)
        return response["Blocks"]

    with open(cache_path, encoding="utf-8") as file:
        return json.loads(file.read())["Blocks"]


def get_kv_map(
    blocks: list[BlockTypeDef],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    key_map: dict[str, dict[str, Any]] = {}
    value_map: dict[str, dict[str, Any]] = {}
    block_map: dict[str, dict[str, Any]] = {}

    for block in blocks:
        block_id = block["Id"]
        block_map[block_id] = block  # type: ignore[assignment]
        if block["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in block.get("EntityTypes", []):
                key_map[block_id] = block  # type: ignore[assignment]
            else:
                value_map[block_id] = block  # type: ignore[assignment]

    return key_map, value_map, block_map


def find_value_block(
    key_block: dict[str, Any], value_map: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    for relationship in key_block.get("Relationships", []):
        if relationship["Type"] == "VALUE":
            for value_id in relationship["Ids"]:
                return value_map[value_id]
    return {}


def get_text(result: dict[str, Any], block_map: dict[str, dict[str, Any]]) -> str:
    text = ""
    for relationship in result.get("Relationships", []):
        if relationship["Type"] == "CHILD":
            for child_id in relationship["Ids"]:
                word = block_map[child_id]
                if word["BlockType"] == "WORD":
                    text += word["Text"] + " "
    return text.rstrip()


def get_kv_relationship(
    key_map: dict[str, dict[str, Any]],
    value_map: dict[str, dict[str, Any]],
    block_map: dict[str, dict[str, Any]],
) -> dict[str, str]:
    kvs: dict[str, str] = {}
    for key_block in key_map.values():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        value = get_text(value_block, block_map)
        if key:
            kvs[key] = value
    return kvs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai campos de uma CNH com Amazon Textract (FORMS)."
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
        blocks = load_blocks(
            args.image.resolve(),
            CACHE_PATH,
            force=args.force,
            region=args.region,
        )
        key_map, value_map, block_map = get_kv_map(blocks)
        kvs = get_kv_relationship(key_map, value_map, block_map)

        print("\n\n== DADOS DA CNH ==\n")
        if not kvs:
            print("Nenhum campo chave/valor encontrado.")
            return 0
        for key, value in kvs.items():
            print(f"{key}: {value}")
        return 0
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except (ClientError, BotoCoreError) as exc:
        print(f"Erro ao chamar o Textract: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

import json
from pathlib import Path

from main import get_kv_map, get_kv_relationship

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "textract_response.json"


def test_get_kv_map_extracts_key_value_sets():
    blocks = json.loads(FIXTURE.read_text(encoding="utf-8"))["Blocks"]
    key_map, value_map, block_map = get_kv_map(blocks)

    assert key_map
    assert value_map
    assert block_map
    assert len(block_map) == len(blocks)


def test_get_kv_relationship_returns_cnh_fields():
    blocks = json.loads(FIXTURE.read_text(encoding="utf-8"))["Blocks"]
    key_map, value_map, block_map = get_kv_map(blocks)
    kvs = get_kv_relationship(key_map, value_map, block_map)

    assert kvs
    joined_keys = " ".join(kvs.keys()).upper()
    assert any(
        token in joined_keys
        for token in ("NOME", "CPF", "FILIAÇÃO", "FILIACAO", "NASCIMENTO")
    )

import json
from pathlib import Path

from main import extract_lines

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "textract_response.json"


def test_extract_lines_from_fixture():
    blocks = json.loads(FIXTURE.read_text(encoding="utf-8"))["Blocks"]
    lines = extract_lines(blocks)

    assert lines
    assert all(isinstance(line, str) and line.strip() for line in lines)

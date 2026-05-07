import uuid
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest) -> Path:
    base_root = Path.home() / ".codex" / "memories" / "participation_report_generator-tests"
    base_root.mkdir(parents=True, exist_ok=True)
    test_dir = base_root / f"{request.node.name}-{uuid.uuid4().hex}"
    test_dir.mkdir(parents=True, exist_ok=False)
    return test_dir


@pytest.fixture
def write_contacts_csv(tmp_path: Path):
    def _write(filename: str, rows: list[dict[str, str]], sep: str = ";") -> Path:
        csv_file = tmp_path / filename
        headers = ["IdUsuario", "Nombre", "Empresa", "Estado"]
        lines = [sep.join(headers)]
        for row in rows:
            lines.append(sep.join([row[h] for h in headers]))
        csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return csv_file

    return _write

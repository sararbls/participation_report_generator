from pathlib import Path

import pytest


@pytest.fixture
def write_contacts_csv(tmp_path):
    def _write(filename: str, rows: list[dict[str, str]], sep: str = ";") -> Path:
        csv_file = tmp_path / filename
        headers = ["IdUsuario", "Nombre", "Empresa", "Estado"]
        lines = [sep.join(headers)]
        for row in rows:
            lines.append(sep.join([row[h] for h in headers]))
        csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return csv_file

    return _write

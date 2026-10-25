import sys
from pathlib import Path

import segno

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vcard_qr as vq  # noqa: E402


def lines(vcard: str) -> list[str]:
    return vcard.split("\r\n")


def test_crlf_and_envelope():
    v = vq.build_vcard({"display_name": "Ana"})
    assert "\n" not in v.replace("\r\n", "")
    assert lines(v)[0] == "BEGIN:VCARD"
    assert lines(v)[1] == "VERSION:3.0"
    assert lines(v)[-1] == "END:VCARD"


def test_display_name_only_fills_N():
    """Regresión: con --name solo, N: salía vacío (N:;;;;)."""
    v = vq.build_vcard({"display_name": "Ana Martínez López"})
    assert "N:Martínez López;Ana;;;" in lines(v)
    assert "FN:Ana Martínez López" in lines(v)


def test_single_word_name():
    v = vq.build_vcard({"display_name": "Paulina"})
    assert "N:;Paulina;;;" in lines(v)


def test_explicit_parts_win():
    v = vq.build_vcard({"first_name": "Ana", "last_name": "López",
                        "display_name": "Anita"})
    assert "N:López;Ana;;;" in lines(v)
    assert "FN:Anita" in lines(v)


def test_escaping():
    v = vq.build_vcard({"display_name": "A", "organization": "Foo, S.A.; de C.V."})
    assert "ORG:Foo\\, S.A.\\; de C.V." in lines(v)


def test_qr_payload_is_utf8(tmp_path, monkeypatch):
    """Regresión: segno codificaba en ISO-8859-1 si podía."""
    seen = {}
    real_make = segno.make

    def spy(content, **kw):
        seen.update(kw)
        return real_make(content, **kw)

    monkeypatch.setattr(vq.segno, "make", spy)
    v = vq.build_vcard({"display_name": "Ana Martínez"})
    vq.generate(v, {"formats": ["png"], "basename": "t"}, tmp_path)
    assert seen.get("encoding") == "utf-8"
    # Y confirma que sin forzarlo el código sí sería distinto.
    assert real_make(v, error="h", encoding="utf-8") != real_make(v, error="h")
    assert (tmp_path / "t.png").stat().st_size > 0


def test_cli_address_and_work_phone(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "x", "--name", "Ana Martínez", "--phone", "+525512345678",
        "--phone-work", "+528180818717", "--address", "Calle 1, Monterrey",
        "--out", str(tmp_path)])
    assert vq.main() == 0
    out = capsys.readouterr().out
    assert "TEL;TYPE=WORK;TYPE=VOICE:+528180818717" in out
    assert "ADR;TYPE=WORK:;;Calle 1\\, Monterrey;;;;" in out

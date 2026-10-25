#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vcard_qr.py — Genera un QR de contacto (vCard 3.0) listo para escanear.

Al escanearlo con la cámara del teléfono, el contacto se guarda directamente
en la agenda: nombre, organización, puesto, teléfono, correo, web y dirección.
Funciona en iOS y Android sin apps adicionales.

Uso:
    python vcard_qr.py --config examples/contact.example.json
    python vcard_qr.py --name "Ana Martínez" --phone +525512345678 \
                       --email ana@ejemplo.mx --org "Estudio Ejemplo"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# En Windows la consola suele ser cp1252 y truena al imprimir acentos o líneas
# de caja. Forzamos UTF-8 en stdout/stderr cuando es posible.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

try:
    import segno
except ImportError:
    raise SystemExit(
        "Falta la dependencia 'segno'. Instálala con:\n    pip install segno"
    )


# ───────────────────────────── vCard ──────────────────────────────────

def escape(value: str) -> str:
    """Escapa los caracteres reservados del formato vCard."""
    if value is None:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def build_vcard(c: dict) -> str:
    """
    Construye la vCard 3.0.

    Se usa 3.0 y no 4.0 porque es la versión con mejor compatibilidad
    universal: iOS, Android, macOS y Outlook la leen sin problemas.
    """
    first = c.get("first_name", "")
    last = c.get("last_name", "")
    display = c.get("display_name") or f"{first} {last}".strip()

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape(last)};{escape(first)};;;",
        f"FN:{escape(display)}",
    ]

    if c.get("organization"):
        lines.append(f"ORG:{escape(c['organization'])}")
    if c.get("title"):
        lines.append(f"TITLE:{escape(c['title'])}")
    if c.get("phone"):
        lines.append(f"TEL;TYPE=CELL;TYPE=VOICE;TYPE=pref:{c['phone']}")
    if c.get("phone_work"):
        lines.append(f"TEL;TYPE=WORK;TYPE=VOICE:{c['phone_work']}")
    if c.get("email"):
        lines.append(f"EMAIL;TYPE=INTERNET;TYPE=pref:{c['email']}")
    if c.get("website"):
        lines.append(f"URL:{c['website']}")
    if c.get("address"):
        lines.append(f"ADR;TYPE=WORK:;;{escape(c['address'])};;;;")
    if c.get("note"):
        lines.append(f"NOTE:{escape(c['note'])}")

    lines.append("END:VCARD")

    # vCard 3.0 exige CRLF entre líneas. Usar \n rompe algunos lectores.
    return "\r\n".join(lines)


# ───────────────────────────── Salida ──────────────────────────────────

def generate(vcard: str, out: dict, out_dir: Path) -> list[Path]:
    basename = out.get("basename", "QR Contacto")
    dark = out.get("dark", "#1A237E")
    light = out.get("light", "#FFFFFF")
    scale = int(out.get("scale", 14))
    border = int(out.get("border", 4))
    error_level = out.get("error_level", "h")
    formats = out.get("formats", ["png", "svg"])

    qr = segno.make(vcard, error=error_level)

    written = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for fmt in formats:
        path = out_dir / f"{basename}.{fmt}"
        qr.save(str(path), scale=scale, border=border,
                dark=dark, light=light, kind=fmt)
        written.append(path)
    return written


# ───────────────────────────── CLI ────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Genera un QR de contacto vCard 3.0."
    )
    ap.add_argument("--config", help="JSON con los datos del contacto")
    ap.add_argument("--out", default=".", help="Carpeta de salida")
    ap.add_argument("--name", help="Nombre completo (si no usas --config)")
    ap.add_argument("--phone", help="Teléfono con código de país, ej. +525512345678")
    ap.add_argument("--email", help="Correo electrónico")
    ap.add_argument("--org", help="Organización o empresa")
    ap.add_argument("--title", help="Puesto o cargo")
    ap.add_argument("--website", help="Sitio web")
    ap.add_argument("--first-name", help="Nombre(s)")
    ap.add_argument("--last-name", help="Apellidos")
    args = ap.parse_args()

    if args.config:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
        contact = cfg.get("contact", cfg)
        output = cfg.get("output", {})
    else:
        if not args.name and not args.phone and not args.email:
            ap.error("Usa --config o al menos --name/--phone/--email")
        contact = {
            "first_name": args.first_name or "",
            "last_name": args.last_name or "",
            "display_name": args.name or "",
            "phone": args.phone or "",
            "email": args.email or "",
            "organization": args.org or "",
            "title": args.title or "",
            "website": args.website or "",
        }
        output = {"basename": f"QR {(args.name or 'contacto').strip()}"}

    vcard = build_vcard(contact)
    written = generate(vcard, output, Path(args.out))

    print("--- vCard generada ---")
    print(vcard)
    print()
    for p in written:
        print(f"{p}  ({p.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

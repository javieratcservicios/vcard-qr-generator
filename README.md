# vcard-qr-generator

**Genera un QR de contacto que se guarda solo en la agenda del teléfono.**
Escanear con la cámara → "Añadir contacto" → listo. Sin apps, sin escribir nada.

**Contact QR codes from a vCard 3.0 payload. Scan, add, done.**


![QR de contacto vCard 3.0 listo para escanear](docs/example-qr.png)

<sub>QR de contacto vCard 3.0 listo para escanear · vCard 3.0 contact QR code ready to scan</sub>

---

## Por qué existe

Compartir datos por WhatsApp es frágil: el otro tiene que copiar, pegar, guardar y corregir. Un QR con **vCard** resuelve el problema completo — la cámara del teléfono reconoce el formato y ofrece guardar el contacto con todos sus campos.

Y no hay que instalar nada: tanto iOS como Android leen vCard 3.0 de forma nativa desde la app de cámara.

## Características

- **vCard 3.0**, la versión con mejor compatibilidad universal (iOS, Android, macOS, Outlook)
- **Corrección de errores configurable** — por defecto nivel `h` (~30% de redundancia), aguanta que se manche o se tape parte del código
- **PNG y SVG** — PNG para compartir e imprimir, SVG para tamaño grande sin pixelarse
- **Escapado correcto** de caracteres reservados (`;`, `,`, `\`) — el error más común al generar vCards a mano
- **CRLF obligatorio** — vCard 3.0 lo exige; con `\n` algunos lectores ignoran campos
- **Teléfono de trabajo opcional** además del celular
- **UTF-8 forzado en el QR** — los acentos y la ñ llegan bien al teléfono
- **Solo con `--name` basta** — si no das nombre y apellidos por separado, se parten solos (primera palabra = nombre)
- **Colores y escala configurables**

## Instalación

```bash
git clone https://github.com/javieratcservicios/vcard-qr-generator.git
cd vcard-qr-generator
pip install segno
```

## Uso

### Desde un archivo de configuración

```bash
python vcard_qr.py --config examples/contact.example.json
```

```json
{
  "contact": {
    "first_name": "Ana",
    "last_name": "Martínez López",
    "display_name": "Ana Martínez",
    "organization": "Estudio Ejemplo",
    "title": "Gerencia Comercial",
    "phone": "+525512345678",
    "phone_work": "+525512340000",
    "email": "ana.martinez@ejemplo.mx",
    "website": "https://ejemplo.mx",
    "address": "Av. Reforma 123, Col. Centro, CDMX, CP 06000"
  },
  "output": {
    "basename": "QR Ana Martinez",
    "dark": "#1A237E",
    "light": "#FFFFFF",
    "scale": 14,
    "border": 4,
    "error_level": "h",
    "formats": ["png", "svg"]
  }
}
```

### Desde la línea de comandos

```bash
python vcard_qr.py \
  --name "Ana Martínez" \
  --phone +525512345678 \
  --email ana.martinez@ejemplo.mx \
  --org "Estudio Ejemplo" \
  --title "Gerencia Comercial" \
  --out ./qr
```

| Opción | Descripción |
|---|---|
| `--config` | JSON con contacto y opciones de salida |
| `--out` | Carpeta de salida (default: actual) |
| `--name` | Nombre completo a mostrar |
| `--first-name` / `--last-name` | Nombre y apellidos por separado |
| `--phone` | Celular con código de país, ej. `+525512345678` |
| `--email` | Correo electrónico |
| `--org` / `--title` | Organización y puesto |
| `--website` | Sitio web |
| `--phone-work` | Teléfono de oficina con código de país |
| `--address` | Dirección en una línea |

## Niveles de corrección de errores

| Nivel | Redundancia | Cuándo usarlo |
|---|---|---|
| `l` | ~7% | Etiquetas grandes impresas en interior |
| `m` | ~15% | Uso general |
| `q` | ~25% | Impresión pequeña o superficies curveadas |
| `h` | ~30% | **Default** — tolera manchas, logo al centro, daño parcial |

Si vas a poner un logo en el centro del QR, mantén `h` y no cubras más del 20% del área.

## Notas de operación

- **El teléfono debe llevar código de país.** `+528112345678`. Sin el `+52`, iOS en México a veces no marca bien.
- **`N:` y `FN:` son distintos.** `N` lleva los componentes separados por `;` (`Apellido;Nombre;;;`), `FN` el nombre a mostrar. Si solo pones uno, algunos lectores muestran el contacto en blanco.
- **No pongas foto en la vCard.** La mayoría de los lectores de QR no soporta `PHOTO` embebido en el payload y el código se vuelve ilegible por tamaño.
- **Prueba siempre con tu propio teléfono** antes de imprimir mil tarjetas.

## Licencia

MIT — ver [LICENSE](LICENSE).

---

## English

Generates contact QR codes from a vCard 3.0 payload. Scanning with the phone camera offers to save the contact directly — no app, no typing.

- vCard **3.0** for maximum compatibility (iOS, Android, macOS, Outlook)
- Error correction level `h` by default (~30% redundancy)
- PNG for sharing/printing, SVG for large formats
- Correct escaping of reserved characters and mandatory CRLF line endings

```bash
pip install segno
python vcard_qr.py --name "Ana Martinez" --phone +525512345678 --email ana@ejemplo.mx
```

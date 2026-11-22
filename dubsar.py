#!/usr/bin/env python3
"""
dubsar.py — Cálamo de bolsillo para la Tablilla de los 222 Me (Termux / Linux).

«Dub-sar» (sumerio: 𒁾𒊬, escriba de tablillas). Lee 'boolean4_atlas.csv'
(la Dub-nam-tar-ra de B4) y estampa en la terminal la tablilla de arcilla
de cualquiera de las 65.536 formas del Abzu booleano:
  - Su impronta 4x4 del mapa de Karnaugh en cuñas Unicode (██ / ░░).
  - Su polinomio algebraico legible (ANF / Zhegalkin) en A, B, C, D.
  - Su linaje exacto entre los 402 Ĝiš-ḫur (NP) y los 222 Me (NPN).
  - Un colofón poético 100 % determinista forjado desde sus propios bits.

Cero dependencias externas. Ajustado a 48 columnas para Termux.
"""

import argparse
import csv
import random
import sys
from pathlib import Path

DEFAULT_CSV = Path("boolean4_atlas.csv")

# Código Gray de 2 bits para ordenar filas (AB) y columnas (CD) del mapa
# de Karnaugh de modo que celdas vecinas solo cambien en un único cable.
GRAY_2 = (0, 1, 3, 2)
GRAY_LABELS = ("00", "01", "11", "10")

# Colofones deterministas inspirados en la cosmogonía sumeria arcaica
# (Nammu, An, Ki, Enlil, Enki, Ninmaḫ, Kulla, Utu, Ereškigal, Nisaba,
# Abgal y Gidim). Cada número de 16 bits recitará siempre la misma tablilla.
OPENING_BY_ORDER = {
    "nammu": (
        "Nammu en reposo: mar sin orilla ni nombre,",
        "Aguas mudas de Nammu antes de An y de Ki,",
    ),
    "an": (
        "Bóveda íntegra de An, luz sin una fisura,",
        "Cielo de An encendido en sus dieciséis sellos,",
    ),
    "enlil": (
        "Aliento de Enlil que aparta el Cielo de la Tierra,",
        "Viento de Enlil: si un cable tiembla, todo gira,",
    ),
    "abgal": (
        "Sabio Abgal surgido del fondo del Abzu,",
        "Cifra de los Abgal, jamás dócil al trazo recto,",
        "Voz de los Abgal: espectro plano en el abismo,",
    ),
    "kulla": (
        "Ladrillo de Kulla: lo cocido nunca vuelve al barro,",
        "Molde de Kulla que solo asciende hacia la luz,",
    ),
    "utu_kur": (
        "Paso de Utu hacia el Kur de Ereškigal,",
        "Espejo de Utu: día arriba, reverso bajo tierra,",
    ),
    "nisaba": (
        "Cálamo de Nisaba: solo cuenta espigas encendidas,",
        "Balanza de Nisaba, ciega al orden de los muros,",
    ),
    "eridu_cord": (
        "Cuerda tensa de Eridu, linde recto sin vértigo,",
        "Trazo de agrimensor sin curva en la arcilla,",
    ),
    "gidim": (
        "Gidim del Kur: habita cuatro muros e ignora una puerta,",
        "Sombra incompleta de un Gidim en el templo,",
    ),
    "clay": (
        "Arcilla de Ninmaḫ amasada en el borde del Abzu,",
        "Cuña anónima en la tablilla de los destinos,",
        "Barro cocido por Enki en un cosmos sin azar,",
        "Sello discreto del templo de Eridu,",
    ),
}

MIDDLE_BY_WEIGHT = (
    "sin una sola cuña encendida en su barro,",      # hw == 0
    "apenas una brasa solitaria en la penumbra,",    # hw 1..3
    "contadas luces que resisten el agua oscura,",   # hw 4..6
    "casi en vilo sobre el filo de la balanza,",     # hw == 7 o 9
    "ocho luces y ocho sombras en calma justa,",     # hw == 8
    "campo espeso de espigas con claros de sombra,", # hw 10..12
    "casi todo sol, salvo un rincón del Kur,",       # hw 13..15
    "sin una sola sombra que contradiga al cielo,",  # hw == 16
)

CLOSING_BY_COMPLEXITY = (
    "su decreto cabe en un solo golpe de cálamo.",   # terms <= 1
    "basta un puñado breve de puertas para grabarla.",# terms 2..3
    "exige pulso firme sobre la arcilla húmeda.",    # terms 4..5
    "ningún dub-sar logra acortar su tablilla.",     # terms >= 6
)

ORDERS_HELP = (
    "abgal, kulla, utu_kur, nisaba, eridu, gidim, balanced, enlil, solitary"
)


def parse_func_id(raw: str) -> int:
    """Acepta decimal (27030), hexadecimal (0x6996 o 6996) o binario (16 bits)."""
    s = raw.strip()
    if not s:
        raise ValueError("Identificador vacío.")

    low = s.lower()
    if low.startswith("0x"):
        val = int(low, 16)
    elif low.startswith("0b"):
        val = int(low, 2)
    elif len(s) == 16 and set(s) <= {"0", "1"}:
        val = int(s, 2)
    elif any(ch in "abcdef" for ch in low):
        val = int(low, 16)
    else:
        val = int(s, 10)

    if not (0 <= val <= 65535):
        raise ValueError(f"Fuera del Abzu B4 (0..65535): {raw}")
    return val


def decode_anf(anf_hex: str) -> str:
    """Traduce la máscara hexadecimal ANF al polinomio de Zhegalkin en A,B,C,D."""
    anf_int = int(anf_hex, 16)
    if anf_int == 0:
        return "0"

    terms = []
    for mask in range(16):
        if (anf_int >> mask) & 1:
            if mask == 0:
                terms.append((0, "1"))
            else:
                name = "".join(
                    ch for b, ch in enumerate("ABCD") if (mask >> (3 - b)) & 1
                )
                terms.append((len(name), name))

    # Orden canónico: primero por grado (0..4) y luego alfabéticamente (A, B, C, D).
    terms.sort(key=lambda item: (item[0], item[1]))
    return " ⊕ ".join(name for _, name in terms)


def render_tablet(f: int) -> list[str]:
    """Estampa el mapa de Karnaugh 4x4 (filas AB, columnas CD en código Gray)."""
    lines = [
        "       CD",
        "   AB  00 01 11 10",
        "      ┌───────────┐",
    ]
    for r_lbl, ab in zip(GRAY_LABELS, GRAY_2):
        cells = []
        for cd in GRAY_2:
            idx = (ab << 2) | cd
            bit = (f >> idx) & 1
            cells.append("██" if bit else "░░")
        lines.append(f"   {r_lbl} │{' '.join(cells)}│")
    lines.append("      └───────────┘")
    return lines


def load_tablet(csv_path: Path) -> tuple[list[dict], dict[int, int]]:
    """Carga la Dub-nam-tar-ra (CSV) y mide la órbita exacta de cada Me (NPN)."""
    if not csv_path.exists():
        print(
            f"Error: no encuentro '{csv_path}'. "
            "Ejecuta primero: python3 build_boolean4_atlas.py",
            file=sys.stderr,
        )
        sys.exit(1)

    rows = []
    orbit_sizes: dict[int, int] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            cid = int(row["npn_class_id"])
            orbit_sizes[cid] = orbit_sizes.get(cid, 0) + 1
            rows.append(row)

    if len(rows) != 65536:
        print(
            f"Aviso: la tablilla tiene {len(rows)} filas (se esperaban 65.536).",
            file=sys.stderr,
        )
    return rows, orbit_sizes


def matches_order(row: dict, orbit_size: int, order: str) -> bool:
    """Filtra sellos según su linaje en la cosmogonía sumeria."""
    sp = order.lower().replace("-", "_")
    f = int(row["func_id_dec"])
    if sp in ("abgal", "bent"):
        return row["is_bent"] == "1"
    if sp in ("kulla", "monotone"):
        return row["is_monotone"] == "1"
    if sp in ("utu_kur", "utu", "self_dual"):
        return row["is_self_dual"] == "1"
    if sp in ("nisaba", "symmetric"):
        return row["is_symmetric"] == "1"
    if sp in ("eridu", "affine"):
        return row["is_affine"] == "1"
    if sp == "balanced":
        return row["is_balanced"] == "1"
    if sp in ("gidim", "impostor"):
        return int(row["essential_vars"]) < 4
    if sp == "enlil":
        return f in (0x6996, 0x9669)
    if sp in ("solitary", "hermit"):
        return orbit_size == 2
    raise ValueError(f"Linaje desconocido '{order}'. Opciones: {ORDERS_HELP}")


def get_seals(row: dict, orbit_size: int) -> list[str]:
    """Construye los sellos cosmogónicos visibles en la tablilla."""
    f = int(row["func_id_dec"])
    seals = []
    if f == 0x0000:
        seals.append("NAMMU")
    elif f == 0xFFFF:
        seals.append("AN")
    elif f in (0x6996, 0x9669):
        seals.append("ENLIL")

    if orbit_size == 2:
        seals.append("ME SOLITARIO")
    if row["is_bent"] == "1":
        seals.append("ABGAL")
    if row["is_monotone"] == "1":
        seals.append("KULLA")
    if row["is_balanced"] == "1":
        seals.append("EQUILIBRADA")
    if row["is_self_dual"] == "1":
        seals.append("UTU-KUR")
    if row["is_symmetric"] == "1":
        seals.append("NISABA")
    if row["is_affine"] == "1":
        seals.append("CUERDA DE ERIDU")
    if int(row["essential_vars"]) < 4:
        seals.append("GIDIM")
    if not seals:
        seals.append("ARCILLA DE NINMAḪ")
    return seals


def build_colophon(row: dict) -> list[str]:
    """Graba un colofón de tres versos 100 % determinista desde los bits."""
    f = int(row["func_id_dec"])
    hw = int(row["hamming_weight"])
    terms = int(row["min_sop_terms"])
    ess = int(row["essential_vars"])

    # 1) Verso de apertura según la jerarquía sumeria dominante.
    if f == 0x0000:
        arch = "nammu"
    elif f == 0xFFFF:
        arch = "an"
    elif f in (0x6996, 0x9669):
        arch = "enlil"
    elif row["is_bent"] == "1":
        arch = "abgal"
    elif row["is_monotone"] == "1":
        arch = "kulla"
    elif row["is_self_dual"] == "1":
        arch = "utu_kur"
    elif row["is_symmetric"] == "1":
        arch = "nisaba"
    elif row["is_affine"] == "1":
        arch = "eridu_cord"
    elif ess < 4:
        arch = "gidim"
    else:
        arch = "clay"

    pool = OPENING_BY_ORDER[arch]
    line1 = pool[(f ^ (f >> 8)) % len(pool)]

    # 2) Verso central según el peso de Hamming (cuñas encendidas).
    if hw == 0:
        w_idx = 0
    elif hw <= 3:
        w_idx = 1
    elif hw <= 6:
        w_idx = 2
    elif hw in (7, 9):
        w_idx = 3
    elif hw == 8:
        w_idx = 4
    elif hw <= 12:
        w_idx = 5
    elif hw <= 15:
        w_idx = 6
    else:
        w_idx = 7
    line2 = MIDDLE_BY_WEIGHT[w_idx]

    # 3) Verso de cierre según la irreductibilidad en Suma de Productos.
    if terms <= 1:
        c_idx = 0
    elif terms <= 3:
        c_idx = 1
    elif terms <= 5:
        c_idx = 2
    else:
        c_idx = 3
    line3 = CLOSING_BY_COMPLEXITY[c_idx]

    return [line1, line2, line3]


def wrap_text(text: str, width: int = 44, prefix: str = "  ") -> list[str]:
    """Ajusta líneas largas para pantalla estrecha de Termux."""
    words = text.split()
    if not words:
        return [prefix]
    lines, curr = [], words[0]
    for w in words[1:]:
        if len(curr) + 1 + len(w) <= width:
            curr += " " + w
        else:
            lines.append(prefix + curr)
            curr = w
    lines.append(prefix + curr)
    return lines


def print_tablet(row: dict, orbit_size: int, show_colophon: bool = True) -> None:
    """Imprime la tablilla de arcilla completa en la terminal."""
    f = int(row["func_id_dec"])
    seals = get_seals(row, orbit_size)
    anf_expr = decode_anf(row["anf_hex"])
    sep = "═" * 48
    thin = "─" * 48

    print(sep)
    print(f" TABLILLA {row['func_id_hex']}  (#{f})  |  ME #{row['npn_class_id']} (órbita: {orbit_size})")
    print(thin)
    for line in wrap_text(" ".join(f"[{s}]" for s in seals), width=44, prefix=" "):
        print(line)
    print(f" Cuñas:     {row['truth_table_bin']}  (peso {row['hamming_weight']}/16)")
    print()

    for line in render_tablet(f):
        print(line)

    print()
    print(f" Trazo:     Ĝiš-ḫur {row['np_canonical_hex']}  |  Me {row['npn_canonical_hex']}")
    print(f" Puertas:   {row['essential_vars']}/4 activas  |  Sensib.: {row['avg_sensitivity']}")
    print(f" Espectro:  Grado {row['algebraic_degree']}  |  NL {row['nonlinearity']}  |  Walsh máx {row['walsh_max_abs']}")
    print(f" Min SOP:   {row['min_sop_terms']} términos, {row['min_sop_literals']} literales")
    print(" ANF:")
    for line in wrap_text(anf_expr, width=44, prefix="   "):
        print(line)

    if show_colophon:
        print(thin)
        verses = build_colophon(row)
        print(f"  «{verses[0]}")
        print(f"   {verses[1]}")
        print(f"   {verses[2]}»")
    print(sep)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dub-sar: visor de bolsillo para la Tablilla de los 222 Me (boolean4_atlas.csv)."
    )
    parser.add_argument(
        "seal",
        nargs="?",
        help="ID en hex (0x6996), decimal (27030) o binario (16 bits).",
    )
    parser.add_argument(
        "-r", "--random",
        action="store_true",
        help="Extrae una tablilla al azar del Abzu (o del linaje filtrado).",
    )
    parser.add_argument(
        "-o", "--order",
        help=f"Filtra por linaje sumerio al usar --random ({ORDERS_HELP}).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Semilla opcional para reproducir una extracción --random.",
    )
    parser.add_argument(
        "--no-colophon",
        action="store_true",
        help="Muestra solo la ficha técnica sin el colofón poético.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Ruta al archivo boolean4_atlas.csv.",
    )
    args = parser.parse_args()

    if not args.seal and not args.random and not args.order:
        parser.print_help()
        print("\nEjemplos rápidos:")
        print("  python3 dubsar.py 0x6996")
        print("  python3 dubsar.py --random")
        print("  python3 dubsar.py --random --order abgal")
        sys.exit(0)

    rows, orbit_sizes = load_tablet(args.csv)

    if args.seal:
        try:
            fid = parse_func_id(args.seal)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        row = rows[fid]
        cid = int(row["npn_class_id"])
        print_tablet(row, orbit_sizes[cid], show_colophon=not args.no_colophon)
        return

    if args.order:
        try:
            candidates = [
                r for r in rows
                if matches_order(r, orbit_sizes[int(r["npn_class_id"])], args.order)
            ]
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        if not candidates:
            print("No hay tablillas en el Abzu que cumplan ese filtro.", file=sys.stderr)
            sys.exit(1)
    else:
        candidates = rows

    rng = random.Random(args.seed)
    row = rng.choice(candidates)
    cid = int(row["npn_class_id"])
    print_tablet(row, orbit_sizes[cid], show_colophon=not args.no_colophon)


if __name__ == "__main__":
    main()

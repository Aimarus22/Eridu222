#!/usr/bin/env python3
"""
build_boolean4_atlas.py — Horno portátil para la Tablilla de los 222 Me (B4).

Cuatro puertas (A, B, C, D) abren dieciséis estados posibles. Cada sello del
Abzu booleano graba una cuña encendida (1) o en sombra (0) en esas dieciséis
casillas: una impronta 16 bits, un sino entre 65.536 posibles destinos.

En román paladino: este script no importa librerías externas ni
adivina nada. Recorre una por una las 65.536 funciones booleanas de 4
variables, mide sus propiedades lógicas, criptográficas y de circuito, las
ordena en sus 402 Ĝiš-ḫur (NP) y 222 Me (NPN), exige que las cuentas de Nisaba
cuadren contra los teoremas clásicos y cuece la Dub-nam-tar-ra (CSV) con un
sello SHA-256 inmutable.
"""

# Herramientas desnudas del dub-sar (biblioteca estándar de Python, cero extras):
# - hashlib: el sello cilíndrico criptográfico que lacra la tablilla bit a bit.
# - time: el reloj de agua que mide cuántos segundos tarda en cocerse el Abzu.
# - permutations: para permutar las cuatro puertas de entrada (4! = 24 órdenes).
# - Path: para tocar el disco con limpieza sin pelearse con rutas de sistema.
import hashlib
import time
from itertools import permutations
from pathlib import Path

# La Dub-nam-tar-ra (Tablilla de los Destinos) donde se cuecen las 65.536 formas.
OUT_FILE = Path("boolean4_atlas.csv")


def build_np_luts():
    """Precalcula LUTs de 8 bits para los 384 reflejos de un Ĝiš-ḫur (NP: 4! * 2^4)."""
    # =========================================================================
    # LOS 384 ESPEJOS DEL ABZU
    # -------------------------------------------------------------------------
    # Si a una tablilla le cambias las cuatro puertas de sitio (Permutación:
    # 24 formas) o inviertes algunas entradas (Negación: 16 formas), parece
    # otra... pero sigue trazada sobre el mismo plano primordial (Ĝiš-ḫur).
    # En total existen 24 x 16 = 384 reflejos posibles.
    #
    # El truco práctico (para que el móvil no se fría):
    # En vez de girar 65.536 tablillas bit a bit por 384 reflejos, partimos
    # cada sello de 16 bits en dos mitades de 8 bits (byte bajo y byte alto).
    # Precalculamos a dónde viaja cada mitad (solo 256 casos) y recomponemos
    # el sello transformado de un solo golpe con un OR (|).
    # =========================================================================
    luts = []
    # Probamos cada orden posible de las 4 puertas (A, B, C, D).
    for perm in permutations(range(4)):
        # Probamos cada máscara de 4 bits que decide qué puertas entran invertidas.
        for neg_mask in range(16):
            # Mapa inverso: anota en qué casilla nueva aterriza cada cuña vieja.
            inv_map = [0] * 16
            for i in range(16):
                # Desempaquetamos el índice 'i' (0..15) en sus 4 puertas binarias.
                xb = [(i >> (3 - b)) & 1 for b in range(4)]
                j = 0
                for k in range(4):
                    # Reordenamos la puerta y, si la máscara manda, volteamos
                    # la cuña con un golpe XOR (^).
                    bit = xb[perm[k]] ^ ((neg_mask >> (3 - k)) & 1)
                    j = (j << 1) | bit
                inv_map[j] = i
            # Dos tablas de atajo (LUTs): una para los 8 bits bajos, otra para los altos.
            lut_lo = [0] * 256
            lut_hi = [0] * 256
            for byte in range(256):
                r0 = r1 = 0
                for b in range(8):
                    # Si esta cuña arde en 1, la estampamos en su nueva casilla.
                    if (byte >> b) & 1:
                        r0 |= 1 << inv_map[b]
                        r1 |= 1 << inv_map[b + 8]
                lut_lo[byte] = r0
                lut_hi[byte] = r1
            luts.append((lut_lo, lut_hi))
    return luts


def exact_min_sop(f: int) -> tuple[int, int]:
    """Quine-McCluskey + cobertura exacta (minimiza términos, luego literales)."""
    # =========================================================================
    # EL CÁLAMO DE QUINE-McCLUSKEY 
    # -------------------------------------------------------------------------
    # Toda tablilla puede escribirse como una lista de condiciones que la
    # encienden (Suma de Productos / SOP), pero a esa lista bruta suele sobrarle
    # arcilla. Aquí tallamos hasta el tuétano arcíllico para hallar el mínimo exacto
    # de términos (puertas AND) y de cables (literales) irreductibles.
    # =========================================================================

    # Dos extremos primordiales fuera de talla:
    # - 0x0000 es Nammu: mar mudo sin una sola cuña (0 puertas, 0 cables).
    # - 0xFFFF es An: bóveda íntegra sin sombra (1 constante viva, 0 cables).
    if f == 0:
        return 0, 0
    if f == 0xFFFF:
        return 1, 0

    # 1) Recogemos los "minterms": las casillas exactas donde la cuña está en 1.
    minterms = [i for i in range(16) if (f >> i) & 1]
    # Cada bloque se guarda como (valor, máscara_comodín). Al nacer, sin comodines (0).
    current = {(m, 0) for m in minterms}
    # Aquí caerán los "implicantes primos": trazos imposibles de fundir más.
    primes = set()

    # 2) Fusión por vecindad sobre la cuadrícula de Karnaugh:
    # Si dos casillas encendidas solo difieren en UNA puerta, esa puerta no
    # decide nada y se vuelve comodín ("da igual si entra 0 o 1").
    while current:
        used, nxt = set(), set()
        cl = list(current)
        for i in range(len(cl)):
            v1, m1 = cl[i]
            for j in range(i + 1, len(cl)):
                v2, m2 = cl[j]
                if m1 == m2:
                    # Truco clásico de bits: (diff & (diff - 1)) == 0 solo es
                    # cierto si 'diff' tiene un único bit a 1 (difieren en 1 bit).
                    diff = v1 ^ v2
                    if diff and (diff & (diff - 1)) == 0:
                        used.add((v1, m1))
                        used.add((v2, m2))
                        nxt.add((v1 & ~diff, m1 | diff))
        # Todo lo que no pudo fusionarse en esta ronda es un trazo irreductible.
        primes |= current - used
        current = nxt

    # 3) Anotamos qué unos cubre cada implicante primo y cuántos cables exige.
    mt_idx = {m: idx for idx, m in enumerate(minterms)}
    full_mask = (1 << len(minterms)) - 1
    pi_info = []
    for val, mask in primes:
        cov = 0
        for m in minterms:
            if (m & ~mask) == val:
                cov |= 1 << mt_idx[m]
        # Sin comodines cuesta 4 cables; cada comodín ahorra una entrada.
        pi_info.append((cov, 4 - mask.bit_count()))

    # 4) Implicantes esenciales: si una cuña en 1 solo tiene un bloque capaz
    # de cubrirla, ese trazo es impepinable y entra el primero en la tablilla.
    essential = set()
    covered = 0
    for idx_m in range(len(minterms)):
        bit = 1 << idx_m
        owners = [i for i, (cov, _) in enumerate(pi_info) if cov & bit]
        if len(owners) == 1:
            essential.add(owners[0])

    for i in essential:
        covered |= pi_info[i][0]

    # ¿Queda alguna cuña sin cubrir? Si no queda ninguna, fin de la talla.
    rem = full_mask & ~covered
    if rem == 0:
        return len(essential), sum(pi_info[i][1] for i in essential)

    # 5) Búsqueda exacta para los huecos rebeldes:
    # Ordenamos los candidatos poniendo primero los que cubren más unos con
    # menos literales y exploramos el árbol podando cualquier rama seca.
    cands = [
        (cov & rem, lits)
        for i, (cov, lits) in enumerate(pi_info)
        if i not in essential and (cov & rem)
    ]
    cands.sort(key=lambda x: (-x[0].bit_count(), x[1]))
    best = [999, 999]

    def dfs(uncov: int, t_cnt: int, l_cnt: int):
        # Poda seca: si esta rama ya empata o empeora el mínimo, media vuelta.
        if t_cnt > best[0] or (t_cnt == best[0] and l_cnt >= best[1]):
            return
        # Si ya cubrimos hasta la última cuña, fijamos nuevo récord exacto.
        if uncov == 0:
            best[0], best[1] = t_cnt, l_cnt
            return
        # Elegimos siempre la cuña más difícil de tapar (menos candidatos) para
        # cerrar el laberinto en milisegundos.
        best_opts = None
        tmp = uncov
        while tmp:
            # Truco de bits: (tmp & -tmp) aísla el bit menos significativo a 1.
            lsb = tmp & -tmp
            opts = [c for c in cands if c[0] & lsb]
            if best_opts is None or len(opts) < len(best_opts):
                best_opts = opts
                if len(opts) <= 1:
                    break
            tmp ^= lsb
        for eff, lits in best_opts:
            dfs(uncov & ~eff, t_cnt + 1, l_cnt + lits)

    dfs(rem, 0, 0)
    return len(essential) + best[0], sum(pi_info[i][1] for i in essential) + best[1]


def main():
    # Encendemos el horno de Eridu y activamos el reloj. Se abre el telón.
    t0 = time.perf_counter()

    # =========================================================================
    # ACTO I: EL CENSO DEL ABZU
    # -------------------------------------------------------------------------
    # Recorremos las 65.536 formas de 0x0000 a 0xFFFF. Cada vez que hallamos
    # una inédita, la consagramos como arquetipo canónico y marcamos toda su
    # órbita a través de los 384 espejos.
    # - NP (Ĝiš-ḫur): permutar y negar puertas reduce el Abzu a 402 planos.
    # - NPN (Me): si además invertimos la salida (f ^ 0xFFFF, día y noche
    #   como el paso de Utu por el Kur), todo colapsa en los 222 Me eternos.
    # =========================================================================
    print("[1/4] Precalculando órbitas NP (402) y NPN (222)...")
    luts = build_np_luts()
    np_canon = [-1] * 65536
    npn_canon = [-1] * 65536
    np_classes, npn_classes = [], []

    for f in range(65536):
        if np_canon[f] == -1:
            np_classes.append(f)
            lo, hi = f & 0xFF, f >> 8
            for l0, l1 in luts:
                np_canon[l0[lo] | l1[hi]] = f

    for f in range(65536):
        if npn_canon[f] == -1:
            npn_classes.append(f)
            # Probamos tanto la tablilla diurna como su reverso en el Kur.
            for src in (f, f ^ 0xFFFF):
                lo, hi = src & 0xFF, src >> 8
                for l0, l1 in luts:
                    npn_canon[l0[lo] | l1[hi]] = f

    # Si los números sagrados de la simetría no cuadran, se detiene la cocción.
    assert len(np_classes) == 402, f"Error NP: {len(np_classes)}"
    assert len(npn_classes) == 222, f"Error NPN: {len(npn_classes)}"

    # =========================================================================
    # ACTO II: LA ECONOMÍA DEL DUB-SAR
    # -------------------------------------------------------------------------
    # Permutar o negar puertas NO altera cuántas puertas AND ni cuántos
    # literales exige el circuito mínimo (es un invariante de cada Ĝiš-ḫur).
    # En vez de tallar 65.536 tablillas, tallamos solo los 402 arquetipos NP y
    # cada forma hereda la medida exacta de su plano primordial.
    # =========================================================================
    print("[2/4] Resolviendo Quine-McCluskey exacto en las 402 clases NP...")
    sop_by_np = {f: exact_min_sop(f) for f in np_classes}
    npn_id_map = {f: idx + 1 for idx, f in enumerate(npn_classes)}

    # Preparamos las aristas del hipercubo de 4 dimensiones para la Obra de Kulla:
    # cada pareja (u, v) donde 'v' enciende exactamente una puerta más que 'u'.
    mono_pairs = [
        (i, i | (1 << b))
        for i in range(16)
        for b in range(4)
        if not (i & (1 << b))
    ]
    # Agrupamos las 16 casillas por número de puertas encendidas (0..4) para
    # reconocer las Cañas de Nisaba (simétricas: solo cuentan espigas).
    weight_buckets = [[i for i in range(16) if i.bit_count() == w] for w in range(5)]
    # Las cuatro máscaras individuales de las puertas: 0001, 0010, 0100, 1000.
    var_masks = [1 << b for b in range(4)]

    # =========================================================================
    # ACTO III: LA COCCIÓN UNA A UNA
    # -------------------------------------------------------------------------
    # Abrimos el archivo en modo binario ("wb") para fijar saltos de línea Unix
    # puros (LF) sin contaminación; cada byte grabado en la arcilla pasa en
    # paralelo por el sello cilíndrico del SHA-256.
    # =========================================================================
    print(f"[3/4] Calculando invariantes y escribiendo {OUT_FILE}...")
    stats = {"bent": 0, "mono": 0, "sdual": 0, "sym": 0, "aff": 0}
    sha = hashlib.sha256()

    header = (
        "func_id_dec,func_id_hex,truth_table_bin,hamming_weight,"
        "essential_vars,avg_sensitivity,algebraic_degree,anf_hex,"
        "walsh_max_abs,nonlinearity,min_sop_terms,min_sop_literals,"
        "np_canonical_hex,npn_class_id,npn_canonical_hex,"
        "is_balanced,is_monotone,is_self_dual,is_symmetric,is_affine,is_bent\n"
    )

    with OUT_FILE.open("wb") as fh:
        hb = header.encode("utf-8")
        fh.write(hb)
        sha.update(hb)

        for f in range(65536):
            # Peso de Hamming: cuántas cuñas encendidas (1) guarda en 16 bits.
            hw = f.bit_count()

            # --- Prueba de puertas: Variables esenciales y Sensibilidad ---
            # Golpeamos cada una de las 4 puertas en sus 8 parejas posibles.
            # Si la tablilla jamás cambia al mover una puerta, esa pared es
            # hueca: estamos ante un Gidim (espectro con menos de 4 variables).
            # La sensibilidad media mide cuántas puertas, de media, la hacen
            # volcar (alcanza 4.0000 en Enlil: 0x6996 y 0x9669).
            ess = 0
            total_flips = 0
            for vm in var_masks:
                flips = 0
                for i in range(16):
                    if not (i & vm):
                        if ((f >> i) & 1) != ((f >> (i | vm)) & 1):
                            flips += 1
                if flips:
                    ess += 1
                    total_flips += flips
            avg_sens = total_flips / 8.0

            # --- Lectura algebraica: Transformada rápida de Möbius (ANF) ---
            # Traduce las 16 cuñas al polinomio de Zhegalkin (solo sumas XOR y
            # productos AND). El término que enlaza más letras a la vez marca
            # el "grado algebraico" (0..4): la curvatura interna del decreto.
            a = [(f >> i) & 1 for i in range(16)]
            for b in range(4):
                step = 1 << b
                for i in range(16):
                    if i & step:
                        a[i] ^= a[i ^ step]
            anf_int = 0
            deg = 0
            for i in range(16):
                if a[i]:
                    anf_int |= 1 << i
                    w = i.bit_count()
                    if w > deg:
                        deg = w

            # --- Sondeo espectral: Transformada rápida de Walsh-Hadamard ---
            # Traduce 0/1 a +1/-1 y contrasta la tablilla contra todas las
            # cuerdas rectas posibles (un Fourier discreto sobre B4). Cuanto
            # menor es el pico máximo (w_max), más lejos vive la forma del
            # trazo afín; en el límite plano (w_max = 4, nl = 6) moran los Abgal.
            w = [1 - 2 * ((f >> i) & 1) for i in range(16)]
            for b in range(4):
                step = 1 << b
                for i in range(0, 16, step * 2):
                    for j in range(i, i + step):
                        u, v = w[j], w[j + step]
                        w[j] = u + v
                        w[j + step] = u - v
            w_max = max(abs(x) for x in w)
            nl = 8 - (w_max >> 1)

            # --- Los 6 sellos de la Teogonía del Abzu (1 = sí, 0 = no) ---
            # Equilibrada: ocho cuñas encendidas y ocho en sombra (balanza justa).
            is_bal = hw == 8
            # Obra de Kulla (monótona): ladrillo cocido que nunca vuelve al barro.
            is_mono = all(((f >> u) & 1) <= ((f >> v) & 1) for u, v in mono_pairs)
            # Paso de Utu por el Kur (autodual): su reverso nocturno niega el día.
            is_sdual = all(((f >> (15 - i)) & 1) != ((f >> i) & 1) for i in range(8))
            # Cañas de Nisaba (simétrica): ciega al orden, solo pesa espigas.
            is_sym = all(len({(f >> i) & 1 for i in bkt}) == 1 for bkt in weight_buckets)
            # Cuerda de Eridu (afín): linde recto, grado <= 1 y nl == 0.
            is_aff = deg <= 1
            # Los Abgal (bent): sabios crípticos de espectro plano (nl == 6).
            is_bent = nl == 6

            # Anotamos el recuento de cada linaje para el cierre del Acto IV.
            if is_bent: stats["bent"] += 1
            if is_mono: stats["mono"] += 1
            if is_sdual: stats["sdual"] += 1
            if is_sym: stats["sym"] += 1
            if is_aff: stats["aff"] += 1

            # Heredamos Ĝiš-ḫur, Me canónico y talla mínima precalculada.
            npc = np_canon[f]
            npnc = npn_canon[f]
            terms, lits = sop_by_np[npc]

            # Estampamos la línea en el CSV y actualizamos el sello SHA-256.
            row = (
                f"{f},0x{f:04X},{f:016b},{hw},"
                f"{ess},{avg_sens:.4f},{deg},0x{anf_int:04X},"
                f"{w_max},{nl},{terms},{lits},"
                f"0x{npc:04X},{npn_id_map[npnc]},0x{npnc:04X},"
                f"{int(is_bal)},{int(is_mono)},{int(is_sdual)},"
                f"{int(is_sym)},{int(is_aff)},{int(is_bent)}\n"
            ).encode("utf-8")
            fh.write(row)
            sha.update(row)

    # =========================================================================
    # ACTO IV: LAS CUENTAS DE NISABA
    # -------------------------------------------------------------------------
    # Aquí no existe el "más o menos". Antes de dar la tablilla por cocida,
    # el script rinde cuentas ante las constantes exactas de B4: 896 Abgal
    # (bent), 168 ladrillos de Kulla (Dedekind M(4)), 256 pasos de Utu-Kur
    # (autoduales), 32 cañas de Nisaba (simétricas) y 32 cuerdas de Eridu
    # (afines). Si baila un solo bit, se rompe el molde.
    # =========================================================================
    print("[4/4] Ejecutando auditoría de invariantes teóricos...")
    assert stats["bent"] == 896, f"Bent mismatch: {stats['bent']}"
    assert stats["mono"] == 168, f"Dedekind M(4) mismatch: {stats['mono']}"
    assert stats["sdual"] == 256, f"Self-dual mismatch: {stats['sdual']}"
    assert stats["sym"] == 32, f"Symmetric mismatch: {stats['sym']}"
    assert stats["aff"] == 32, f"Affine mismatch: {stats['aff']}"

    elapsed = time.perf_counter() - t0
    size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
    print(f"OK | 65.536 filas generadas en {elapsed:.2f}s ({size_mb:.2f} MB)")
    print(f"SHA-256: {sha.hexdigest()}")


# Si alguien invoca este horno directamente en la terminal, que empiece la cocción.
if __name__ == "__main__":
    main()

"""
pdf_to_dict.py
==============
Extraction PDF → dictionnaire structuré pour l'auto-remplissage.
Source unique : le fichier PDF des comptes annuels.

Mapping page PDF → clé JSON :
  page 6  (I. Prospectus)          → "prospectus"
  page 7  (I. Caractéristiques)    → "caracteristiques"
  pages 8-9 (II. Règlement)        → "copie_reglement"
  page 11 (IV. Evol parts)         → "evol_parts"
  pages 13-14 (VI. Ventilation AN) → "ventilation_an"
"""

from __future__ import annotations
import re, io
import pdfplumber


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _page_text_clean(page, space_threshold: float = 1.0) -> str:
    """
    Reconstruit le texte d'une page en insérant des espaces aux endroits où
    les caractères sont séparés par un gap > space_threshold pt.

    Nécessaire car certains PDF générés par Excel/macro encodent le texte
    justifié sans espaces entre les mots — les espaces sont simulés par
    le positionnement des glyphes. pdfplumber.extract_text() restitue alors
    des mots collés. Cette fonction corrige ce problème au niveau caractère.
    """
    chars = page.chars
    if not chars:
        return ""

    # Grouper les caractères par ligne (y arrondi au pt)
    lines: dict[int, list] = {}
    for char in chars:
        y_key = round(char["top"])
        lines.setdefault(y_key, []).append(char)

    result_lines = []
    for y in sorted(lines):
        line_chars = sorted(lines[y], key=lambda c: c["x0"])
        text = ""
        for i, char in enumerate(line_chars):
            if i == 0:
                text += char["text"]
            else:
                prev = line_chars[i - 1]
                gap = char["x0"] - prev["x1"]
                # Insérer un espace si :
                #   - le gap est supérieur au seuil
                #   - aucun des deux caractères n'est déjà un espace
                if gap > space_threshold and char["text"] != " " and prev["text"] != " ":
                    text += " "
                text += char["text"]
        result_lines.append(text)

    return "\n".join(result_lines)


def _get_pages(pdf_bytes: bytes) -> list[str]:
    """
    Retourne le texte reconstruit de chaque page (index 0 = page 1).
    Utilise _page_text_clean pour corriger les mots collés dus aux ligatures
    PDF générés par Excel avec justification de texte.
    """
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return [_page_text_clean(p) for p in pdf.pages]


def _get_tables(pdf_bytes: bytes, page_index: int) -> list[list[list]]:
    """Retourne les tableaux détectés sur une page donnée (0-indexé)."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return pdf.pages[page_index].extract_tables()


def _norm(s: str) -> str:
    """Normalise apostrophes typographiques → droites pour la recherche."""
    return s.replace("\u2019", "'").replace("\u2018", "'").replace("\u2032", "'")


def _full(pages: list[str]) -> str:
    ft = "\n".join(pages)
    ft = re.sub(r"Page\s+\d+\s+sur\s+\d+", "", ft)
    ft = re.sub(r"[^\n]+FPCI\s*[-–]\s*Comptes annuels au \d{2}/\d{2}/\d{4}", "", ft)
    return ft


def _between(text: str, start: str, end: str) -> str:
    tn, sn, en = _norm(text.lower()), _norm(start.lower()), _norm(end.lower())
    i = tn.find(sn)
    if i == -1:
        return ""
    i += len(sn)
    j = tn.find(en, i)
    return text[i: j if j != -1 else len(text)].strip()


def _clean_num(s: str) -> str | None:
    """Nettoie une valeur numérique PDF (espaces insécables, virgule décimale)."""
    if s is None:
        return None
    s = s.strip().replace("\u202f", "").replace("\u00a0", "").replace(" ", "")
    if s in ("-", "–", ""):
        return None
    return s.replace(",", ".")


def _parse_num(s: str) -> float | int | None:
    c = _clean_num(s)
    if c is None:
        return None
    try:
        f = float(c)
        return int(f) if f == int(f) else f
    except ValueError:
        return c


def _split_cell(cell: str) -> list[str]:
    """Découpe une cellule multi-lignes PDF en liste de valeurs."""
    if cell is None:
        return []
    return [l.strip() for l in cell.split("\n") if l.strip()]


# ─── prospectus ───────────────────────────────────────────────────────────────

def _parse_prospectus(pages: list[str]) -> dict:
    """
    Page 6 du PDF — onglet source : I. Prospectus
    Extrait :
      - titre_0       : "ANNEXE AUX COMPTES ANNUELS"
      - titre_section : "I. Caractéristiques et activité de l'OPC"
      - section_1_1   : { titre, texte }
    """
    ft = _full(pages)

    TITRE_0   = "ANNEXE AUX COMPTES ANNUELS"
    TITRE_I   = "I. Caractéristiques et activité de l'OPC"
    TITRE_1_1 = "1.1 - Informations relatives à la stratégie de l'OPC ainsi que les stratégies de gestion du risque afférentes"
    STOP      = "1.2 - Eléments caractéristiques"

    return {
        "titre_0":       TITRE_0,
        "titre_section": TITRE_I,
        "section_1_1": {
            "titre": TITRE_1_1,
            "texte": _between(ft, TITRE_1_1, STOP),
        },
    }


# ─── caracteristiques ─────────────────────────────────────────────────────────

def _parse_caracteristiques(pdf_bytes: bytes, pages: list[str]) -> dict:
    """
    Page 7 du PDF — onglet source : I. Caractéristiques

    pdfplumber.extract_tables() retourne 1 tableau avec 5 rows :
      row 0 : colonnes  [Libellé | date1..date5]
      row 1 : Actif net
      row 2 : groupe Parts A   (col0 = libellés \n-séparés, cols 1-5 = valeurs \n-séparées)
      row 3 : groupe Parts A'
      row 4 : groupe Parts B

    Dans col0 de chaque groupe, les libellés sont dans l'ordre fixe :
      Engagement de souscription | Montant libéré | Répartition d'avoirs* |
      Nombre de parts | Distribution revenu net | Distribution PVMV réal | Valeur liquidative
      (+ Distribution PVMV latentes pour Parts B)

    Les colonnes de valeurs contiennent 4 ou 5 valeurs selon si "Répartition d'avoirs*"
    est présente ("-") ou absente (None). On normalise toujours à 5 valeurs.

    Les valeurs "-" dans le PDF signifient None (pas de distribution/répartition).
    """
    ft    = _full(pages)
    TITRE = "1.2 - Eléments caractéristiques de l'OPC au cours des cinq derniers exercices en euros"
    STOP  = "II. Règles et méthodes comptables"

    # Positions fixes des libellés qui ont des valeurs dans le tableau PDF
    POSITIONS_AVEC_VALEUR = {
        "Engagement de souscription": 0,
        "Montant libéré":             1,
        "Répartition d'avoirs*":      2,
        "Nombre de parts":            3,
        "Valeur liquidative":         4,
    }

    def _parse_group(row: list) -> dict:
        """Parse un groupe de parts (1 row du tableau)."""
        col0_lines = row[0].split("\n") if row[0] else []
        nom = col0_lines[0]

        # Reconstituer les libellés multi-lignes du PDF
        # "Distribution unitaire sur plus et\nmoins-values réalisées nettes" → 1 libellé
        libelles = []
        i = 1  # skip le nom
        while i < len(col0_lines):
            l = col0_lines[i]
            if l.startswith("Distribution unitaire sur plus et") and i + 1 < len(col0_lines):
                libelles.append(l + " " + col0_lines[i + 1])
                i += 2
            else:
                libelles.append(l)
                i += 1

        # Valeurs par colonne date (cols 1-5), normalisées à 5 valeurs
        cols_vals = []
        for col_idx in range(1, 6):
            cell = row[col_idx] if col_idx < len(row) and row[col_idx] else ""
            vals = [v.strip() for v in cell.split("\n") if v.strip()] if cell else []
            # Si 4 valeurs → "Répartition d'avoirs*" absente → insérer None à l'index 2
            if len(vals) == 4:
                vals = [vals[0], vals[1], None, vals[2], vals[3]]
            # Pad à 5
            while len(vals) < 5:
                vals.append(None)
            cols_vals.append(vals)

        # Construire les lignes
        lignes = []
        for libelle in libelles:
            pos = POSITIONS_AVEC_VALEUR.get(libelle)
            if pos is not None:
                valeurs = []
                for c in cols_vals:
                    raw = c[pos]
                    # "-" → None ; nombre → string (gardé tel quel pour l'auto-fill)
                    valeurs.append(None if raw in (None, "-", "–") else raw)
            else:
                valeurs = [None] * len(cols_vals)
            lignes.append({"libelle": libelle, "valeurs": valeurs})

        return {"nom": nom, "lignes": lignes}

    # Extraction du tableau via pdfplumber (page 7 = index 6)
    raw_tables = _get_tables(pdf_bytes, page_index=6)
    tableau = {}

    if raw_tables:
        t = raw_tables[0]
        colonnes  = [c for c in t[0] if c]
        actif_net = [
            (None if v in ("-", "–", None) else v)
            for v in (t[1][1:] if len(t) > 1 else [])
        ]
        parties = [_parse_group(t[i]) for i in [2, 3, 4] if i < len(t)]
        tableau = {"colonnes": colonnes, "actif_net": actif_net, "parties": parties}

    # Notes de bas de tableau
    bloc          = _between(ft, TITRE, STOP)
    note_star     = ""
    note_starstar = ""
    note_absence  = ""

    m = re.search(r"\*\s+Pour les r[ée]partitions d.avoirs[^\n]*", bloc)
    if m:
        note_star = m.group(0).strip()

    m = re.search(r"\*\*\s*Premier exercice[^\n]*", bloc)
    if m:
        note_starstar = m.group(0).strip()

    m = re.search(
        r"En\s*l.absence\s*de\s*disposition\s*concernant.*?communiqu[eé]es\s*\.",
        bloc, re.IGNORECASE | re.DOTALL
    )
    if m:
        note_absence = re.sub(r"\s+", " ", m.group(0)).strip()

    return {
        "titre":   TITRE,
        "tableau": tableau,
        "note_star":                 note_star,
        "note_starstar":             note_starstar,
        "note_absence_distribution": note_absence,
    }


# ─── copie_reglement ──────────────────────────────────────────────────────────

def _parse_copie_reglement(pages: list[str]) -> dict:
    """
    Pages 8-9 du PDF — onglets sources : II. Copie règlement 1 et 2
    Extrait les textes de :
      - section_2_1 : "2.1 - Règles et méthodes comptables appliquées..."
      - section_2_2 : "2.2 - Description des méthodes de valorisation..."
          - texte_intro
          - sous_section "Instruments financiers non négociés..."
          - sous_section "Instruments financiers négociés..."
          - sous_section "Parts ou actions d'OPC..."
          - sous_section "Instruments financiers à terme (prêts)"
    """
    ft = _full(pages)

    TITRE_SEC  = "II. Règles et méthodes comptables"
    TITRE_2_1  = "2.1 - Règles et méthodes comptables appliquées au cours de l'exercice"
    TITRE_2_2  = "2.2 - Description des méthodes de valorisation des postes de bilan"
    ST_NON_COT = "Instruments financiers non négociés sur un marché réglementé ou assimilé"
    ST_COTES   = "Instruments financiers négociés sur un marché réglementé ou assimilé"
    ST_OPC     = "Parts ou actions d'OPC et droits d'entrée d'investissement"
    ST_TERME   = "Instruments financiers à terme (prêts)"
    STOP_SEC   = "III. Reconstitution de la ligne"

    return {
        "titre_section": TITRE_SEC,
        "section_2_1": {
            "titre": TITRE_2_1,
            "texte": _between(ft, TITRE_2_1, TITRE_2_2),
        },
        "section_2_2": {
            "titre":       TITRE_2_2,
            "texte_intro": _between(ft, TITRE_2_2, ST_NON_COT),
            "sous_sections": [
                {"titre": ST_NON_COT, "texte": _between(ft, ST_NON_COT, ST_COTES)},
                {"titre": ST_COTES,   "texte": _between(ft, ST_COTES,   ST_OPC)},
                {"titre": ST_OPC,     "texte": _between(ft, ST_OPC,     ST_TERME)},
                {"titre": ST_TERME,   "texte": _between(ft, ST_TERME,   STOP_SEC)},
            ],
        },
    }


# ─── evol_parts ───────────────────────────────────────────────────────────────

def _parse_evol_parts(pdf_bytes: bytes, pages: list[str]) -> dict:
    """
    Page 11 du PDF (index 10) — onglet source : IV. Evol parts
    Extrait :
      section_4_1 :
        tableau_souscrits → table 0 (colonnes: Type de parts | Nombre | Valeur)
        tableau_rachetes  → table 1 (même structure)
      section_4_2 : texte "Néant." ou autre

    Structure des tables :
      Row 0 : ['Type de parts', 'Nombre', 'Valeur']
      Row 1 : ['Parts A\nParts A'\nParts B', '-\n-\n-', '-\n-\n-']
      Row 2 : ['Total', '-', '-']
    """
    ft = _full(pages)

    TITRE_SEC = "IV. Evolution du nombre de parts au cours de l'exercice"
    TITRE_4_1 = "4.1 - Nombre et valeur des titres"
    ST_SOUSCR = "- Souscrits pendant l'exercice"
    ST_RACHET = "- Rachetés pendant l'exercice"
    TITRE_4_2 = "4.2 - Commission de souscription/rachat acquise ou rétrocédée"
    STOP_SEC  = "V. Flux concernant le nominal"

    raw_tables = _get_tables(pdf_bytes, page_index=10)

    def _build_table(t: list, sous_titre: str) -> dict:
        colonnes = [c for c in (t[0] if t else []) if c]
        lignes   = []

        PARTS = ["Parts A'", "Parts A", "Parts B", "Total"]

        for row in t[1:]:
            if not row or not row[0]:
                continue
            noms_lignes  = _split_cell(row[0])
            vals_nombre  = _split_cell(row[1]) if len(row) > 1 else []
            vals_valeur  = _split_cell(row[2]) if len(row) > 2 else []

            for i, nom in enumerate(noms_lignes):
                # Chercher "Parts A'" avant "Parts A"
                part = next((p for p in PARTS if _norm(nom.strip()) == _norm(p)), nom.strip())
                lignes.append({
                    "type_de_parts": part,
                    "nombre": _parse_num(vals_nombre[i]) if i < len(vals_nombre) else None,
                    "valeur": _parse_num(vals_valeur[i])  if i < len(vals_valeur)  else None,
                })

        return {"sous_titre": sous_titre, "colonnes": colonnes, "lignes": lignes}

    tab_souscr = _build_table(raw_tables[0] if len(raw_tables) > 0 else [], ST_SOUSCR)
    tab_rachet = _build_table(raw_tables[1] if len(raw_tables) > 1 else [], ST_RACHET)

    texte_4_2 = _between(ft, TITRE_4_2, STOP_SEC).split("\n")[0].strip()

    return {
        "titre_section": TITRE_SEC,
        "section_4_1": {
            "titre":             TITRE_4_1,
            "tableau_souscrits": tab_souscr,
            "tableau_rachetes":  tab_rachet,
        },
        "section_4_2": {
            "titre": TITRE_4_2,
            "texte": texte_4_2,
        },
    }


# ─── ventilation_an ───────────────────────────────────────────────────────────

def _parse_ventilation_an(pdf_bytes: bytes, pages: list[str]) -> dict:
    """
    Pages 13-14 du PDF — onglets sources : VI. Ventilation AN 1 et AN 2

    section_6_1 (page 13, index 12) :
      texte du titre "6.1 - Description de la méthode de calcul..."

    section_6_2 (page 14, index 13) — tableau extract_tables() :
      Colonnes (8) :
        Type de parts | Nombre de parts | Remboursement montant libéré |
        Affectation sur revenu prioritaire |
        20% aux parts A et 80% aux parts C |
        80% aux parts a et 20% aux parts C |
        Actif net | Valeur liquidative

      Lignes :
        Row 0 : headers (multi-lignes dans le PDF)
        Row 1 : "Parts A\nParts A'\nParts B" + valeurs multi-lignes
        Row 2 : "Total" + valeurs

      Note bas de tableau : "Il est rappelé aux souscripteurs..."
    """
    ft = _full(pages)

    TITRE_SEC = "VI. Ventilation de l'actif net par nature de parts"
    TITRE_6_1 = "6.1 - Description de la méthode de calcul des différentes parts"
    TITRE_6_2 = "6.2 - Ventilation de l'actif net par nature de parts"
    NOTE_KEY  = "Il est rappelé aux souscripteurs"
    STOP_SEC  = "VII. Présentation des expositions"

    texte_6_1 = _between(ft, TITRE_6_1, TITRE_6_2)

    # Tableau 6.2 — page 14 = index 13
    raw_tables = _get_tables(pdf_bytes, page_index=13)
    tableau_6_2 = {}

    if raw_tables:
        t = raw_tables[0]

        # Colonnes : headers multi-lignes → concaténer avec espace
        colonnes = [" ".join(_split_cell(c)) for c in (t[0] if t else []) if c]

        COL_KEYS = [
            "type_de_parts",
            "nombre_de_parts",
            "remboursement_montant_libere",
            "affectation_revenu_prioritaire",
            "pct_20_parts_A_80_parts_C",
            "pct_80_parts_A_20_parts_C",
            "actif_net",
            "valeur_liquidative",
        ]
        PARTS = ["Parts A'", "Parts A", "Parts B", "Total"]

        lignes = []
        for row in t[1:]:
            if not row or not row[0]:
                continue
            noms_lignes = _split_cell(row[0])
            # Valeurs par colonne
            cols_vals = [_split_cell(row[i]) if i < len(row) else [] for i in range(1, 8)]
            n = len(noms_lignes)

            for i, nom in enumerate(noms_lignes):
                part = next((p for p in PARTS if _norm(nom.strip()) == _norm(p)), nom.strip())
                entry = {"type_de_parts": part}
                for ki, key in enumerate(COL_KEYS[1:]):
                    cv = cols_vals[ki]
                    entry[key] = _parse_num(cv[i]) if i < len(cv) else None
                lignes.append(entry)

        tableau_6_2 = {"colonnes": colonnes, "lignes": lignes}

    # Note bas de tableau
    note_6_2 = ""
    i = ft.find(NOTE_KEY)
    if i != -1:
        j = ft.find(STOP_SEC, i)
        note_6_2 = re.sub(r"\s+", " ", ft[i: j if j != -1 else i + 500]).strip()

    return {
        "titre_section": TITRE_SEC,
        "section_6_1": {
            "titre": TITRE_6_1,
            "texte": texte_6_1,
        },
        "section_6_2": {
            "titre":            TITRE_6_2,
            "tableau":          tableau_6_2,
            "note_bas_tableau": note_6_2,
        },
    }



# ─── flux_nominal  (V. Flux concernant le nominal) ───────────────────────────

def _parse_flux_nominal(pdf_bytes: bytes, pages: list[str]) -> dict:
    """
    Page 12 du PDF — section V.

    Tableau à double header dynamique :
      Row 0 : groupes de colonnes  → ex. ["Exercice N"]
                                     ou  ["Exercice N", "Exercice N-1"]  (si N-1 présent)
      Row 1 : sous-colonnes        → noms des parts détectés dynamiquement
                                     (Parts A, Parts A', Parts B, ou tout autre nom)
      Rows 2+ : lignes de données  → col 0 = libellé (peut contenir des sous-lignes
                                     séparées par \n, ex: "Appel de fonds\nADF n°11 06/06/2025")

    Retourne :
    {
        "titre_section": str,
        "tableau": {
            "groupes":  [str, ...],            // ex: ["Exercice N"]
            "colonnes": {                      // parties par groupe, dans l'ordre
                "Exercice N": [
                    {"index": 1, "nom": "Parts A"},
                    {"index": 2, "nom": "Parts A'"},
                    ...
                ]
            },
            "lignes": [
                {
                    "libelle": str,            // ex: "Nominal appelé et non remboursé..."
                    "valeurs": {
                        "Exercice N": {
                            "Parts A":  str|None,
                            "Parts A'": str|None,
                            ...
                        }
                    },
                    "sous_lignes": [           // présent seulement si la ligne a des sous-lignes
                        {
                            "libelle": str,    // ex: "ADF n°11 06/06/2025"
                            "valeurs": { ... } // même structure
                        }
                    ]
                },
                ...
            ]
        }
    }
    """
    TITRE_SEC = "V. Flux concernant le nominal appelé et remboursé sur l\'exercice"

    raw_tables = _get_tables(pdf_bytes, page_index=11)   # page 12 = index 11
    if not raw_tables:
        return {"titre_section": TITRE_SEC, "tableau": {}}

    t = raw_tables[0]
    if len(t) < 3:
        return {"titre_section": TITRE_SEC, "tableau": {}}

    # ── Headers ──────────────────────────────────────────────────────────────
    header1 = t[0]   # groupes : [None, "Exercice N", None, None, ...]
    header2 = t[1]   # parts   : [None, "Parts A", "Parts A'", "Parts B", ...]
    n_cols  = len(header1)

    # Mapper chaque index de colonne → groupe (en propageant le dernier groupe non-None)
    col_groupe = {}
    last_groupe = None
    for i, cell in enumerate(header1):
        if cell and cell.strip():
            last_groupe = cell.strip()
        col_groupe[i] = last_groupe

    # Mapper chaque index de colonne → nom de la sous-colonne
    col_nom = {}
    for i, cell in enumerate(header2):
        if cell and cell.strip():
            col_nom[i] = cell.strip()

    # Groupes uniques dans l\'ordre d\'apparition (hors col 0)
    groupes = []
    for i in range(1, n_cols):
        g = col_groupe.get(i)
        if g and g not in groupes:
            groupes.append(g)

    # Sous-colonnes par groupe
    cols_par_groupe = {g: [] for g in groupes}
    for i in range(1, n_cols):
        g   = col_groupe.get(i)
        nom = col_nom.get(i)
        if g and nom:
            cols_par_groupe[g].append({"index": i, "nom": nom})

    # ── Lignes de données ─────────────────────────────────────────────────────
    def _v(cell: str | None) -> str | None:
        if cell is None:
            return None
        s = cell.strip().replace("\u202f", "").replace("\u00a0", "")
        return None if s in ("-", "\u2013", "") else s

    lignes = []
    for row in t[2:]:
        if not row or not row[0]:
            continue

        col0_lines  = row[0].split("\n")
        libelle     = col0_lines[0].strip()
        sous_labels = [l.strip() for l in col0_lines[1:] if l.strip()]

        # Valeurs principales (première sous-ligne de chaque cellule)
        valeurs = {}
        for g, parts in cols_par_groupe.items():
            valeurs[g] = {}
            for p in parts:
                cell = row[p["index"]] if p["index"] < len(row) else None
                cell_lines = cell.split("\n") if cell else []
                valeurs[g][p["nom"]] = _v(cell_lines[0]) if cell_lines else None

        # Sous-lignes (ex: "ADF n°11 06/06/2025" avec ses propres valeurs)
        sous_lignes = []
        for j, sl_label in enumerate(sous_labels):
            sv = {}
            for g, parts in cols_par_groupe.items():
                sv[g] = {}
                for p in parts:
                    cell = row[p["index"]] if p["index"] < len(row) else None
                    cell_lines = cell.split("\n") if cell else []
                    sv[g][p["nom"]] = _v(cell_lines[j + 1]) if j + 1 < len(cell_lines) else None
            sous_lignes.append({"libelle": sl_label, "valeurs": sv})

        ligne = {"libelle": libelle, "valeurs": valeurs}
        if sous_lignes:
            ligne["sous_lignes"] = sous_lignes
        lignes.append(ligne)

    return {
        "titre_section": TITRE_SEC,
        "tableau": {
            "groupes":  groupes,
            "colonnes": cols_par_groupe,
            "lignes":   lignes,
        },
    }

# ─── Contrôleur principal ─────────────────────────────────────────────────────

async def PdfToDictController(pdf_bytes: bytes) -> dict:
    """
    Extrait les sections textuelles et tabulaires du PDF des comptes annuels.
    Source unique : le fichier PDF.

    Paramètre
    ---------
    pdf_bytes : bytes — contenu brut du fichier PDF uploadé.

    Retourne le dictionnaire structuré décrit dans la docstring du module.
    """
    pages = _get_pages(pdf_bytes)

    return {
        "prospectus":       _parse_prospectus(pages),
        "caracteristiques": _parse_caracteristiques(pdf_bytes, pages),
        "copie_reglement":  _parse_copie_reglement(pages),
        "evol_parts":       _parse_evol_parts(pdf_bytes, pages),
        "ventilation_an":   _parse_ventilation_an(pdf_bytes, pages),
        "flux_nominal":     _parse_flux_nominal(pdf_bytes, pages),
    }
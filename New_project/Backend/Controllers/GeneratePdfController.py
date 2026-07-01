"""
GeneratePdfController.py
========================
Génère le PDF complet (Bilan Actif + Bilan Passif + CR1 + CR2)
via WeasyPrint + Jinja2.

Architecture
------------
  Templates/
    bilan_actif.html
    bilan_passif.html
    compte_resultat_1.html
    compte_resultat_2.html

  GeneratePdfController.py  ← ce fichier

Dépendances
-----------
    pip install weasyprint jinja2 pypdf
"""

from __future__ import annotations

import io
import re
import base64
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


# ── Chemins ───────────────────────────────────────────────────────────────────
TEMPLATES_DIR = Path(__file__).parent.parent / "Templates"
LOGO_PATH     = Path(__file__).parent.parent / "Static" / "aplitec.png"


# ── Logo → data URL ───────────────────────────────────────────────────────────
def _logo_to_data_url(logo_path: Path) -> str:
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "svg": "image/svg+xml"}.get(logo_path.suffix.lstrip(".").lower(), "image/png")
    b64 = base64.b64encode(logo_path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


# ── Formatage des nombres ─────────────────────────────────────────────────────
def _fmt(v: Optional[float]) -> str:
    """
    None / 0  → "-"
    positif   → "236 717 947"
    négatif   → "- 15 996 742"
    Séparateur : espace fine insécable (U+202F).
    """
    if v is None or v == 0.0:
        return "-"
    s = f"{abs(v):,.0f}".replace(",", "\u202f")
    return f"- {s}" if v < 0 else s


# ── Dict avec accès par attribut ─────────────────────────────────────────────
class _D(dict):
    def __getattr__(self, key):
        try:
            val = self[key]
            return _D(val) if isinstance(val, dict) else val
        except KeyError:
            return None
    def __missing__(self, key):
        return None

def _wrap(data: dict) -> _D:
    if not isinstance(data, dict):
        return data
    return _D({k: _wrap(v) for k, v in data.items()})


# ── Rendu Jinja2 ─────────────────────────────────────────────────────────────
def _render(template_name: str, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    env.globals["fmt"]     = _fmt
    env.globals["fmt_abs"] = lambda v: _fmt(abs(v) if v else 0)
    return env.get_template(template_name).render(**context)


# ── Injection numéro de page dans le CSS @page ────────────────────────────────
def _inject_page_numbers(html: str, page_number: int, total_pages: int) -> str:
    """
    Remplace counter(page) et counter(pages) dans @bottom-right
    par des valeurs fixes — nécessaire car chaque template est converti
    séparément et WeasyPrint ne connaît pas le total du document fusionné.
    """
    def replace_counters(m):
        content = m.group(0)
        content = re.sub(r'counter\(pages\)', f'"{total_pages}"', content)
        content = re.sub(r'counter\(page\)',  f'"{page_number}"', content)
        return content
    return re.sub(r'@bottom-right\s*\{[^}]*\}', replace_counters, html, flags=re.DOTALL)


# ── HTML → PDF ────────────────────────────────────────────────────────────────
def _to_pdf(html: str) -> bytes:
    return HTML(string=html).write_pdf()


# ── Fusion de PDFs ────────────────────────────────────────────────────────────
def _merge(pdf_list: list[bytes]) -> bytes:
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    for pdf_bytes in pdf_list:
        for page in PdfReader(io.BytesIO(pdf_bytes)).pages:
            writer.add_page(page)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf.read()


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTROLLER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

async def GeneratePdfController(
    bilan:                    dict,
    compte_resultat:          dict,
    nom_fond:                 str,
    date_cloture:             str,
    capitaux_propres:         Optional[dict] = None,
    exposition_portefeuille:  Optional[dict] = None,
    sommes_distribuables:     Optional[dict] = None,
) -> bytes:
    """
    Génère le PDF complet :
      Page 1 — Bilan Actif
      Page 2 — Bilan Passif
      Page 3 — Compte de Résultat 1
      Page 4 — Compte de Résultat 2
      Page 5 — Capitaux Propres (si fourni)

    Paramètres
    ----------
    bilan            : résultat de BilanController
    compte_resultat  : résultat de CompteResultatController
    nom_fond         : ex "SINGULAR VENTURES I FPCI"
    date_cloture     : ex "31/12/2025"

    Retourne
    --------
    bytes : PDF prêt à streamer en Response FastAPI
    """

    # ── Données bilan ─────────────────────────────────────────────────────
    actif_n      = _wrap(bilan["bilan_actif"]["exercice_n"])
    actif_n1_raw = bilan["bilan_actif"].get("exercice_n1")
    actif_n1     = _wrap(actif_n1_raw) if actif_n1_raw else None
    has_n1       = actif_n1 is not None

    passif_n  = _wrap(bilan["bilan_passif"]["exercice_n"])
    passif_n1 = _wrap(bilan["bilan_passif"]["exercice_n1"]) if has_n1 else None

    # ── Données compte de résultat ────────────────────────────────────────
    cr1_n  = _wrap(compte_resultat["compte_resultat_1"]["exercice_n"])
    cr1_n1 = _wrap(compte_resultat["compte_resultat_1"]["exercice_n1"]) if has_n1 else _wrap({})

    cr2_n  = _wrap(compte_resultat["compte_resultat_2"]["exercice_n"])
    cr2_n1 = _wrap(compte_resultat["compte_resultat_2"]["exercice_n1"]) if has_n1 else _wrap({})

    # ── Données capitaux propres (optionnel) ──────────────────────────────
    cp_data   = _wrap(capitaux_propres["capitaux_propres"]) if capitaux_propres else None

    # ── Données exposition portefeuille (optionnel) ───────────────────────
    expo_data = None
    if exposition_portefeuille:
        ep = exposition_portefeuille["exposition_portefeuille"]
        expo_data = _wrap(ep.get("exercice_n", ep))

    # ── Données sommes distribuables (optionnel) ──────────────────────────
    sd_data = _wrap(sommes_distribuables["sommes_distribuables"]) if sommes_distribuables else None

    # ── Contexte commun ───────────────────────────────────────────────────
    logo_url = _logo_to_data_url(LOGO_PATH) if LOGO_PATH.exists() else ""
    base_ctx = {
        "nom_fond":     nom_fond,
        "date_cloture": date_cloture,
        "has_n1":       has_n1,
        "logo_url":     logo_url,
    }

    # ── Rendu des templates ───────────────────────────────────────────────
    pages_html = [
        _render("bilan_actif.html",        {**base_ctx, "actif_n": actif_n,   "actif_n1": actif_n1 or _wrap({})}),
        _render("bilan_passif.html",       {**base_ctx, "passif_n": passif_n, "passif_n1": passif_n1 or _wrap({})}),
        _render("compte_resultat_1.html",  {**base_ctx, "cr1_n": cr1_n,       "cr1_n1": cr1_n1}),
        _render("compte_resultat_2.html",  {**base_ctx, "cr2_n": cr2_n,       "cr2_n1": cr2_n1}),
    ]
    # Page 5 : Capitaux propres (optionnel)
    if cp_data is not None:
        pages_html.append(
            _render("capitaux_propres.html", {**base_ctx, "cp": cp_data})
        )
    # Page 6 : Exposition portefeuille (optionnel)
    if expo_data is not None:
        pages_html.append(
            _render("exposition_portefeuille.html", {**base_ctx, "expo": expo_data})
        )
    # Page 7 : Sommes distribuables (optionnel)
    if sd_data is not None:
        pages_html.append(
            _render("sommes_distribuables.html", {**base_ctx, "sd": sd_data})
        )

    total_pages = len(pages_html)

    # ── Conversion + injection numéros de page ────────────────────────────
    pdf_list = [
        _to_pdf(_inject_page_numbers(html, i + 1, total_pages))
        for i, html in enumerate(pages_html)
    ]

    return _merge(pdf_list)


# ── Alias rétrocompatibilité ──────────────────────────────────────────────────
async def generer_bilan_pdf(
    bilan:                   dict,
    nom_fond:                str,
    date_cloture:            str,
    compte_resultat:         Optional[dict] = None,
    capitaux_propres:        Optional[dict] = None,
    exposition_portefeuille: Optional[dict] = None,
    sommes_distribuables:    Optional[dict] = None,
    # Anciens paramètres ignorés (WeasyPrint gère la pagination)
    total_pages: int = 2,
    page_actif:  int = 1,
    page_passif: int = 2,
) -> bytes:
    """
    Alias vers GeneratePdfController.
    Si compte_resultat n'est pas fourni, génère uniquement les 2 pages bilan.
    """
    if compte_resultat:
        return await GeneratePdfController(
            bilan=bilan,
            compte_resultat=compte_resultat,
            nom_fond=nom_fond,
            date_cloture=date_cloture,
            capitaux_propres=capitaux_propres,
            exposition_portefeuille=exposition_portefeuille,
            sommes_distribuables=sommes_distribuables,
        )

    # Mode 2 pages : bilan uniquement (rétrocompatibilité)
    from jinja2 import Environment, FileSystemLoader

    actif_n      = _wrap(bilan["bilan_actif"]["exercice_n"])
    actif_n1_raw = bilan["bilan_actif"].get("exercice_n1")
    actif_n1     = _wrap(actif_n1_raw) if actif_n1_raw else None
    has_n1       = actif_n1 is not None
    passif_n     = _wrap(bilan["bilan_passif"]["exercice_n"])
    passif_n1    = _wrap(bilan["bilan_passif"]["exercice_n1"]) if has_n1 else None

    logo_url = _logo_to_data_url(LOGO_PATH) if LOGO_PATH.exists() else ""
    base_ctx = {"nom_fond": nom_fond, "date_cloture": date_cloture,
                "has_n1": has_n1, "logo_url": logo_url}

    pages_html = [
        _render("bilan_actif.html",  {**base_ctx, "actif_n": actif_n,   "actif_n1": actif_n1 or _wrap({})}),
        _render("bilan_passif.html", {**base_ctx, "passif_n": passif_n, "passif_n1": passif_n1 or _wrap({})}),
    ]
    return _merge([
        _to_pdf(_inject_page_numbers(html, i + 1, len(pages_html)))
        for i, html in enumerate(pages_html)
    ])
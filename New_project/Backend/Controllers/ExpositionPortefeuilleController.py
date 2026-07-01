"""
ExpositionPortefeuilleController.py
=====================================
Génère la ventilation de l'exposition sur les portefeuilles de
capital-investissement (onglet "VIII. Exposition portefeuille").

Entrées
-------
data : dict  — même format que BilanController / CompteResultatController
    {
        "N":   {"balance_n": [...], "inventaire_n": [...], "pvmv": [...]},
        "N_1": {"balance_n_1": [...], "inventaire_n_1": [...]}  # ou None
    }

Sortie
------
{
    "exposition_portefeuille": {
        "actions": {
            "cotees":     {"capital_investissement": float, "autres_actifs": float, "total": float},
            "non_cotees": {...}
        },
        "obligations_convertibles": { "cotees": {...}, "non_cotees": {...} },
        "autres_obligations":       { "cotees": {...}, "non_cotees": {...} },
        "titres_creances":          {"capital_investissement": float, "autres_actifs": float, "total": float},
        "parts_opc":                {"capital_investissement": float, "autres_actifs": float, "total": float},
        "prets":                    {"capital_investissement": float, "autres_actifs": float, "total": float},
        "autres_actifs_eligibles":  {"capital_investissement": float, "autres_actifs": float, "total": float},
        "total":                    {"capital_investissement": float, "autres_actifs": float, "total": float},
    }
}

Formules (onglet "VIII. Exposition portefeuille")
--------------------------------------------------
Source : inventaire uniquement (colonne "Valeur estimation coupon inclus")

E9   Actions cotées (Cap. Inv.)     = SUMIFS(inv, G_ou_I="I", Libellé LIKE "*Action*")
E10  Actions non cotées (Cap. Inv.) = SUMIF(Code_titre, "??AC*|??AD*|??SA*|??BS*")
F9   Actions cotées (Autres)        = 0 (hardcodé)
F10  Actions non cotées (Autres)    = 0 (hardcodé)

E12  Oblig. conv. cotées            = 0 (hardcodé)
E13  Oblig. conv. non cotées        = SUMIF(Code_titre, "??OC*")
F12/F13 = 0 (hardcodé)

E15  Autres oblig. cotées           = 0 (hardcodé)
E16  Autres oblig. non cotées       = SUMIF(Code_titre, "??OS*|??OR*|??CN*")
F15/F16 = 0 (hardcodé)

E17  Titres de créances (Cap. Inv.) = SUMIF(Code_titre, "??TC*")
F17  Titres de créances (Autres)    = 0 (hardcodé)

E18  Parts OPC (Cap. Inv.)          = SUMIF(Libellé, "*FPCI*|*SLP*|*FCPR*|*FCPI*")
F18  Parts OPC (Autres OPCVM)       = SUMIF(Libellé, "*FCP*|*SICAV*")

E19  Prêts (Cap. Inv.)              = SUMIF(Code_titre, "??CC*|??PR*|??NO*")
F19  Prêts (Autres)                 = 0 (hardcodé)

E20  Autres actifs éligibles (CI)   = SUMIF(Code_titre, "*CT*|*OP*")
F20  Autres actifs éligibles (Aut.) = 0 (hardcodé)

G*   Total = E* + F* pour chaque ligne
E21/F21/G21 = SUM de chaque colonne
"""

from __future__ import annotations
from fnmatch import fnmatch
from typing import Optional


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _to_float(v) -> float:
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _val(row: dict) -> float:
    return _to_float(row.get("Valeur estimation coupon inclus", 0))


def _sumif_code(inventaire: list[dict], *patterns: str) -> float:
    """SUMIF sur Code_titre avec wildcards."""
    total = 0.0
    for row in inventaire:
        code = str(row.get("Code_titre", "")).strip().upper()
        if not code:
            continue
        if any(fnmatch(code, p.upper()) for p in patterns):
            total += _val(row)
    return total


def _sumif_libelle(inventaire: list[dict], *substrings: str) -> float:
    """SUMIF sur Libellé (contient sous-chaîne)."""
    total = 0.0
    for row in inventaire:
        lib = str(row.get("Libellé", "")).upper()
        if any(s.upper() in lib for s in substrings):
            total += _val(row)
    return total


def _sumifs_cotees(inventaire: list[dict]) -> float:
    """SUMIFS : G_ou_I = 'I' ET Libellé contient 'Action'."""
    total = 0.0
    for row in inventaire:
        gi  = str(row.get("G ou I", "")).strip()
        lib = str(row.get("Libellé", "")).upper()
        if gi == "I" and "ACTION" in lib:
            total += _val(row)
    return total


def _poste(ci: float, autres: float) -> dict:
    return {
        "capital_investissement": round(ci,     2),
        "autres_actifs":          round(autres, 2),
        "total":                  round(ci + autres, 2),
    }


# ─── Calcul pour un exercice ─────────────────────────────────────────────────

def _calculer(inventaire: list[dict]) -> dict:
    """Calcule la ventilation de l'exposition pour un inventaire donné."""

    # ── Actions ───────────────────────────────────────────────────────────
    actions_cotees_ci     = _sumifs_cotees(inventaire)
    actions_non_cotees_ci = _sumif_code(inventaire, "??AC*", "??AD*", "??SA*", "??BS*")

    # ── Obligations convertibles ──────────────────────────────────────────
    oblig_conv_non_cotees_ci = _sumif_code(inventaire, "??OC*")

    # ── Autres obligations ────────────────────────────────────────────────
    autres_oblig_non_cotees_ci = _sumif_code(inventaire, "??OS*", "??OR*", "??CN*")

    # ── Titres de créances ────────────────────────────────────────────────
    titres_creances_ci = _sumif_code(inventaire, "??TC*", "??FCT*")

    # ── Parts d'OPC ───────────────────────────────────────────────────────
    opc_ci     = _sumif_libelle(inventaire, "FPCI", "SLP", "FCPR", "FCPI")
    opc_autres = _sumif_libelle(inventaire, "FCP", "SICAV")

    # ── Prêts ─────────────────────────────────────────────────────────────
    prets_ci = _sumif_code(inventaire, "??CC*", "??PR*", "??NO*")

    # ── Autres actifs éligibles ───────────────────────────────────────────
    autres_ci = _sumif_code(inventaire, "*CT*", "*OP*")

    # ── Totaux colonnes ───────────────────────────────────────────────────
    total_ci = (
        actions_cotees_ci + actions_non_cotees_ci
        + oblig_conv_non_cotees_ci
        + autres_oblig_non_cotees_ci
        + titres_creances_ci
        + opc_ci
        + prets_ci
        + autres_ci
    )
    total_autres = opc_autres  # seule valeur non nulle possible côté "autres"
    total_total  = total_ci + total_autres

    return {
        "actions": {
            "cotees":     _poste(actions_cotees_ci, 0.0),
            "non_cotees": _poste(actions_non_cotees_ci, 0.0),
        },
        "obligations_convertibles": {
            "cotees":     _poste(0.0, 0.0),
            "non_cotees": _poste(oblig_conv_non_cotees_ci, 0.0),
        },
        "autres_obligations": {
            "cotees":     _poste(0.0, 0.0),
            "non_cotees": _poste(autres_oblig_non_cotees_ci, 0.0),
        },
        "titres_creances": _poste(titres_creances_ci, 0.0),
        "parts_opc":       _poste(opc_ci, opc_autres),
        "prets":           _poste(prets_ci, 0.0),
        "autres_actifs_eligibles": _poste(autres_ci, 0.0),
        "total": {
            "capital_investissement": round(total_ci,     2),
            "autres_actifs":          round(total_autres, 2),
            "total":                  round(total_total,  2),
        },
    }


# ─── Contrôleur principal ─────────────────────────────────────────────────────

async def ExpositionPortefeuilleController(data: dict) -> dict:
    """
    Génère la ventilation de l'exposition portefeuille (onglet VIII).

    Paramètre
    ---------
    data : dict
        {
            "N":   {"balance_n": [...], "inventaire_n": [...], "pvmv": [...]},
            "N_1": {"balance_n_1": [...], "inventaire_n_1": [...]}  # ou None
        }

    Retourne
    --------
    {
        "exposition_portefeuille": {
            "exercice_n":  { <ventilation complète> },
            "exercice_n1": { <ventilation complète> }  # absent si N_1 est None
        }
    }

    Structure de chaque poste :
        { "capital_investissement": float, "autres_actifs": float, "total": float }
    Les postes "actions" et "obligations_*" ont des sous-clés "cotees"/"non_cotees".
    """

    data_n  = data.get("N") or {}
    data_n1 = data.get("N_1")

    inventaire_n = data_n.get("inventaire_n", [])
    result = {"exercice_n": _calculer(inventaire_n)}

    if data_n1:
        inventaire_n1 = data_n1.get("inventaire_n_1", [])
        result["exercice_n1"] = _calculer(inventaire_n1)

    return {"exposition_portefeuille": result}
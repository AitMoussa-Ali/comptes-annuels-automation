"""
SommesDistribuablesController.py
=================================
Génère la détermination et ventilation des sommes distribuables
(onglet "XIII. Sommes distribuables").

Entrées
-------
data : dict  — même format que BilanController
    {
        "N":   {"balance_n": [...], "inventaire_n": [...], "pvmv": [...]},
        "N_1": {"balance_n_1": [...], ...}  # ou None
    }

Sortie
------
{
    "sommes_distribuables": {

        "meta": {
            "label_exercice_n":  str,   # "Exercice N" ou "Exercice N*"
            "label_exercice_n1": str,   # "Exercice N-1" ou "Exercice N-1*"
            "premier_exercice":  bool,
            "note_generale":     str,   # texte de l'alinéa A3 (toujours présent)
        },

        # ── SECTION REVENUS NETS ──────────────────────────────────────────
        "revenus_nets": {
            "revenus_nets":                 {"n": float, "n1": float},
            "acomptes_sur_revenus_nets":    {"n": float, "n1": float},
            "revenus_exercice_a_affecter":  {"n": float, "n1": float},
            "report_a_nouveau":             {"n": float, "n1": float},
            "sommes_distribuables_revenus": {"n": float, "n1": float},
            "affectation": {
                "distribution":             {"n": float, "n1": float},
                "report_a_nouveau_exo":     {"n": float, "n1": float},
                "capitalisation":           {"n": float, "n1": float},
                "total":                    {"n": float, "n1": float},
            },
            "acomptes_info": {
                "montant_unitaire":         {"n": float, "n1": float},
                "credits_impots_totaux":    {"n": float, "n1": float},
                "credits_impots_unitaires": {"n": float, "n1": float},
            },
            "parts_info": {
                "nombre_parts":             {"n": float, "n1": float},
                "distribution_unitaire":    {"n": float, "n1": float},
                "credit_impot_distribution":{"n": float, "n1": float},
            },
        },

        # ── SECTION PVMV RÉALISÉES ────────────────────────────────────────
        "pvmv_realisees": {
            "pvmv_realisees_nettes":            {"n": float, "n1": float},
            "acomptes_sur_pvmv_realisees":      {"n": float, "n1": float},
            "pvmv_realisees_a_affecter":        {"n": float, "n1": float},
            "pvmv_anterieures_non_distribuees": {"n": float, "n1": float},
            "sommes_distribuables_pvmv":        {"n": float, "n1": float},
            "affectation": {
                "distribution":                 {"n": float, "n1": float},
                "report_a_nouveau_pvmv":        {"n": float, "n1": float},
                "capitalisation":               {"n": float, "n1": float},
                "total":                        {"n": float, "n1": float},
            },
            "acomptes_info": {
                "acomptes_unitaires":           {"n": float, "n1": float},
            },
            "parts_info": {
                "nombre_parts":                 {"n": float, "n1": float},
                "distribution_unitaire":        {"n": float, "n1": float},
            },
        },
    }
}

Formules (onglet "XIII. Sommes distribuables")
----------------------------------------------
Toutes les valeurs "n" viennent de balance_n, "n1" de balance_n_1.
net(prefix) = SUMIF(prefix*, Crédit) - SUMIF(prefix*, Débit)

── SECTION REVENUS NETS ──────────────────────────────────────────────────
G8  Revenus nets          = net("70")+net("71")+net("72")+net("60")+net("61")+net("62")
                            [même formule que CapitauxPropres F10]
G9  Acomptes revenus nets = SUMIF("791*", Débit)
G10 Revenus à affecter    = G8 - G9
G11 Report à nouveau      = net("111*")
G12 Sommes distribuables  = G10 + G11
G14 Distribution          = 0  (hardcodé — capitalisé dans ce fonds)
G15 Report à nouveau exo  = 0  (hardcodé)
G16 Capitalisation        = G12
G17 Total                 = G14+G15+G16
G18 Info acomptes total   = 0 (hardcodé dans ce fonds)
G19 Montant unitaire      = 0
G20 Crédits impôts totaux = 0
G21 Crédits impôts unit.  = 0
G22 Info parts total      = 0
G23 Nombre de parts       = 0
G24 Distribution unitaire = 0
G25 Crédit impôt distrib. = 0

── SECTION PVMV RÉALISÉES ────────────────────────────────────────────────
G30 PVMV réal. nettes     = net("74") + net("64")
                            = SUMIF("74*",F) - SUMIF("64*",E) + SUMIF("64*",F)
G31 Acomptes PVMV         = SUMIF("794*", Débit)
G32 PVMV à affecter       = G30 - G31
G33 PVMV antér. non distr = net("111*")  [même que G11]
G34 Sommes distrib. PVMV  = G32 + G33
G36 Distribution          = 0 (hardcodé)
G37 Report à nouveau PVMV = net("111*")
G38 Capitalisation        = G34
G39 Total                 = G36+G37+G38
G40 Info acomptes total   = 0
G41 Acomptes unitaires    = 0
G42 Info parts total      = 0
G43 Nombre de parts       = 0
G44 Distribution unitaire = 0

Labels dynamiques :
  "Exercice N*"   si total capitaux propres N-1 = 0 (premier exercice)
  "Exercice N-1*" si pas de balance N-1 fournie
"""

from __future__ import annotations
from typing import Optional


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _to_float(v) -> float:
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _sumif(balance: list[dict], prefix: str, col: str) -> float:
    return sum(
        _to_float(row.get(col, 0))
        for row in balance
        if str(row.get("Compte", "")).startswith(prefix)
    )


def _net(balance: list[dict], prefix: str) -> float:
    return (
        _sumif(balance, prefix, "Solde Crédit")
        - _sumif(balance, prefix, "Solde Débit")
    )


def _v(n: float, n1: float) -> dict:
    return {"n": round(n, 2), "n1": round(n1, 2)}


# ─── Calcul d'une section pour les deux exercices ────────────────────────────

def _revenus_nets(bal_n: list[dict], bal_n1: list[dict]) -> dict:
    """Section 'Affectation des sommes distribuables afférentes aux revenus nets'."""

    def _calc(bal: list[dict]) -> dict:
        # G8 : Revenus nets = net(70+71+72) + net(60+61+62)
        revenus = (
            _net(bal, "70") + _net(bal, "71") + _net(bal, "72")
            + _net(bal, "60") + _net(bal, "61") + _net(bal, "62")
        )
        # G9 : Acomptes revenus nets = SUMIF("791*", Débit)
        acomptes = _sumif(bal, "791", "Solde Débit")
        # G10 = G8 - G9
        a_affecter = revenus - acomptes
        # G11 : Report à nouveau = net("111*")
        report = _net(bal, "111")
        # G12 = G10 + G11
        sommes_distrib = a_affecter + report
        # G14/G15 = 0 (hardcodé — pas de distribution dans ce type de fonds)
        distribution  = 0.0
        report_exo    = 0.0
        # G16 = G12
        capitalisation = sommes_distrib
        # G17 = G14+G15+G16
        total = distribution + report_exo + capitalisation

        return {
            "revenus_nets":              revenus,
            "acomptes_sur_revenus_nets": acomptes,
            "revenus_exercice_a_affecter": a_affecter,
            "report_a_nouveau":          report,
            "sommes_distribuables":      sommes_distrib,
            "distribution":              distribution,
            "report_exo":                report_exo,
            "capitalisation":            capitalisation,
            "total":                     total,
        }

    vn  = _calc(bal_n)
    vn1 = _calc(bal_n1)

    return {
        "revenus_nets":                 _v(vn["revenus_nets"],              vn1["revenus_nets"]),
        "acomptes_sur_revenus_nets":    _v(vn["acomptes_sur_revenus_nets"], vn1["acomptes_sur_revenus_nets"]),
        "revenus_exercice_a_affecter":  _v(vn["revenus_exercice_a_affecter"], vn1["revenus_exercice_a_affecter"]),
        "report_a_nouveau":             _v(vn["report_a_nouveau"],          vn1["report_a_nouveau"]),
        "sommes_distribuables_revenus": _v(vn["sommes_distribuables"],      vn1["sommes_distribuables"]),
        "affectation": {
            "distribution":          _v(vn["distribution"],   vn1["distribution"]),
            "report_a_nouveau_exo":  _v(vn["report_exo"],     vn1["report_exo"]),
            "capitalisation":        _v(vn["capitalisation"],  vn1["capitalisation"]),
            "total":                 _v(vn["total"],           vn1["total"]),
        },
        "acomptes_info": {
            "montant_unitaire":          _v(0.0, 0.0),
            "credits_impots_totaux":     _v(0.0, 0.0),
            "credits_impots_unitaires":  _v(0.0, 0.0),
        },
        "parts_info": {
            "nombre_parts":              _v(0.0, 0.0),
            "distribution_unitaire":     _v(0.0, 0.0),
            "credit_impot_distribution": _v(0.0, 0.0),
        },
    }


def _pvmv_realisees(bal_n: list[dict], bal_n1: list[dict]) -> dict:
    """Section 'Affectation des sommes distribuables afférentes aux PVMV réalisées'."""

    def _calc(bal: list[dict]) -> dict:
        # G30 : PVMV réal. nettes = net("74") + net("64")
        pvmv = _net(bal, "74") + _net(bal, "64")
        # G31 : Acomptes PVMV = SUMIF("794*", Débit)
        acomptes = _sumif(bal, "794", "Solde Débit")
        # G32 = G30 - G31
        a_affecter = pvmv - acomptes
        # G33 = net("111*")  [PVMV antérieures non distribuées]
        anterieures = _net(bal, "111")
        # G34 = G32 + G33
        sommes_distrib = a_affecter + anterieures
        # G36 = 0
        distribution = 0.0
        # G37 = net("111*")
        report_pvmv = anterieures
        # G38 = G34
        capitalisation = sommes_distrib
        # G39 = G36+G37+G38
        total = distribution + report_pvmv + capitalisation

        return {
            "pvmv_realisees":    pvmv,
            "acomptes":          acomptes,
            "a_affecter":        a_affecter,
            "anterieures":       anterieures,
            "sommes_distrib":    sommes_distrib,
            "distribution":      distribution,
            "report_pvmv":       report_pvmv,
            "capitalisation":    capitalisation,
            "total":             total,
        }

    vn  = _calc(bal_n)
    vn1 = _calc(bal_n1)

    return {
        "pvmv_realisees_nettes":             _v(vn["pvmv_realisees"], vn1["pvmv_realisees"]),
        "acomptes_sur_pvmv_realisees":       _v(vn["acomptes"],       vn1["acomptes"]),
        "pvmv_realisees_a_affecter":         _v(vn["a_affecter"],     vn1["a_affecter"]),
        "pvmv_anterieures_non_distribuees":  _v(vn["anterieures"],    vn1["anterieures"]),
        "sommes_distribuables_pvmv":         _v(vn["sommes_distrib"], vn1["sommes_distrib"]),
        "affectation": {
            "distribution":         _v(vn["distribution"],   vn1["distribution"]),
            "report_a_nouveau_pvmv":_v(vn["report_pvmv"],    vn1["report_pvmv"]),
            "capitalisation":       _v(vn["capitalisation"],  vn1["capitalisation"]),
            "total":                _v(vn["total"],           vn1["total"]),
        },
        "acomptes_info": {
            "acomptes_unitaires": _v(0.0, 0.0),
        },
        "parts_info": {
            "nombre_parts":          _v(0.0, 0.0),
            "distribution_unitaire": _v(0.0, 0.0),
        },
    }


# ─── Contrôleur principal ─────────────────────────────────────────────────────

NOTE_GENERALE = (
    "En l'absence de dispositions concernant la répartition des revenus nets "
    "et plus ou moins-values réalisées au cours de la vie du fonds, la ventilation "
    "des sommes distribuables par catégorie de parts et la capitalisation unitaire "
    "ne sont pas communiquées."
)


async def SommesDistribuablesController(data: dict) -> dict:
    """
    Génère la détermination et ventilation des sommes distribuables (onglet XIII).

    Paramètre
    ---------
    data : dict
        {
            "N":   {"balance_n": [...], "inventaire_n": [...], "pvmv": [...]},
            "N_1": {"balance_n_1": [...], ...}  # ou None si nouveau fonds
        }

    Retourne
    --------
    { "sommes_distribuables": { "meta": {...}, "revenus_nets": {...}, "pvmv_realisees": {...} } }
    """

    data_n  = data.get("N") or {}
    data_n1 = data.get("N_1")

    bal_n  = data_n.get("balance_n", [])
    bal_n1 = data_n1.get("balance_n_1", []) if data_n1 else []

    # ── Labels dynamiques ─────────────────────────────────────────────────
    # "Exercice N*" si c'est le premier exercice (pas de N-1)
    premier_exercice = data_n1 is None
    label_n  = "Exercice N*"   if premier_exercice else "Exercice N"
    label_n1 = "Exercice N-1*" if premier_exercice else "Exercice N-1"

    # ── Calculs ───────────────────────────────────────────────────────────
    revenus  = _revenus_nets(bal_n, bal_n1)
    pvmv     = _pvmv_realisees(bal_n, bal_n1)

    return {
        "sommes_distribuables": {
            "meta": {
                "label_exercice_n":  label_n,
                "label_exercice_n1": label_n1,
                "premier_exercice":  premier_exercice,
                "note_generale":     NOTE_GENERALE,
            },
            "revenus_nets":   revenus,
            "pvmv_realisees": pvmv,
        }
    }
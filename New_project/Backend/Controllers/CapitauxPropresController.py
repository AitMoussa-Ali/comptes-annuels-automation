"""
CapitauxPropresController.py
=============================
Génère la reconstitution de la ligne "Capitaux propres" (onglet III)
sous forme de dictionnaire, en reproduisant exactement les formules de
la macro Excel du fichier Comptes Annuels (onglet "III. Capitaux propres").

Entrées (format issu de UploadController / Data_extraction)
------------------------------------------------------------
data : dict
    {
        "N":   {"balance_n": [...], "inventaire_n": [...], "pvmv": [...]},
        "N_1": {"balance_n_1": [...], ...}   # ou None si nouveau fonds
    }

Sortie
------
{
    "capitaux_propres": {

        "meta": {
            "label_col_n":   str,   # "Cumul Exercice N" ou "Cumul Exercice N*"
            "label_col_n1":  str,   # "Cumul Exercice N-1" ou "Cumul Exercice N-1*"
            "premier_exercice": bool,
            "autres_elements_detail": {
                "frais_constitution": float | None,
                "prime_souscription": float | None,
            }
        },

        # Apports
        "capital_souscrit":               {"n": float, "n1": float, "variation": float},
        "capital_non_appele":             {"n": float, "n1": float, "variation": float},
        "emission_passifs_financement":   {"n": float, "n1": float, "variation": float},
        "sous_total_apports":             {"n": float, "n1": float, "variation": float},

        # Résultat de gestion
        "revenus_nets_exercice":          {"n": float, "n1": float, "variation": float},
        "cumul_revenus_nets_precedents":  {"n": float, "n1": float, "variation": float},
        "sous_total_resultat_gestion":    {"n": float, "n1": float, "variation": float},

        # Plus ou moins-values réalisées
        "pvmv_realisees_exercice":        {"n": float, "n1": float, "variation": float},
        "cumul_pvmv_realisees_precedents":{"n": float, "n1": float, "variation": float},
        "sous_total_pvmv_realisees":      {"n": float, "n1": float, "variation": float},

        # Variation PVMV latentes
        "pvmv_latentes_exercice":         {"n": float, "n1": float, "variation": float},
        "cumul_pvmv_latentes_precedents": {"n": float, "n1": float, "variation": float},
        "sous_total_pvmv_latentes":       {"n": float, "n1": float, "variation": float},

        # Boni de liquidation
        "boni_liquidation":               {"n": float, "n1": float, "variation": float},

        # Rachats et répartitions
        "rachats":                        {"n": float, "n1": float, "variation": float},
        "repartition_actifs":             {"n": float, "n1": float, "variation": float},
        "distribution_resultats_nets":    {"n": float, "n1": float, "variation": float},
        "distribution_pvmv_realisees":    {"n": float, "n1": float, "variation": float},
        "remboursement_passifs_fin":      {"n": float, "n1": float, "variation": float},
        "sous_total_rachats_repartitions":{"n": float, "n1": float, "variation": float},

        # Autres éléments
        "autres_elements":                {"n": float, "n1": float, "variation": float},
        "label_autres_elements":          str,  # "Autres éléments" ou "Autres éléments (3)"

        # Total final
        "total_capitaux_propres":         {"n": float, "n1": float, "variation": float},
    }
}

Formules reproduites depuis l'onglet "III. Capitaux propres"
-------------------------------------------------------------
Toutes les valeurs sont calculées comme :  net(compte) = Solde Crédit - Solde Débit

F6   Capital souscrit           = net("1011*") + net("103*") + net("1012*")
F7   Capital non appelé         = net("1021*") - net("1019*")
F8   Emission passifs fin.      = 0 (hardcodé)
F10  Revenus nets exercice      = net("70*")+net("71*")+net("72*") - net("60*")-net("61*")-net("62*")
F11  Cumul revenus nets préc.   = net("10150010")
F13  PVMV réal. exercice        = net("74*") + net("64*")
F14  Cumul PVMV réal. préc.     = net("10150020")
F17  PVMV lat. exercice         = net("75*") + net("65*") + net("68*")
F18  Cumul PVMV lat. préc.      = net("10150030")
F20  Boni de liquidation        = net("104*")
F22  Rachats                    = net("1022*")
F23  Répartition d'actifs       = net("109*")
F24  Distribution résultats     = net("791*")
F25  Distribution PVMV réal.    = net("794*")
F26  Remboursement passifs fin. = 0 (hardcodé)
F27  Autres éléments            = net("130*") + net("1014*")
F28  TOTAL                      = F5+F9+F12+F16+F20+F21+F27

Labels dynamiques :
  "Cumul Exercice N*"   si G28 (total N-1) = 0  → premier exercice
  "Autres éléments (3)" si F27 ≠ 0              → note de bas de tableau
  Détail F27 : frais_constitution = net("130*"), prime_souscription = net("1014*")
"""

from __future__ import annotations
from typing import Optional


# ─── Helper ──────────────────────────────────────────────────────────────────

def _to_float(v) -> float:
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _sumif(balance: list[dict], prefix: str, col: str) -> float:
    """SUMIF(balance.Compte, 'prefix*', balance[col])"""
    return sum(
        _to_float(row.get(col, 0))
        for row in balance
        if str(row.get("Compte", "")).startswith(prefix)
    )


def _net(balance: list[dict], prefix: str) -> float:
    """
    Solde net = Solde Crédit - Solde Débit pour tous les comptes commençant par `prefix`.
    Positif = créditeur, négatif = débiteur.
    """
    return (
        _sumif(balance, prefix, "Solde Crédit")
        - _sumif(balance, prefix, "Solde Débit")
    )


def _poste(n: float, n1: float) -> dict:
    """Construit un poste {n, n1, variation} avec arrondi."""
    return {
        "n":         round(n,  2),
        "n1":        round(n1, 2),
        "variation": round(n - n1, 2),
    }


# ─── Calcul pour un exercice ──────────────────────────────────────────────────

def _calculer(balance: list[dict]) -> dict:
    """
    Calcule tous les postes de la reconstitution des capitaux propres
    pour une balance donnée (N ou N-1).
    Retourne un dict plat avec toutes les valeurs de la colonne N (ou N-1).
    """

    # ── Apports ───────────────────────────────────────────────────────────
    # F6 : Capital souscrit (1) = net("1011*") + net("103*") + net("1012*")
    capital_souscrit = (
        _net(balance, "1011")
        + _net(balance, "103")
        + _net(balance, "1012")
    )

    # F7 : Capital non appelé (2) = net("1021*") - net("1019*")
    # Formule Excel : net(1021) + net(1019)  [tous deux négatifs si non appelés]
    capital_non_appele = _net(balance, "1021") + _net(balance, "1019")

    # F8 : Emission de passifs de financement = 0 (hardcodé)
    emission_passifs_fin = 0.0

    # F5 = F6 + F7 + F8
    sous_total_apports = capital_souscrit + capital_non_appele + emission_passifs_fin

    # ── Résultat de gestion ───────────────────────────────────────────────
    # F10 : Revenus nets de l'exercice
    #  = net("70*")+net("71*")+net("72*") - net("60*")-net("61*")-net("62*")
    # Formule Excel : SUMIF(70*,F)+SUMIF(71*,F)+SUMIF(72*,F)-SUMIF(60*,E)-SUMIF(61*,E)-SUMIF(62*,E)
    #                  -SUMIF(70*,E)+SUMIF(60*,F)+... = net(70)+net(71)+net(72)+net(60)+net(61)+net(62)
    # (le net des comptes 6x est négatif car débiteurs → soustraction naturelle)
    revenus_nets = (
        _net(balance, "70") + _net(balance, "71") + _net(balance, "72")
        + _net(balance, "60") + _net(balance, "61") + _net(balance, "62")
    )

    # F11 : Cumul des revenus nets des exercices précédents = net("10150010")
    cumul_revenus_precedents = _net(balance, "10150010")

    # F9 = F10 + F11
    sous_total_resultat_gestion = revenus_nets + cumul_revenus_precedents

    # ── Plus ou moins-values réalisées ────────────────────────────────────
    # F13 : PVMV réal. exercice = net("74*") + net("64*")
    pvmv_realisees = _net(balance, "74") + _net(balance, "64")

    # F14 : Cumul PVMV réal. préc. = net("10150020")
    cumul_pvmv_realisees_prec = _net(balance, "10150020")

    # F12 = F13 + F14
    sous_total_pvmv_realisees = pvmv_realisees + cumul_pvmv_realisees_prec

    # ── Variation des PVMV latentes ───────────────────────────────────────
    # F17 : PVMV lat. exercice = net("75*") + net("65*") + net("68*")
    pvmv_latentes = (
        _net(balance, "75") + _net(balance, "65") + _net(balance, "68")
    )

    # F18 : Cumul PVMV lat. préc. = net("10150030")
    cumul_pvmv_latentes_prec = _net(balance, "10150030")

    # F16 = F17 + F18
    sous_total_pvmv_latentes = pvmv_latentes + cumul_pvmv_latentes_prec

    # ── Boni de liquidation ───────────────────────────────────────────────
    # F20 : net("104*")
    boni_liquidation = _net(balance, "104")

    # ── Rachats et répartitions ───────────────────────────────────────────
    # F22 : Rachats = net("1022*")
    rachats = _net(balance, "1022")

    # F23 : Répartition d'actifs = net("109*")
    repartition_actifs = _net(balance, "109")

    # F24 : Distribution résultats nets = net("791*")
    distribution_resultats = _net(balance, "791")

    # F25 : Distribution PVMV réalisées = net("794*")
    distribution_pvmv = _net(balance, "794")

    # F26 : Remboursement passifs financement = 0 (hardcodé)
    remboursement_passifs = 0.0

    # F21 = F22+F23+F24+F25+F26
    sous_total_rachats = (
        rachats + repartition_actifs + distribution_resultats
        + distribution_pvmv + remboursement_passifs
    )

    # ── Autres éléments ───────────────────────────────────────────────────
    # F27 : net("130*") + net("1014*")
    frais_constitution  = _net(balance, "130")
    prime_souscription  = _net(balance, "1014")
    autres_elements     = frais_constitution + prime_souscription

    # ── Total capitaux propres ────────────────────────────────────────────
    # F28 = F5+F9+F12+F16+F20+F21+F27
    total = (
        sous_total_apports
        + sous_total_resultat_gestion
        + sous_total_pvmv_realisees
        + sous_total_pvmv_latentes
        + boni_liquidation
        + sous_total_rachats
        + autres_elements
    )

    return {
        "capital_souscrit":                capital_souscrit,
        "capital_non_appele":              capital_non_appele,
        "emission_passifs_financement":    emission_passifs_fin,
        "sous_total_apports":              sous_total_apports,
        "revenus_nets_exercice":           revenus_nets,
        "cumul_revenus_nets_precedents":   cumul_revenus_precedents,
        "sous_total_resultat_gestion":     sous_total_resultat_gestion,
        "pvmv_realisees_exercice":         pvmv_realisees,
        "cumul_pvmv_realisees_precedents": cumul_pvmv_realisees_prec,
        "sous_total_pvmv_realisees":       sous_total_pvmv_realisees,
        "pvmv_latentes_exercice":          pvmv_latentes,
        "cumul_pvmv_latentes_precedents":  cumul_pvmv_latentes_prec,
        "sous_total_pvmv_latentes":        sous_total_pvmv_latentes,
        "boni_liquidation":                boni_liquidation,
        "rachats":                         rachats,
        "repartition_actifs":              repartition_actifs,
        "distribution_resultats_nets":     distribution_resultats,
        "distribution_pvmv_realisees":     distribution_pvmv,
        "remboursement_passifs_financement": remboursement_passifs,
        "sous_total_rachats_repartitions": sous_total_rachats,
        "autres_elements":                 autres_elements,
        "_frais_constitution":             frais_constitution,   # pour le détail note (3)
        "_prime_souscription":             prime_souscription,   # pour le détail note (3)
        "total_capitaux_propres":          total,
    }


# ─── Contrôleur principal ─────────────────────────────────────────────────────

async def CapitauxPropresController(data: dict) -> dict:
    """
    Génère la reconstitution de la ligne "Capitaux propres" (onglet III).

    Paramètre
    ---------
    data : dict
        Même structure que BilanController / CompteResultatController :
        {
            "N":   {"balance_n": [...], "inventaire_n": [...], "pvmv": [...]},
            "N_1": {"balance_n_1": [...], ...}  # ou None
        }

    Retourne
    --------
    {
        "capitaux_propres": {
            "meta": { label_col_n, label_col_n1, premier_exercice,
                      autres_elements_detail },
            <tous les postes avec {n, n1, variation}>,
        }
    }
    """

    # ── Données ───────────────────────────────────────────────────────────
    data_n  = data.get("N") or {}
    data_n1 = data.get("N_1")

    balance_n  = data_n.get("balance_n", [])
    balance_n1 = data_n1.get("balance_n_1", []) if data_n1 else []

    # ── Calcul des deux exercices ─────────────────────────────────────────
    vals_n  = _calculer(balance_n)
    vals_n1 = _calculer(balance_n1)

    # ── Labels dynamiques ─────────────────────────────────────────────────
    # "Cumul Exercice N*" si c'est le premier exercice (total N-1 = 0)
    premier_exercice = (vals_n1["total_capitaux_propres"] == 0.0)
    label_n  = "Cumul Exercice N*"  if premier_exercice else "Cumul Exercice N"
    label_n1 = "Cumul Exercice N-1*" if (data_n1 is None) else "Cumul Exercice N-1"

    # "Autres éléments (3)" si la valeur N est non nulle
    label_autres = (
        "Autres éléments (3)"
        if vals_n["autres_elements"] != 0.0
        else "Autres éléments"
    )

    # Détail de la note (3) : afficher uniquement les composantes non nulles
    detail_autres = {}
    if vals_n["_frais_constitution"] != 0.0:
        detail_autres["frais_constitution"] = round(vals_n["_frais_constitution"], 2)
    if vals_n["_prime_souscription"] != 0.0:
        detail_autres["prime_souscription"] = round(vals_n["_prime_souscription"], 2)

    # ── Construction du résultat final ────────────────────────────────────
    def p(key: str) -> dict:
        """Construit le poste {n, n1, variation} pour une clé donnée."""
        return _poste(vals_n[key], vals_n1[key])

    return {
        "capitaux_propres": {

            "meta": {
                "label_col_n":      label_n,
                "label_col_n1":     label_n1,
                "premier_exercice": premier_exercice,
                "autres_elements_detail": detail_autres,
            },

            # ── Apports ──────────────────────────────────────────────────
            "capital_souscrit":             p("capital_souscrit"),
            "capital_non_appele":           p("capital_non_appele"),
            "emission_passifs_financement": p("emission_passifs_financement"),
            "sous_total_apports":           p("sous_total_apports"),

            # ── Résultat de gestion ───────────────────────────────────────
            "revenus_nets_exercice":         p("revenus_nets_exercice"),
            "cumul_revenus_nets_precedents": p("cumul_revenus_nets_precedents"),
            "sous_total_resultat_gestion":   p("sous_total_resultat_gestion"),

            # ── PVMV réalisées ────────────────────────────────────────────
            "pvmv_realisees_exercice":          p("pvmv_realisees_exercice"),
            "cumul_pvmv_realisees_precedents":  p("cumul_pvmv_realisees_precedents"),
            "sous_total_pvmv_realisees":        p("sous_total_pvmv_realisees"),

            # ── PVMV latentes ─────────────────────────────────────────────
            "pvmv_latentes_exercice":           p("pvmv_latentes_exercice"),
            "cumul_pvmv_latentes_precedents":   p("cumul_pvmv_latentes_precedents"),
            "sous_total_pvmv_latentes":         p("sous_total_pvmv_latentes"),

            # ── Boni de liquidation ───────────────────────────────────────
            "boni_liquidation": p("boni_liquidation"),

            # ── Rachats et répartitions ───────────────────────────────────
            "rachats":                            p("rachats"),
            "repartition_actifs":                 p("repartition_actifs"),
            "distribution_resultats_nets":        p("distribution_resultats_nets"),
            "distribution_pvmv_realisees":        p("distribution_pvmv_realisees"),
            "remboursement_passifs_financement":  p("remboursement_passifs_financement"),
            "sous_total_rachats_repartitions":    p("sous_total_rachats_repartitions"),

            # ── Autres éléments ───────────────────────────────────────────
            "label_autres_elements": label_autres,
            "autres_elements":       p("autres_elements"),

            # ── Total ─────────────────────────────────────────────────────
            "total_capitaux_propres": p("total_capitaux_propres"),
        }
    }
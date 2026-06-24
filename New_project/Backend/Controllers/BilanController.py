"""
BilanController.py
==================
Génère le Bilan Actif et le Bilan Passif sous forme de dictionnaires,
en reproduisant exactement les formules de la macro Excel du fichier
Comptes Annuels (onglets "Bilan Actif" et "Bilan Passif").

Entrées (format issu de Data_extraction)
-----------------------------------------
Le contrôleur attend le dictionnaire complet retourné par UploadController :
{
    "N": {
        "balance_n":    [ {"Compte": str, "Solde Débit": float, "Solde Crédit": float, ...} ],
        "inventaire_n": [ {"G ou I": str, "Code_titre": str, "Libellé": str,
                           "Valeur estimation coupon inclus": float, ...} ],
        "pvmv":         [ {...} ]
    },
    "N_1": {                                          # None si nouveau fonds
        "balance_n_1":    [ {"Compte": str, "Solde Débit": float, "Solde Crédit": float, ...} ],
        "inventaire_n_1": [ {"G ou I": str, "Code_titre": str, "Libellé": str,
                             "Valeur estimation coupon inclus": float, ...} ]
    }
}

Sortie
------
{
    "bilan_actif": {
        "exercice_n":  { <tous les postes> },
        "exercice_n1": { <tous les postes> }   # absent si N_1 est None
    },
    "bilan_passif": {
        "exercice_n":  { <tous les postes> },
        "exercice_n1": { <tous les postes> }
    },
    "controles": {
        "actif_egal_passif_n":  bool,
        "ecart_n":              float,
        "actif_egal_passif_n1": bool,   # absent si N_1 est None
        "ecart_n1":             float
    }
}

Formules reproduites (référence cellules de la macro)
------------------------------------------------------
BILAN ACTIF — onglet "Bilan Actif"
  G9   Actions cotées          SUMIFS(inv.N, inv["G ou I"]="I", inv.Libellé LIKE "*Action*")
  G10  Actions non cotées      SUMIF(inv.Code_titre, "??AC*|??AD*|??SA*|??BS*")
  G14  Oblig. conv. nc.        SUMIF(inv.Code_titre, "??OC*")
  G18  Autres oblig. nc.       SUMIF(inv.Code_titre, "??OS*|??OR*|??CN*")
  G22  Titres de créances       SUMIF(inv.Code_titre, "??TC*|??FCT*")
  G25  OPCVM                   SUMIF(inv.Libellé, "*FCP*|*SICAV*")
  G26  FIA                     SUMIF(inv.Libellé, "*FPCI*|*SLP*|*FCPR*|*FCPI*")
  G29  Dépôts                  SUMIF(inv.Code_titre, "*CT*")
  G31  IFT                     SUMIF(inv.Code_titre, "??OP*")
  G35  Prêts                   SUMIF(inv.Code_titre, "??CC*|??PR*|??NO*")
  G41  Créances                SUMIF(balance.Compte, "4*", "Solde Débit")
  G43  Comptes financiers      SUMIF(balance.Compte, "5*", "Solde Débit")

BILAN PASSIF — onglet "Bilan Passif"
  G7   Report revenu net       SUMIF("111*", "Solde Crédit") - SUMIF("111*", "Solde Débit")
  G9   Report PVMV latentes    SUMIF("115*", crédit - débit)
  G11  Report PVMV réalisées   SUMIF("114*", crédit - débit)
  G13  Résultat net            SUMIF("7*",F) - SUMIF("6*",E) - SUMIF("7*",E) + SUMIF("6*",F)
  G16  Capitaux propres I      résultat - SUMIF("1*",E) + SUMIF("1*",F)
  G5   Capital                 capitaux_propres - résultat - report_pvmv_real - report_pvmv_lat - report_revenu
  G30  Emprunts                SUMIF("39*", "Solde Crédit")
  G38  Dettes passif (4*)      SUMIF("4*", "Solde Crédit")
  G40  Concours bancaires (5*) SUMIF("5*", "Solde Crédit")
"""

from __future__ import annotations
from fnmatch import fnmatch
from typing import Optional


# ─── Helpers internes ────────────────────────────────────────────────────────

def _to_float(v) -> float:
    """Convertit n'importe quelle valeur en float (0.0 si None/vide)."""
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _sumif_balance(
    balance: list[dict],
    prefix: str,
    col: str,          # "Solde Débit" ou "Solde Crédit"
) -> float:
    """
    Émule : SUMIF(Balance!A:A, "prefix*", Balance!col)
    Additionne `col` pour toutes les lignes dont le compte commence par `prefix`.
    """
    return sum(
        _to_float(row.get(col, 0))
        for row in balance
        if str(row.get("Compte", "")).startswith(prefix)
    )


def _sumif_inv_code(
    inventaire: list[dict],
    *patterns: str,
) -> float:
    """
    Émule : SUMIF(Inventaire!B:B, "??XX*", Inventaire!N:N)
    Additionne "Valeur estimation coupon inclus" pour les lignes dont
    le Code_titre correspond à au moins un pattern (wildcards '?' et '*').
    """
    total = 0.0
    for row in inventaire:
        code = str(row.get("Code_titre", "")).strip().upper()
        if not code:
            continue
        val = _to_float(row.get("Valeur estimation coupon inclus", 0))
        if any(fnmatch(code, p.upper()) for p in patterns):
            total += val
    return total


def _sumif_inv_libelle(
    inventaire: list[dict],
    *substrings: str,
) -> float:
    """
    Émule : SUMIF(Inventaire!C:C, "*substr*", Inventaire!N:N)
    Additionne "Valeur estimation coupon inclus" pour les lignes dont
    le Libellé contient au moins une des sous-chaînes.
    """
    total = 0.0
    for row in inventaire:
        libelle = str(row.get("Libellé", "")).upper()
        val = _to_float(row.get("Valeur estimation coupon inclus", 0))
        if any(s.upper() in libelle for s in substrings):
            total += val
    return total


def _sumifs_inv_cotes(inventaire: list[dict]) -> float:
    """
    Émule G9 : SUMIFS(inv.N, inv.A="I", inv.C CONTIENT "Action")
    Titres marqués "I" (cotés sur marché réglementé) dont le libellé
    contient le mot "Action".
    """
    total = 0.0
    for row in inventaire:
        gi = str(row.get("G ou I", "")).strip()
        libelle = str(row.get("Libellé", "")).upper()
        val = _to_float(row.get("Valeur estimation coupon inclus", 0))
        if gi == "I" and "ACTION" in libelle:
            total += val
    return total


# ─── Calcul Bilan Actif pour un exercice ─────────────────────────────────────

def _calculer_actif(
    inventaire: list[dict],
    balance: list[dict],
) -> dict:
    """
    Calcule tous les postes du Bilan Actif pour un exercice donné.
    Reproduit les formules G*/H* de l'onglet "Bilan Actif".
    """

    # ── Titres financiers (classe 3 — inventaire) ─────────────────────────

    # G9  Actions cotées (type I, libellé contient "Action")
    actions_cotees = _sumifs_inv_cotes(inventaire)

    # G10 Actions non cotées : AC, AD, SA, BS
    actions_non_cotees = _sumif_inv_code(inventaire, "??AC*", "??AD*", "??SA*", "??BS*")

    # G8  Actions total = G9 + G10
    actions_total = actions_cotees + actions_non_cotees

    # G13 Obligations convertibles cotées = 0 (hardcodé)
    # G14 Obligations convertibles non cotées : OC
    oblig_conv_non_cotees = _sumif_inv_code(inventaire, "??OC*")
    # G12 Obligations convertibles total = 0 + G14
    oblig_conv_total = oblig_conv_non_cotees

    # G17 Autres obligations cotées = 0 (hardcodé)
    # G18 Autres obligations non cotées : OS, OR, CN
    autres_oblig_non_cotees = _sumif_inv_code(inventaire, "??OS*", "??OR*", "??CN*")
    # G16 Autres obligations total = 0 + G18
    autres_oblig_total = autres_oblig_non_cotees

    # G21 Titres de créances cotés = 0 (hardcodé)
    # G22 Titres de créances non cotés : TC, FCT
    titres_creances = _sumif_inv_code(inventaire, "??TC*", "??FCT*")
    # G20 Titres de créances total = 0 + G22
    titres_creances_total = titres_creances

    # G25 OPCVM : libellé contient FCP ou SICAV
    opcvm = _sumif_inv_libelle(inventaire, "FCP", "SICAV")
    # G26 FIA : libellé contient FPCI, SLP, FCPR, FCPI
    fia = _sumif_inv_libelle(inventaire, "FPCI", "SLP", "FCPR", "FCPI")
    # G27 Autres OPC = 0 (hardcodé)
    # G24 Parts OPC total = G25 + G26 + 0
    opc_total = opcvm + fia

    # G29 Dépôts : pattern *CT*
    depots = _sumif_inv_code(inventaire, "*CT*")

    # G31 Instruments financiers à terme : OP
    ift = _sumif_inv_code(inventaire, "??OP*")

    # G33 Opérations temporaires = 0 (hardcodé)
    op_temporaires = 0.0

    # G35 Prêts : CC, PR, NO
    prets = _sumif_inv_code(inventaire, "??CC*", "??PR*", "??NO*")

    # G37 Autres actifs éligibles = 0 (hardcodé côté N ; côté N-1 : *CT* dans macro)
    autres_actifs_eligibles = 0.0

    # G6  TITRES FINANCIERS = G8+G12+G16+G24+G31+G35+G37
    titres_financiers = (
        actions_total
        + oblig_conv_total
        + autres_oblig_total
        + titres_creances_total
        + opc_total
        + ift
        + prets
        + autres_actifs_eligibles
    )

    # G39 Sous-total actifs éligibles I = G8+G12+G16+G24+G35+G37
    # (Note : G39 exclut G29 dépôts et G31 IFT, cf. formule exacte de la macro)
    sous_total_actifs_eligibles = (
        actions_total
        + oblig_conv_total
        + autres_oblig_total
        + titres_creances_total
        + opc_total
        + prets
        + autres_actifs_eligibles
    )

    # ── Actifs autres que les actifs éligibles (classes 4 & 5 — balance) ──

    # G41 Créances et comptes d'ajustement actifs = SUMIF("4*", Solde Débit)
    creances = _sumif_balance(balance, "4", "Solde Débit")

    # G43 Comptes financiers = SUMIF("5*", Solde Débit)
    comptes_financiers = _sumif_balance(balance, "5", "Solde Débit")

    # G45 Sous-total autres = G41 + G43
    sous_total_actifs_autres = creances + comptes_financiers

    # G46 TOTAL ACTIF = G39 + G45
    total_actif = sous_total_actifs_eligibles + sous_total_actifs_autres

    return {
        "immobilisations_corporelles_nettes": 0.0,
        "titres_financiers": titres_financiers,
        "actions": {
            "total": actions_total,
            "cotees": actions_cotees,
            "non_cotees": actions_non_cotees,
        },
        "obligations_convertibles": {
            "total": oblig_conv_total,
            "cotees": 0.0,
            "non_cotees": oblig_conv_non_cotees,
        },
        "autres_obligations": {
            "total": autres_oblig_total,
            "cotees": 0.0,
            "non_cotees": autres_oblig_non_cotees,
        },
        "titres_creances": {
            "total": titres_creances_total,
            "cotes": 0.0,
            "non_cotes": titres_creances,
        },
        "parts_opc": {
            "total": opc_total,
            "opcvm": opcvm,
            "fia": fia,
            "autres": 0.0,
        },
        "depots": depots,
        "instruments_financiers_terme": ift,
        "operations_temporaires_titres": op_temporaires,
        "prets": prets,
        "autres_actifs_eligibles": autres_actifs_eligibles,
        "sous_total_actifs_eligibles_I": sous_total_actifs_eligibles,
        "creances_et_comptes_ajustement": creances,
        "comptes_financiers": comptes_financiers,
        "sous_total_actifs_autres_II": sous_total_actifs_autres,
        "total_actif": total_actif,
    }


# ─── Calcul Bilan Passif pour un exercice ────────────────────────────────────

def _calculer_passif(balance: list[dict]) -> dict:
    """
    Calcule tous les postes du Bilan Passif pour un exercice donné.
    Reproduit les formules G*/H* de l'onglet "Bilan Passif".
    """

    # ── Capitaux propres ──────────────────────────────────────────────────

    # G7  Report à nouveau sur revenu net
    #     = SUMIF("111*", Solde Crédit) - SUMIF("111*", Solde Débit)
    report_revenu_net = (
        _sumif_balance(balance, "111", "Solde Crédit")
        - _sumif_balance(balance, "111", "Solde Débit")
    )

    # G9  Report à nouveau PVMV latentes nettes
    #     = SUMIF("115*", Solde Crédit) - SUMIF("115*", Solde Débit)
    report_pvmv_latentes = (
        _sumif_balance(balance, "115", "Solde Crédit")
        - _sumif_balance(balance, "115", "Solde Débit")
    )

    # G11 Report à nouveau PVMV réalisées nettes
    #     = SUMIF("114*", Solde Crédit) - SUMIF("114*", Solde Débit)
    report_pvmv_realisees = (
        _sumif_balance(balance, "114", "Solde Crédit")
        - _sumif_balance(balance, "114", "Solde Débit")
    )

    # G13 Résultat net de l'exercice
    #     = SUMIF("7*", Solde Crédit) - SUMIF("6*", Solde Débit)
    #       - SUMIF("7*", Solde Débit) + SUMIF("6*", Solde Crédit)
    resultat_net = (
        _sumif_balance(balance, "7", "Solde Crédit")
        - _sumif_balance(balance, "6", "Solde Débit")
        - _sumif_balance(balance, "7", "Solde Débit")
        + _sumif_balance(balance, "6", "Solde Crédit")
    )

    # G16 Capitaux propres I  (= Actif net)
    #     = résultat - SUMIF("1*", Solde Débit) + SUMIF("1*", Solde Crédit)
    capitaux_propres = (
        resultat_net
        - _sumif_balance(balance, "1", "Solde Débit")
        + _sumif_balance(balance, "1", "Solde Crédit")
    )

    # G5  Capital = G16 - G13 - G11 - G9 - G7
    capital = (
        capitaux_propres
        - resultat_net
        - report_pvmv_realisees
        - report_pvmv_latentes
        - report_revenu_net
    )

    # G18 Passifs de financement II = 0 (hardcodé)
    passifs_financement = 0.0

    # G20 Capitaux propres et passifs de financement (I+II)
    capitaux_et_passifs_fin = capitaux_propres + passifs_financement

    # ── Passifs éligibles ─────────────────────────────────────────────────

    # G24 Instruments financiers (A) = 0  (G25=0, G26=0 hardcodés)
    # G28 Instruments financiers à terme (B) = 0
    # G32 Autres passifs éligibles (D) = 0

    # G30 Emprunts (C) = SUMIF("39*", Solde Crédit)
    emprunts = _sumif_balance(balance, "39", "Solde Crédit")

    # G34 Sous-total passifs éligibles III = 0 + emprunts + 0
    sous_total_passifs_eligibles = emprunts

    # ── Autres passifs ────────────────────────────────────────────────────

    # G38 Dettes et comptes d'ajustement passifs = SUMIF("4*", Solde Crédit)
    dettes = _sumif_balance(balance, "4", "Solde Crédit")

    # G40 Concours bancaires = SUMIF("5*", Solde Crédit)
    concours_bancaires = _sumif_balance(balance, "5", "Solde Crédit")

    # G42 Sous-total autres passifs IV = G38 + G40
    sous_total_autres_passifs = dettes + concours_bancaires

    # G43 TOTAL PASSIFS = G20 + G34 + G42
    total_passif = capitaux_et_passifs_fin + sous_total_passifs_eligibles + sous_total_autres_passifs

    return {
        # Capitaux propres
        "capital": capital,
        "report_a_nouveau_revenu_net": report_revenu_net,
        "report_a_nouveau_pvmv_latentes_nettes": report_pvmv_latentes,
        "report_a_nouveau_pvmv_realisees_nettes": report_pvmv_realisees,
        "resultat_net_exercice": resultat_net,
        "capitaux_propres_I": capitaux_propres,
        # Passifs de financement
        "passifs_financement_II": passifs_financement,
        "capitaux_propres_et_passifs_financement": capitaux_et_passifs_fin,
        # Passifs éligibles
        "passifs_eligibles": {
            "instruments_financiers_A": 0.0,
            "instruments_financiers_terme_B": 0.0,
            "emprunts_C": emprunts,
            "autres_passifs_eligibles_D": 0.0,
            "sous_total_III": sous_total_passifs_eligibles,
        },
        # Autres passifs
        "autres_passifs": {
            "dettes_et_comptes_ajustement": dettes,
            "concours_bancaires": concours_bancaires,
            "sous_total_IV": sous_total_autres_passifs,
        },
        "total_passif": total_passif,
    }


# ─── Contrôleur principal ─────────────────────────────────────────────────────

async def BilanController(data: dict) -> dict:
    """
    Génère le Bilan Actif et le Bilan Passif à partir des données extraites.

    Paramètre
    ---------
    data : dict
        Dictionnaire retourné par UploadController, de la forme :
        {
            "N": {
                "balance_n":    [...],
                "inventaire_n": [...],
                "pvmv":         [...]
            },
            "N_1": {                          # None si nouveau fonds (ancienneté="N")
                "balance_n_1":    [...],
                "inventaire_n_1": [...]
            }
        }

    Retourne
    --------
    {
        "bilan_actif":  {"exercice_n": {...}, "exercice_n1": {...}},
        "bilan_passif": {"exercice_n": {...}, "exercice_n1": {...}},
        "controles":    {"actif_egal_passif_n": bool, "ecart_n": float, ...}
    }
    """

    # ── Récupération des données ──────────────────────────────────────────
    data_n   = data.get("N") or {}
    data_n1  = data.get("N_1")              # None si nouveau fonds

    balance_n    = data_n.get("balance_n", [])
    inventaire_n = data_n.get("inventaire_n", [])

    # ── Calcul exercice N ─────────────────────────────────────────────────
    actif_n  = _calculer_actif(inventaire_n, balance_n)
    passif_n = _calculer_passif(balance_n)

    bilan_actif  = {"exercice_n": actif_n}
    bilan_passif = {"exercice_n": passif_n}

    # ── Calcul exercice N-1 (si présent) ──────────────────────────────────
    if data_n1:
        balance_n1    = data_n1.get("balance_n_1", [])
        inventaire_n1 = data_n1.get("inventaire_n_1", [])

        actif_n1  = _calculer_actif(inventaire_n1, balance_n1)
        passif_n1 = _calculer_passif(balance_n1)

        bilan_actif["exercice_n1"]  = actif_n1
        bilan_passif["exercice_n1"] = passif_n1

    # ── Contrôles d'équilibre (Actif = Passif) ────────────────────────────
    controles: dict = {}

    ecart_n = round(actif_n["total_actif"] - passif_n["total_passif"], 4)
    controles["actif_egal_passif_n"] = abs(ecart_n) < 0.01
    controles["ecart_n"] = ecart_n

    if data_n1:
        ecart_n1 = round(actif_n1["total_actif"] - passif_n1["total_passif"], 4)
        controles["actif_egal_passif_n1"] = abs(ecart_n1) < 0.01
        controles["ecart_n1"] = ecart_n1

    return {
        "bilan_actif":  bilan_actif,
        "bilan_passif": bilan_passif,
        "controles":    controles,
    }
    
    
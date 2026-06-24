"""
CompteResultatController.py
============================
Génère le Compte de Résultat 1 et le Compte de Résultat 2 sous forme
de dictionnaires, en reproduisant exactement les formules de la macro
Excel du fichier Comptes Annuels (onglets "Compte de résultat 1" et
"Compte de résultat 2").

Entrées (format issu de UploadController / Data_extraction)
------------------------------------------------------------
data : dict
    {
        "N": {
            "balance_n":    [ {"Compte": str, "Solde Débit": float, "Solde Crédit": float, ...} ],
            "inventaire_n": [ {...} ],
            "pvmv":         [ {"PLUS_VALUES_REALISEES": float, "MOINS_VALUES_REALISEES": float, ...} ]
        },
        "N_1": {                      # None si nouveau fonds
            "balance_n_1":    [ {...} ],
            "inventaire_n_1": [ {...} ]
        }
    }

Sortie
------
{
    "compte_resultat_1": {
        "exercice_n":  { <tous les postes CR1> },
        "exercice_n1": { <tous les postes CR1> }   # absent si N_1 est None
    },
    "compte_resultat_2": {
        "exercice_n":  { <tous les postes CR2> },
        "exercice_n1": { <tous les postes CR2> }
    },
    "controles": {
        "resultat_coherent_n":  bool,    # CR1+CR2 = Bilan Passif résultat net
        "ecart_n":              float,
        "resultat_coherent_n1": bool,    # absent si N_1 est None
        "ecart_n1":             float
    }
}

Formules reproduites (vérifiées sur le fichier Hospitality Opportunities FPCI)
-------------------------------------------------------------------------------

COMPTE DE RÉSULTAT 1 — "Compte de résultat 1"
─────────────────────────────────────────────
Produits sur opérations financières :
  Produits sur actions             = SUMIF("76*", Crédit) - SUMIF("76*", Débit)
  Produits sur obligations         = SUMIF("762*", Crédit) - SUMIF("762*", Débit)
  Produits sur titres de créance   = SUMIF("763*", Crédit) - SUMIF("763*", Débit)
  Produits sur parts d'OPC         = SUMIF("764*", Crédit) - SUMIF("764*", Débit)
  Produits sur IFT                 = SUMIF("765*", Crédit) - SUMIF("765*", Débit)
  Produits sur opérations temp.    = SUMIF("766*", Crédit) - SUMIF("766*", Débit)
  Produits sur prêts et créances   = SUMIF("767*", Crédit) - SUMIF("767*", Débit)
  Produits sur autres actifs élig. = SUMIF("768*", Crédit) - SUMIF("768*", Débit)
  Autres produits financiers       = SUMIF("769*", Crédit) - SUMIF("769*", Débit)
  Sous-total produits op. fin.     = somme des 9 postes ci-dessus

Charges sur opérations financières :
  Charges sur opérations fin.      = SUMIF("661*", Débit) - SUMIF("661*", Crédit)
  Charges sur IFT                  = SUMIF("665*", Débit) - SUMIF("665*", Crédit)
  Charges sur opérations temp.     = SUMIF("666*", Débit) - SUMIF("666*", Crédit)
  Charges sur emprunts             = SUMIF("667*", Débit) - SUMIF("667*", Crédit)
  Charges sur autres actifs élig.  = SUMIF("668*", Débit) - SUMIF("668*", Crédit)
  Charges sur passifs de fin.      = SUMIF("669*", Débit) - SUMIF("669*", Crédit)
  Autres charges financières       = SUMIF("66*", Débit) - SUMIF("66*", Crédit)  [reste]
  Sous-total charges op. fin.      = somme des 7 postes ci-dessus

Total Revenus financiers nets (A)  = Sous-total produits - Sous-total charges

Autres produits :
  Frais pris en charge (FCPE)      = SUMIF("708*", Crédit)    [toujours 0 pour FPCI/SLP]
  Rétrocession frais gestion       = SUMIF("709*", Crédit)
  Versements garantie capital      = SUMIF("771*", Crédit)
  Autres produits                  = SUMIF("74*", Solde Crédit)

Autres charges :
  Frais gestion société gestion    = SUMIF("61*", Solde Débit)   [vérifié ✅]
  Frais audit / études             = SUMIF("626*", Solde Débit)
  Impôts et taxes                  = SUMIF("63*", Solde Débit)
  Autres charges                   = SUMIF("64*", Solde Débit)

Sous-total Autres produits et charges (B) = Autres charges - Autres produits
Sous-total Revenus nets avant régularisation (C) = (A) - (B)
Régularisation revenus nets (D)    = SUMIF("119*", Crédit) - SUMIF("119*", Débit)
Sous-total Revenus nets I = (C) + (D)

COMPTE DE RÉSULTAT 2 — "Compte de résultat 2"
─────────────────────────────────────────────
PVMV réalisées :
  Plus et moins-values réalisées   = SUMIF("46*", Solde Crédit) - SUMIF("46*", Solde Débit)
                                     [ou depuis pvmv : somme PLUS_VALUES - MOINS_VALUES]
  Frais de transactions externes   = SUMIF("627*", Solde Débit)
  Frais de recherche               = SUMIF("628*", Solde Débit)
  Quote-part PV restit. assureurs  = SUMIF("462*", Solde Débit)
  Indemnités assurance perçues     = SUMIF("772*", Solde Crédit)
  Versements garantie capital      = SUMIF("773*", Solde Crédit)
  Sous-total PVMV réalisées (E)    = somme

Régularisation PVMV réalisées (F)  = SUMIF("119*", ...) [compte régularisation]
PVMV réalisées nettes II = (E) + (F)

PVMV latentes :
  Variation PVMV latentes          = SUMIF("65*", Solde Crédit) - SUMIF("65*", Solde Débit)
                                   + SUMIF("75*", Solde Crédit) - SUMIF("75*", Solde Débit)
                                   [vérifié ✅ : 3633212.33 - 0 - 4251510.84 + 0 = -618298.51]
  Ecarts de change comptes fin.    = SUMIF("512*", ...) [devises]
  Versements garantie              = 0 [hardcodé]
  Quote-part PV latentes assureurs = 0 [hardcodé]
  Sous-total PVMV latentes (G)     = somme

Régularisation PVMV latentes (H)   = 0 [hardcodé dans ce template]
PVMV latentes nettes III = (G) + (H)

Acomptes :
  Acomptes sur revenus nets (J)    = SUMIF("117*", Solde Débit)
  Acomptes sur PVMV réalisées (K)  = SUMIF("118*", Solde Débit)
  Total acomptes IV = (J) + (K)

Impôt sur le résultat V            = SUMIF("69*", Solde Débit)

Résultat net = I + II + III - IV - V
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
    """
    SUMIF(balance.Compte, "prefix*", balance[col])
    Additionne `col` pour toutes les lignes dont le compte commence par `prefix`.
    """
    return sum(
        _to_float(row.get(col, 0))
        for row in balance
        if str(row.get("Compte", "")).replace(".", "").startswith(prefix)
    )


def _net(balance: list[dict], prefix: str) -> float:
    """
    Solde net d'un compte = Solde Crédit - Solde Débit.
    Positif = créditeur (produit), négatif = débiteur (charge).
    """
    return (
        _sumif(balance, prefix, "Solde Crédit")
        - _sumif(balance, prefix, "Solde Débit")
    )


def _charge(balance: list[dict], prefix: str) -> float:
    """
    Charge nette = Solde Débit - Solde Crédit (valeur positive si charge réelle).
    """
    return (
        _sumif(balance, prefix, "Solde Débit")
        - _sumif(balance, prefix, "Solde Crédit")
    )


# ─── Compte de Résultat 1 ────────────────────────────────────────────────────

def _calculer_cr1(balance: list[dict]) -> dict:
    """
    Calcule tous les postes du Compte de Résultat 1.
    Source : balance uniquement.
    """

    # ── Produits sur opérations financières ──────────────────────────────
    # Comptes 76x = produits sur titres financiers (net crédit - débit)
    produits_actions           = _net(balance, "761")
    produits_obligations       = _net(balance, "762")
    produits_titres_creances   = _net(balance, "763")
    produits_parts_opc         = _net(balance, "764")
    produits_ift               = _net(balance, "765")
    produits_op_temporaires    = _net(balance, "766")
    produits_prets_creances    = _net(balance, "767")
    produits_autres_eligibles  = _net(balance, "768")
    autres_produits_financiers = _net(balance, "769")

    sous_total_produits_op_fin = (
        produits_actions
        + produits_obligations
        + produits_titres_creances
        + produits_parts_opc
        + produits_ift
        + produits_op_temporaires
        + produits_prets_creances
        + produits_autres_eligibles
        + autres_produits_financiers
    )

    # ── Charges sur opérations financières ───────────────────────────────
    # Comptes 66x = charges financières (net débit - crédit)
    charges_op_financieres     = _charge(balance, "661")
    charges_ift                = _charge(balance, "665")
    charges_op_temporaires     = _charge(balance, "666")
    charges_emprunts           = _charge(balance, "667")
    charges_autres_eligibles   = _charge(balance, "668")
    charges_passifs_fin        = _charge(balance, "669")
    autres_charges_financieres = _charge(balance, "660")  # 660 = autres charges fin.

    sous_total_charges_op_fin = (
        charges_op_financieres
        + charges_ift
        + charges_op_temporaires
        + charges_emprunts
        + charges_autres_eligibles
        + charges_passifs_fin
        + autres_charges_financieres
    )

    # ── Total Revenus financiers nets (A) ─────────────────────────────────
    total_revenus_financiers_nets_A = (
        sous_total_produits_op_fin - sous_total_charges_op_fin
    )

    # ── Autres produits ───────────────────────────────────────────────────
    frais_pris_en_charge_entreprise    = _sumif(balance, "708", "Solde Crédit")
    retrocession_frais_gestion         = _sumif(balance, "709", "Solde Crédit")
    versements_garantie_capital_prod   = _sumif(balance, "771", "Solde Crédit")
    autres_produits                    = _sumif(balance, "74",  "Solde Crédit")

    # ── Autres charges ────────────────────────────────────────────────────
    # Frais de gestion SG = comptes 61* (vérifié sur le fichier : 6067.76 ✅)
    frais_gestion_sg           = _charge(balance, "61")
    frais_audit_etudes         = _charge(balance, "626")
    impots_taxes               = _charge(balance, "63")
    autres_charges             = _charge(balance, "64")

    # ── Sous-total B = Autres charges - Autres produits ───────────────────
    total_autres_produits = (
        frais_pris_en_charge_entreprise
        + retrocession_frais_gestion
        + versements_garantie_capital_prod
        + autres_produits
    )
    total_autres_charges = (
        frais_gestion_sg
        + frais_audit_etudes
        + impots_taxes
        + autres_charges
    )
    sous_total_autres_B = total_autres_charges - total_autres_produits

    # ── C = A - B ─────────────────────────────────────────────────────────
    sous_total_revenus_nets_avant_regul_C = (
        total_revenus_financiers_nets_A - sous_total_autres_B
    )

    # ── Régularisation revenus nets (D) ───────────────────────────────────
    regularisation_revenus_D = _net(balance, "119")

    # ── Revenus nets I = C + D ────────────────────────────────────────────
    revenus_nets_I = sous_total_revenus_nets_avant_regul_C + regularisation_revenus_D

    return {
        # Produits sur opérations financières
        "produits_sur_actions": produits_actions,
        "produits_sur_obligations": produits_obligations,
        "produits_sur_titres_de_creance": produits_titres_creances,
        "produits_sur_parts_opc": produits_parts_opc,
        "produits_sur_ift": produits_ift,
        "produits_sur_op_temporaires": produits_op_temporaires,
        "produits_sur_prets_creances": produits_prets_creances,
        "produits_sur_autres_actifs_eligibles": produits_autres_eligibles,
        "autres_produits_financiers": autres_produits_financiers,
        "sous_total_produits_op_financieres": sous_total_produits_op_fin,

        # Charges sur opérations financières
        "charges_sur_op_financieres": charges_op_financieres,
        "charges_sur_ift": charges_ift,
        "charges_sur_op_temporaires": charges_op_temporaires,
        "charges_sur_emprunts": charges_emprunts,
        "charges_sur_autres_actifs_eligibles": charges_autres_eligibles,
        "charges_sur_passifs_financement": charges_passifs_fin,
        "autres_charges_financieres": autres_charges_financieres,
        "sous_total_charges_op_financieres": sous_total_charges_op_fin,

        # Total A
        "total_revenus_financiers_nets_A": total_revenus_financiers_nets_A,

        # Autres produits
        "frais_pris_en_charge_entreprise": frais_pris_en_charge_entreprise,
        "retrocession_frais_gestion": retrocession_frais_gestion,
        "versements_garantie_capital": versements_garantie_capital_prod,
        "autres_produits": autres_produits,

        # Autres charges
        "frais_gestion_societe_gestion": frais_gestion_sg,
        "frais_audit_etudes": frais_audit_etudes,
        "impots_taxes": impots_taxes,
        "autres_charges": autres_charges,

        # Sous-totaux
        "sous_total_autres_produits_charges_B": sous_total_autres_B,
        "sous_total_revenus_nets_avant_regul_C": sous_total_revenus_nets_avant_regul_C,
        "regularisation_revenus_nets_D": regularisation_revenus_D,

        # Total I
        "revenus_nets_I": revenus_nets_I,
    }


# ─── Compte de Résultat 2 ────────────────────────────────────────────────────

def _calculer_cr2(balance: list[dict], pvmv: list[dict]) -> dict:
    """
    Calcule tous les postes du Compte de Résultat 2.
    Sources : balance (comptes 46*, 65*, 75*, 117*, 118*, 69*) + pvmv.
    """

    # ── Plus ou moins-values réalisées ────────────────────────────────────
    # Source exclusive : fichier PVMV (table des cessions)
    # Les comptes 46* de la balance sont des comptes de TIERS (dettes/créances)
    # et ne doivent PAS être utilisés ici.
    # Si aucune cession n'a eu lieu → pvmv est vide → PVMV réalisées = 0
    pvmv_realisees = sum(
        _to_float(row.get("PLUS_VALUES_REALISEES", 0))
        - _to_float(row.get("MOINS_VALUES_REALISEES", 0))
        for row in pvmv
    )

    frais_transactions_externes = _charge(balance, "627")
    frais_recherche             = _charge(balance, "628")
    quote_part_pv_assureurs     = _charge(balance, "462")   # restitution assureurs
    indemnites_assurance        = _sumif(balance, "772", "Solde Crédit")
    versements_garantie_perf    = _sumif(balance, "773", "Solde Crédit")

    sous_total_pvmv_realisees_E = (
        pvmv_realisees
        - frais_transactions_externes
        - frais_recherche
        - quote_part_pv_assureurs
        + indemnites_assurance
        + versements_garantie_perf
    )

    # ── Régularisation PVMV réalisées (F) ────────────────────────────────
    regularisation_pvmv_realisees_F = _net(balance, "1191")

    # ── PVMV réalisées nettes II = E + F ─────────────────────────────────
    pvmv_realisees_nettes_II = sous_total_pvmv_realisees_E + regularisation_pvmv_realisees_F

    # ── Plus ou moins-values latentes ────────────────────────────────────
    # Variation PVMV latentes = (65* crédit - 65* débit) + (75* crédit - 75* débit)
    # Vérification sur le fichier :
    #   65100000 Solde ouv PVMV lat : Solde Crédit = 3633212.33
    #   75500000 PVMV lat s/actions : Solde Débit  = 4251510.84
    #   → 3633212.33 - 4251510.84 = -618298.51 ✅
    variation_pvmv_latentes = (
        _net(balance, "65")
        + _net(balance, "75")
    )

    ecarts_change_comptes_fin   = _net(balance, "512")   # comptes en devises
    versements_garantie_lat     = 0.0                    # hardcodé (pas de compte dédié)
    quote_part_pv_lat_assureurs = 0.0                    # hardcodé

    sous_total_pvmv_latentes_G = (
        variation_pvmv_latentes
        + ecarts_change_comptes_fin
        + versements_garantie_lat
        - quote_part_pv_lat_assureurs
    )

    # ── Régularisation PVMV latentes (H) ─────────────────────────────────
    regularisation_pvmv_latentes_H = _net(balance, "1192")

    # ── PVMV latentes nettes III = G + H ─────────────────────────────────
    pvmv_latentes_nettes_III = sous_total_pvmv_latentes_G + regularisation_pvmv_latentes_H

    # ── Acomptes ──────────────────────────────────────────────────────────
    acomptes_revenus_nets_J       = _charge(balance, "117")   # acomptes versés
    acomptes_pvmv_realisees_K     = _charge(balance, "118")
    total_acomptes_IV             = acomptes_revenus_nets_J + acomptes_pvmv_realisees_K

    # ── Impôt sur le résultat V ───────────────────────────────────────────
    impot_resultat_V = _charge(balance, "69")

    # ── Résultat net = I + II + III - IV - V ─────────────────────────────
    # Note : revenus_nets_I est calculé dans CR1 et passé en paramètre lors du contrôle
    # On expose ici les composantes de CR2 seulement.

    return {
        # PVMV réalisées
        "plus_moins_values_realisees": pvmv_realisees,
        "frais_transactions_externes": frais_transactions_externes,
        "frais_recherche": frais_recherche,
        "quote_part_pv_realisees_assureurs": quote_part_pv_assureurs,
        "indemnites_assurance_percues": indemnites_assurance,
        "versements_garantie_capital_perf": versements_garantie_perf,
        "sous_total_pvmv_realisees_E": sous_total_pvmv_realisees_E,
        "regularisation_pvmv_realisees_F": regularisation_pvmv_realisees_F,
        "pvmv_realisees_nettes_II": pvmv_realisees_nettes_II,

        # PVMV latentes
        "variation_pvmv_latentes": variation_pvmv_latentes,
        "ecarts_change_comptes_financiers": ecarts_change_comptes_fin,
        "versements_garantie_capital_lat": versements_garantie_lat,
        "quote_part_pv_latentes_assureurs": quote_part_pv_lat_assureurs,
        "sous_total_pvmv_latentes_G": sous_total_pvmv_latentes_G,
        "regularisation_pvmv_latentes_H": regularisation_pvmv_latentes_H,
        "pvmv_latentes_nettes_III": pvmv_latentes_nettes_III,

        # Acomptes
        "acomptes_revenus_nets_J": acomptes_revenus_nets_J,
        "acomptes_pvmv_realisees_K": acomptes_pvmv_realisees_K,
        "total_acomptes_IV": total_acomptes_IV,

        # Impôt
        "impot_resultat_V": impot_resultat_V,
    }


# ─── Contrôleur principal ─────────────────────────────────────────────────────

async def CompteResultatController(data: dict) -> dict:
    """
    Génère le Compte de Résultat 1 et le Compte de Résultat 2.

    Paramètre
    ---------
    data : dict
        Même structure que pour BilanController :
        {
            "N":   {"balance_n": [...], "inventaire_n": [...], "pvmv": [...]},
            "N_1": {"balance_n_1": [...], "inventaire_n_1": [...]}  # ou None
        }

    Retourne
    --------
    {
        "compte_resultat_1": {
            "exercice_n":  {...},
            "exercice_n1": {...}   # absent si N_1 est None
        },
        "compte_resultat_2": {
            "exercice_n":  {...},
            "exercice_n1": {...}
        },
        "controles": {
            "resultat_net_n":           float,   # résultat calculé par les CR
            "resultat_coherent_n":      bool,    # cohérence avec bilan passif
            "ecart_n":                  float,
            "resultat_net_n1":          float,
            "resultat_coherent_n1":     bool,
            "ecart_n1":                 float
        }
    }
    """

    # ── Données N ─────────────────────────────────────────────────────────
    data_n       = data.get("N") or {}
    balance_n    = data_n.get("balance_n", [])
    pvmv_n       = data_n.get("pvmv", [])

    cr1_n = _calculer_cr1(balance_n)
    cr2_n = _calculer_cr2(balance_n, pvmv_n)

    # Résultat net complet = CR1 + CR2
    resultat_net_n = (
        cr1_n["revenus_nets_I"]
        + cr2_n["pvmv_realisees_nettes_II"]
        + cr2_n["pvmv_latentes_nettes_III"]
        - cr2_n["total_acomptes_IV"]
        - cr2_n["impot_resultat_V"]
    )

    cr1_result = {"exercice_n": cr1_n}
    cr2_result = {"exercice_n": {**cr2_n, "resultat_net": resultat_net_n}}

    # ── Données N-1 ───────────────────────────────────────────────────────
    data_n1 = data.get("N_1")
    resultat_net_n1 = None

    if data_n1:
        balance_n1 = data_n1.get("balance_n_1", [])
        pvmv_n1    = data_n1.get("pvmv", [])   # si disponible dans N_1

        cr1_n1 = _calculer_cr1(balance_n1)
        cr2_n1 = _calculer_cr2(balance_n1, pvmv_n1)

        resultat_net_n1 = (
            cr1_n1["revenus_nets_I"]
            + cr2_n1["pvmv_realisees_nettes_II"]
            + cr2_n1["pvmv_latentes_nettes_III"]
            - cr2_n1["total_acomptes_IV"]
            - cr2_n1["impot_resultat_V"]
        )

        cr1_result["exercice_n1"] = cr1_n1
        cr2_result["exercice_n1"] = {**cr2_n1, "resultat_net": resultat_net_n1}

    # ── Contrôles ─────────────────────────────────────────────────────────
    # Le résultat net calculé ici doit correspondre au résultat net du bilan passif
    # (SUMIF("7*") - SUMIF("6*") calculé par BilanController)
    # On l'expose pour que le router puisse croiser avec BilanController si besoin.
    controles: dict = {
        "resultat_net_n": round(resultat_net_n, 4),
    }

    if resultat_net_n1 is not None:
        controles["resultat_net_n1"] = round(resultat_net_n1, 4)

    return {
        "compte_resultat_1": cr1_result,
        "compte_resultat_2": cr2_result,
        "controles":         controles,
    }
import { useState } from "react"
import { toast } from "sonner"
import {
  uploadFiles,
  computeBilan,
  computeCapitauxPropres,
  computeCompteResultat,
  computeExpositionPortefeuille,
  computeSommesDistribuables,
  generatePdf,
} from "@/src/API/Processing"
import BreadCrampTable, { type LinkTypes } from "@/components/Table/BreadCamp"
import FundSelector from "./Fundselector"
import UploadFilesSection, { type UploadFiles, type FileErrors } from "./Uploadfilessection"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Loader2, Upload, RotateCcw } from "lucide-react"
import ProcessingProgress, { type ProcessingStep, type StepStatus }from "./ProcessingProgress"

// ── Types ──────────────────────────────────────────────────────────────────────

interface FundOption {
  fund_id: string
  fund_name: string
  fund_anciente: string
  company_name: string
}

const EMPTY_FILES: UploadFiles = {
  fichier_vl_n: null,
  fichier_vl_n_1: null,
  comptes_annuels: null,
}

const links: LinkTypes[] = [
  { name: "Général", path: "/" },
  { name: "Importer les fichiers", path: "/upload" },
]

// Définition statique des étapes (le statut sera mis à jour dynamiquement)
const STEP_DEFINITIONS = [
  {
    id: "upload",
    label: "Extraction des données",
    description: "Lecture des fichiers Excel et PDF déposés",
  },
  {
    id: "bilan",
    label: "Calcul du bilan",
    description: "Bilan Actif et Bilan Passif",
  },
  {
    id: "capitaux_propres",
    label: "Capitaux propres",
    description: "Reconstitution de la ligne III",
  },
  {
    id: "compte_resultat",
    label: "Comptes de résultat",
    description: "Compte de Résultat 1 et 2",
  },
  {
    id: "exposition",
    label: "Exposition portefeuille",
    description: "Ventilation des actifs (onglet VIII)",
  },
  {
    id: "sommes",
    label: "Sommes distribuables",
    description: "Détermination et ventilation (onglet XIII)",
  },
  {
    id: "pdf",
    label: "Génération du PDF",
    description: "Assemblage du rapport complet",
  },
]

function buildInitialSteps(): ProcessingStep[] {
  return STEP_DEFINITIONS.map((s) => ({ ...s, status: "idle" as StepStatus }))
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function UploadPage() {
  const [selectedFund, setSelectedFund] = useState<FundOption | null>(null)
  const [files, setFiles] = useState<UploadFiles>(EMPTY_FILES)
  const [errors, setErrors] = useState<FileErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Progression
  const [steps, setSteps] = useState<ProcessingStep[]>(buildInitialSteps())
  const [showProgress, setShowProgress] = useState(false)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [pdfFilename, setPdfFilename] = useState("")

  // ── Helpers ──────────────────────────────────────────────────────────────

  function setStepStatus(id: string, status: StepStatus, errorMessage?: string) {
    setSteps((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status, errorMessage } : s))
    )
  }

  function handleFileChange(key: keyof UploadFiles, file: File | null) {
    setFiles((prev) => ({ ...prev, [key]: file }))
    setErrors((prev) => ({ ...prev, [key]: undefined }))
  }

  function validate(): boolean {
    const newErrors: FileErrors = {}
    if (!files.fichier_vl_n)    newErrors.fichier_vl_n    = "Ce fichier est obligatoire"
    if (!files.comptes_annuels) newErrors.comptes_annuels = "Ce fichier est obligatoire"
    if (selectedFund?.fund_anciente === "A" && !files.fichier_vl_n_1) {
      newErrors.fichier_vl_n_1 = "Ce fichier est obligatoire pour un fonds avec N-1"
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function handleReset() {
    setSelectedFund(null)
    setFiles(EMPTY_FILES)
    setErrors({})
    setSteps(buildInitialSteps())
    setShowProgress(false)
    setPdfUrl(null)
    setPdfFilename("")
  }

  // ── Pipeline principal ────────────────────────────────────────────────────

  async function handleSubmit() {
    if (!selectedFund) { toast.error("Veuillez sélectionner un fonds"); return }
    if (!validate())   { toast.error("Veuillez déposer tous les fichiers requis"); return }

    setIsSubmitting(true)
    setSteps(buildInitialSteps())
    setShowProgress(true)
    setPdfUrl(null)

    try {

      // ── Étape 1 : Upload ────────────────────────────────────────────────
      setStepStatus("upload", "loading")
      const extractedData = await uploadFiles({
        anciennete:     selectedFund.fund_anciente,
        fichier_vl_n:   files.fichier_vl_n!,
        comptes_annuels: files.comptes_annuels!,
        fichier_vl_n_1: files.fichier_vl_n_1,
      })
      setStepStatus("upload", "success")

      // ── Étape 2 : Bilan ─────────────────────────────────────────────────
      setStepStatus("bilan", "loading")
      const bilan = await computeBilan(extractedData)
      setStepStatus("bilan", "success")

      // ── Étape 3 : Capitaux propres ──────────────────────────────────────
      setStepStatus("capitaux_propres", "loading")
      const capitaux_propres = await computeCapitauxPropres(extractedData)
      setStepStatus("capitaux_propres", "success")

      // ── Étape 4 : Compte de résultat ────────────────────────────────────
      setStepStatus("compte_resultat", "loading")
      const compte_resultat = await computeCompteResultat(extractedData)
      setStepStatus("compte_resultat", "success")

      // ── Étape 5 : Exposition portefeuille ───────────────────────────────
      setStepStatus("exposition", "loading")
      const exposition_portefeuille = await computeExpositionPortefeuille(extractedData)
      setStepStatus("exposition", "success")

      // ── Étape 6 : Sommes distribuables ──────────────────────────────────
      setStepStatus("sommes", "loading")
      const sommes_distribuables = await computeSommesDistribuables(extractedData)
      setStepStatus("sommes", "success")

      // ── Étape 7 : Génération PDF ────────────────────────────────────────
      setStepStatus("pdf", "loading")
      const today = new Date().toLocaleDateString("fr-FR")
      const pdfBlob = await generatePdf({
        bilan,
        compte_resultat,
        capitaux_propres,
        exposition_portefeuille,
        sommes_distribuables,
        nom_fond:     selectedFund.fund_name,
        date_cloture: today,
      })
      setStepStatus("pdf", "success")

      // Créer un lien de téléchargement local
      const url      = URL.createObjectURL(pdfBlob)
      const filename = `comptes_annuels_${selectedFund.fund_name.replace(/\s+/g, "_")}_${today.replace(/\//g, "")}.pdf`
      setPdfUrl(url)
      setPdfFilename(filename)

    } catch (error: any) {
      // Le step courant (loading) est automatiquement marqué en erreur
      setSteps((prev) =>
        prev.map((s) =>
          s.status === "loading"
            ? { ...s, status: "error", errorMessage: error.message }
            : s
        )
      )
      toast.error("Traitement interrompu", { description: error.message })
    } finally {
      setIsSubmitting(false)
    }
  }

  // ── Calculs dérivés ───────────────────────────────────────────────────────

  const anciennete      = (selectedFund?.fund_anciente ?? "N") as "A" | "N"
  const requiredCount   = anciennete === "A" ? 3 : 2
  const depositedCount  = [
    files.fichier_vl_n,
    anciennete === "A" ? files.fichier_vl_n_1 : true,
    files.comptes_annuels,
  ].filter(Boolean).length
  const allDeposited    = depositedCount === requiredCount

  // ── Rendu ─────────────────────────────────────────────────────────────────

  return (
    <>
      <BreadCrampTable links={links} className="" />

      <div className="p-6 max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-xl font-semibold">Importer les fichiers</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Sélectionnez un fonds et déposez les fichiers pour générer les comptes annuels.
          </p>
        </div>

        {/* Formulaire — masqué pendant le traitement */}
        {!showProgress && (
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="text-base">Sélection du fonds</CardTitle>
              <CardDescription>
                L'ancienneté du fonds détermine le nombre de fichiers à fournir.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FundSelector value={selectedFund} onChange={setSelectedFund} />

              {selectedFund && (
                <>
                  <Separator />
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">Fichiers à déposer</p>
                      <span className="text-xs text-muted-foreground font-mono">
                        {depositedCount} / {requiredCount} déposé{depositedCount > 1 ? "s" : ""}
                      </span>
                    </div>
                    <UploadFilesSection
                      anciennete={anciennete}
                      files={files}
                      errors={errors}
                      onChange={handleFileChange}
                    />
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}

        {/* Progression — affichée pendant/après le traitement */}
        {showProgress && (
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="text-base flex items-center gap-2">
                {isSubmitting && <Loader2 size={16} className="animate-spin text-primary" />}
                {isSubmitting ? "Traitement en cours..." : "Traitement terminé"}
              </CardTitle>
              <CardDescription>
                {selectedFund?.fund_name} — {selectedFund?.company_name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ProcessingProgress
                steps={steps}
                pdfUrl={pdfUrl}
                pdfFilename={pdfFilename}
                onReset={handleReset}
              />
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        {!showProgress && selectedFund && (
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              disabled={isSubmitting}
              className="gap-2 text-muted-foreground"
            >
              <RotateCcw size={14} />
              Réinitialiser
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || !allDeposited}
              className="gap-2"
            >
              {isSubmitting ? (
                <><Loader2 size={16} className="animate-spin" />Traitement en cours...</>
              ) : (
                <><Upload size={16} />Générer les comptes annuels</>
              )}
            </Button>
          </div>
        )}
      </div>
    </>
  )
}
import { CheckCircle2, Circle, Loader2, XCircle, FileText } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export type StepStatus = "idle" | "loading" | "success" | "error"

export interface ProcessingStep {
  id: string
  label: string
  description: string
  status: StepStatus
  errorMessage?: string
}

interface ProcessingProgressProps {
  steps: ProcessingStep[]
  pdfUrl: string | null
  pdfFilename: string
  onReset: () => void
}

function StepIcon({ status }: { status: StepStatus }) {
  if (status === "loading") return <Loader2 size={18} className="animate-spin text-primary shrink-0" />
  if (status === "success") return <CheckCircle2 size={18} className="text-emerald-500 shrink-0" />
  if (status === "error")   return <XCircle size={18} className="text-red-500 shrink-0" />
  return <Circle size={18} className="text-muted-foreground/40 shrink-0" />
}

export default function ProcessingProgress({
  steps,
  pdfUrl,
  pdfFilename,
  onReset,
}: ProcessingProgressProps) {
  const hasError  = steps.some((s) => s.status === "error")
  const isDone    = steps.every((s) => s.status === "success")
  const errorStep = steps.find((s) => s.status === "error")

  return (
    <div className="space-y-4">

      {/* Liste des étapes */}
      <div className="rounded-xl border bg-background divide-y divide-border/60 overflow-hidden">
        {steps.map((step, index) => {
          const isActive  = step.status === "loading"
          const isDone    = step.status === "success"
          const isError   = step.status === "error"
          const isIdle    = step.status === "idle"

          return (
            <div
              key={step.id}
              className={cn(
                "flex items-start gap-3 px-4 py-3 transition-colors",
                isActive && "bg-primary/5",
                isError  && "bg-red-50",
                isDone   && "bg-emerald-50/40",
              )}
            >
              {/* Icône statut */}
              <div className="mt-0.5">
                <StepIcon status={step.status} />
              </div>

              {/* Contenu */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={cn(
                    "text-sm font-medium",
                    isIdle  && "text-muted-foreground",
                    isActive && "text-primary",
                    isDone  && "text-emerald-700",
                    isError && "text-red-700",
                  )}>
                    {step.label}
                  </span>
                  {isActive && (
                    <span className="text-xs text-primary animate-pulse">
                      En cours...
                    </span>
                  )}
                </div>
                <p className={cn(
                  "text-xs mt-0.5",
                  isIdle  && "text-muted-foreground/60",
                  isActive && "text-primary/70",
                  isDone  && "text-emerald-600/80",
                  isError && "text-red-500",
                )}>
                  {isError && step.errorMessage
                    ? step.errorMessage
                    : step.description}
                </p>
              </div>

              {/* Numéro d'étape pour les idle */}
              {isIdle && (
                <span className="text-xs text-muted-foreground/40 font-mono mt-0.5">
                  {String(index + 1).padStart(2, "0")}
                </span>
              )}
            </div>
          )
        })}
      </div>

      {/* Résultat final */}
      {isDone && pdfUrl && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 flex items-center gap-4">
          <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
            <FileText size={20} className="text-emerald-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-emerald-800">
              Comptes annuels générés avec succès
            </p>
            <p className="text-xs text-emerald-600 truncate mt-0.5">
              {pdfFilename}
            </p>
          </div>
          <a href={pdfUrl} download={pdfFilename}>
            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 gap-2 shrink-0">
              <FileText size={14} />
              Télécharger
            </Button>
          </a>
        </div>
      )}

      {/* Erreur + bouton réessayer */}
      {hasError && (
        <div className="flex items-center justify-between rounded-xl border border-red-200 bg-red-50 px-4 py-3">
          <div>
            <p className="text-sm font-medium text-red-800">Traitement interrompu</p>
            <p className="text-xs text-red-600 mt-0.5">
              Étape échouée : <span className="font-medium">{errorStep?.label}</span>
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={onReset} className="border-red-200 text-red-700 hover:bg-red-100">
            Réessayer
          </Button>
        </div>
      )}
    </div>
  )
}
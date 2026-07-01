import { FileSpreadsheet, FileText } from "lucide-react"
import FileDropZone from "./Filedropzone"

export interface UploadFiles {
  fichier_vl_n: File | null
  fichier_vl_n_1: File | null
  comptes_annuels: File | null
}

export type FileErrors = Partial<Record<keyof UploadFiles, string>>

interface UploadFilesSectionProps {
  anciennete: "A" | "N"
  files: UploadFiles
  errors: FileErrors
  onChange: (key: keyof UploadFiles, file: File | null) => void
}

export default function UploadFilesSection({
  anciennete,
  files,
  errors,
  onChange,
}: UploadFilesSectionProps) {
  return (
    <div className="grid gap-4">

      {/* Fichier VL N — toujours requis */}
      <FileDropZone
        label="Fichier VL — Exercice N"
        description="Fichier Excel contenant les valeurs liquidatives de l'exercice en cours"
        accept=".xlsx,.xls"
        required
        file={files.fichier_vl_n}
        onChange={(f) => onChange("fichier_vl_n", f)}
        error={errors.fichier_vl_n}
      />

      {/* Fichier VL N-1 — uniquement si anciennete === "A" */}
      {anciennete === "A" && (
        <FileDropZone
          label="Fichier VL — Exercice N-1"
          description="Fichier Excel contenant les valeurs liquidatives de l'exercice précédent"
          accept=".xlsx,.xls"
          required
          file={files.fichier_vl_n_1}
          onChange={(f) => onChange("fichier_vl_n_1", f)}
          error={errors.fichier_vl_n_1}
        />
      )}

      {/* PDF Comptes annuels — toujours requis */}
      <FileDropZone
        label="Comptes annuels (PDF)"
        description="PDF des comptes annuels au format Coala"
        accept=".pdf"
        required
        file={files.comptes_annuels}
        onChange={(f) => onChange("comptes_annuels", f)}
        error={errors.comptes_annuels}
      />
    </div>
  )
}
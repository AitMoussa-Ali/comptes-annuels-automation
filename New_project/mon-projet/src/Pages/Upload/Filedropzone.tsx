import { useRef, useState } from "react"
import { Upload, X, FileText, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface FileDropZoneProps {
  label: string
  accept?: string          // ex: ".xlsx,.xls" ou ".pdf"
  file: File | null
  onChange: (file: File | null) => void
  required?: boolean
  description?: string     // ex: "Fichier Excel VL exercice N"
  error?: string
}

export default function FileDropZone({
  label,
  accept,
  file,
  onChange,
  required = false,
  description,
  error,
}: FileDropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) onChange(dropped)
  }

  function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null
    onChange(selected)
    // reset input pour permettre de re-sélectionner le même fichier
    e.target.value = ""
  }

  function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} o`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
  }

  return (
    <div className="grid gap-1.5">
      <p className="text-sm font-medium">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </p>
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}

      {/* Zone de dépôt */}
      {!file ? (
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={cn(
            "border-2 border-dashed rounded-lg p-6 flex flex-col items-center gap-2",
            "cursor-pointer transition-colors select-none",
            isDragging
              ? "border-primary bg-primary/5"
              : error
              ? "border-red-400 bg-red-50 hover:border-red-500"
              : "border-border hover:border-primary/50 hover:bg-muted/30"
          )}
        >
          <div className={cn(
            "h-10 w-10 rounded-full flex items-center justify-center",
            error ? "bg-red-100" : "bg-muted"
          )}>
            {error
              ? <AlertCircle size={18} className="text-red-500" />
              : <Upload size={18} className="text-muted-foreground" />
            }
          </div>
          <div className="text-center">
            <p className="text-sm font-medium">
              {isDragging ? "Déposez le fichier ici" : "Cliquez ou déposez un fichier"}
            </p>
            {accept && (
              <p className="text-xs text-muted-foreground mt-0.5">
                Formats acceptés : {accept}
              </p>
            )}
          </div>
        </div>
      ) : (
        /* Fichier sélectionné */
        <div className="flex items-center gap-3 border rounded-lg px-3 py-2.5 bg-muted/20">
          <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center shrink-0">
            <FileText size={16} className="text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{file.name}</p>
            <p className="text-xs text-muted-foreground">{formatSize(file.size)}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 shrink-0 text-muted-foreground hover:text-red-500"
            onClick={(e) => { e.stopPropagation(); onChange(null) }}
          >
            <X size={14} />
          </Button>
        </div>
      )}

      {error && <p className="text-xs text-red-500">{error}</p>}

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={handleFileInput}
      />
    </div>
  )
}
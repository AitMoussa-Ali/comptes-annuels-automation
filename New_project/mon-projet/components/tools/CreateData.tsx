import { useState, useEffect } from "react"
import { format } from "date-fns"
import { fr } from "date-fns/locale"
import { CalendarIcon } from "lucide-react"
import {
  Dialog, DialogContent, DialogHeader,
  DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Calendar } from "@/components/ui/calendar"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import {
  Popover, PopoverContent, PopoverTrigger,
} from "@/components/ui/popover"
import {
  Select, SelectContent, SelectItem,
  SelectTrigger, SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

export interface FieldDef<T> {
  key: keyof T
  label: string
  type?: "text" | "number" | "date" | "datepicker" | "select" | "email" | "checkbox" | "switch"
  placeholder?: string
  required?: boolean
  options?: { label: string; value: string }[]
  // Pour les selects dynamiques : options chargées depuis l'extérieur
  dynamicOptions?: { label: string; value: string }[]
}

interface EditDialogProps<T> {
  open: boolean
  onOpenChange: (open: boolean) => void
  fields: FieldDef<T>[]
  initialData?: Partial<T> | null
  onSave: (data: T) => void
  title?: string
  description?: string
  isLoading?: boolean
}

export default function EditDialog<T extends Record<string, any>>({
  open,
  onOpenChange,
  fields,
  initialData,
  onSave,
  title,
  description,
  isLoading = false,
}: EditDialogProps<T>) {
  const [formData, setFormData] = useState<Partial<T>>({})
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})

  useEffect(() => {
    if (open) {
      setFormData(initialData ?? {})
      setErrors({})
    }
  }, [open, initialData])

  const isEditMode = Boolean(initialData)

  function handleChange(key: keyof T, value: any) {
    setFormData((prev) => ({ ...prev, [key]: value }))
    setErrors((prev) => ({ ...prev, [key]: undefined }))
  }

  function validate(): boolean {
    const newErrors: Partial<Record<keyof T, string>> = {}
    fields.forEach((field) => {
      const val = formData[field.key]
      // checkbox/switch : false est une valeur valide, ne pas bloquer
      if (field.required && field.type !== "checkbox" && field.type !== "switch" && !val) {
        newErrors[field.key] = "Ce champ est obligatoire"
      }
    })
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function handleSubmit() {
    if (!validate()) return
    onSave(formData as T)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
  <DialogContent
    className="sm:max-w-120"
    onInteractOutside={(e) => {
      // Ne pas fermer si le clic vient d'un portail Radix (Popover, Select, Calendar...)
      const target = e.target as HTMLElement
      if (target.closest("[data-radix-popper-content-wrapper]")) {
        e.preventDefault()
      }
    }}
  >
        <DialogHeader>
          <DialogTitle>
            {title ?? (isEditMode ? "Modifier" : "Ajouter")}
          </DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>

        <div className="grid gap-4 py-2">
          {fields.map((field) => {
            const value = formData[field.key]
            const error = errors[field.key]
            const options = field.dynamicOptions ?? field.options ?? []

            return (
              <div key={String(field.key)} className="grid gap-2">

                {/* CHECKBOX — rendu inline avec le label */}
                {field.type === "checkbox" ? (
                  <div className="flex items-center gap-3 rounded-md border px-3 py-2.5">
                    <Checkbox
                      id={String(field.key)}
                      checked={Boolean(value)}
                      onCheckedChange={(checked) => handleChange(field.key, Boolean(checked))}
                    />
                    <Label htmlFor={String(field.key)} className="cursor-pointer font-normal">
                      {field.label}
                    </Label>
                  </div>
                ) : field.type === "switch" ? (
                  /* SWITCH — même principe */
                  <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
                    <Label htmlFor={String(field.key)} className="cursor-pointer font-normal">
                      {field.label}
                    </Label>
                    <Switch
                      id={String(field.key)}
                      checked={Boolean(value)}
                      onCheckedChange={(checked) => handleChange(field.key, Boolean(checked))}
                    />
                  </div>
                ) : (
                  <>
                    <Label htmlFor={String(field.key)}>
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </Label>

                    {/* DATE PICKER */}
                    {field.type === "datepicker" ? (
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            id={String(field.key)}
                            variant="outline"
                            className={cn(
                              "justify-start text-left font-normal",
                              !value && "text-muted-foreground",
                              error && "border-red-500"
                            )}
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {value
                              ? format(new Date(value), "dd/MM/yyyy", { locale: fr })
                              : field.placeholder ?? "Sélectionner une date"}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                          <Calendar
                            mode="single"
                            selected={value ? new Date(value) : undefined}
                            onSelect={(date) =>
                              handleChange(field.key, date ? format(date, "yyyy-MM-dd") : "")
                            }
                            locale={fr}
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>

                    ) : field.type === "select" ? (
                      /* SELECT — options statiques ou dynamiques */
                      <Select
                      
                        value={value ?? ""}
                        onValueChange={(val) => handleChange(field.key, val)}
                        
                      >
                        <SelectTrigger
                          id={String(field.key)}
                          className={cn(error && "border-red-500")+" w-full"}
                        >
                          <SelectValue placeholder={field.placeholder ?? "Sélectionner..."} />
                        </SelectTrigger>
                        <SelectContent>
                          {options.map((opt) => (
                            <SelectItem key={opt.value} value={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                    ) : (
                      /* INPUT texte / number / email / date */
                      <Input
                        id={String(field.key)}
                        type={field.type ?? "text"}
                        placeholder={field.placeholder}
                        value={value ?? ""}
                        className={cn(error && "border-red-500")}
                        onChange={(e) => handleChange(field.key, e.target.value)}
                      />
                    )}

                    {error && <p className="text-xs text-red-500">{error}</p>}
                  </>
                )}
              </div>
            )
          })}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
            Annuler
          </Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? "Enregistrement..." : isEditMode ? "Enregistrer" : "Ajouter"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
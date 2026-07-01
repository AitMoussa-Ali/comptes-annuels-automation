import { useEffect, useState } from "react"
import { getFunds } from "@/src/API/Funds"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Loader2 } from "lucide-react"

interface FundOption {
  fund_id: string
  fund_name: string
  fund_anciente: string   // "A" | "N"
  company_name: string
}

interface FundSelectorProps {
  value: FundOption | null
  onChange: (fund: FundOption | null) => void
}

export default function FundSelector({ value, onChange }: FundSelectorProps) {
  const [funds, setFunds] = useState<FundOption[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getFunds(1, 100)
      .then((data) => setFunds(data.items))
      .catch(() => {})
      .finally(() => setIsLoading(false))
  }, [])

  function handleChange(fundId: string) {
    const selected = funds.find((f) => f.fund_id === fundId) ?? null
    onChange(selected)
  }

  return (
    <div className="grid gap-2">
      <Label htmlFor="fund-select" className="text-sm font-medium">
        Fonds concerné <span className="text-red-500">*</span>
      </Label>

      <Select value={value?.fund_id ?? ""} onValueChange={handleChange} disabled={isLoading}>
        <SelectTrigger id="fund-select" className="w-full">
          {isLoading ? (
            <span className="flex items-center gap-2 text-muted-foreground">
              <Loader2 size={14} className="animate-spin" />
              Chargement...
            </span>
          ) : (
            <SelectValue placeholder="Sélectionner un fonds..." />
          )}
        </SelectTrigger>
        <SelectContent>
          {funds.map((fund) => (
            <SelectItem key={fund.fund_id} value={fund.fund_id}>
              <div className="flex items-center justify-between gap-3 w-full">
                <span>{fund.fund_name}</span>
                <span className="text-xs text-muted-foreground">{fund.company_name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Infos du fonds sélectionné */}
      {value && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
          <span>{value.company_name}</span>
          <span>·</span>
          <Badge variant={value.fund_anciente === "A" ? "secondary" : "outline"} className="text-xs">
            {value.fund_anciente === "A" ? "Avec N-1 — 3 fichiers requis" : "1er exercice — 2 fichiers requis"}
          </Badge>
        </div>
      )}
    </div>
  )
}
import { useEffect, useState, useMemo } from "react"
import { toast } from "sonner"
import { getFunds, CreateFund, UpdateFund, DeleteFund } from "@/src/API/Funds"
import { getCompanies } from "@/src/API/Companies"
import type { ColumnDef, PaginationState } from "@/components/Table/DataTable"
import DataTable from "@/components/Table/DataTable"
import BreadCrampTable, { type LinkTypes } from "@/components/Table/BreadCamp"
import EditDialog, { type FieldDef } from "@/components/tools/CreateData"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search } from "lucide-react"
import ConfirmDialog from "@/components/tools/ConfirmDialog"

// ── Types ──────────────────────────────────────────────────────────────────────

// Ce que l'API retourne dans items[]
interface FundRow {
  fund_id: string
  fund_name: string
  fund_creation_date: string
  fund_anciente: string   // "A" | "N"  (nom exact du champ FundResponse)
  fund_bilingue: boolean
  company_name: string
  company_id: string
}

// Ce que le formulaire de création envoie
interface FundCreate {
  company_id: string
  fund_name: string
  fund_creation_date: string
  anciennete: string   // "A" | "N"
  bilingue: boolean
}

// Option pour le select Société
interface CompanyOption {
  label: string
  value: string
}

// ── Config statique ────────────────────────────────────────────────────────────

const columns: ColumnDef<FundRow>[] = [
  { key: "company_name", label: "Société de gestion" },
  { key: "fund_name", label: "Nom du fonds" },
  {
    key: "fund_anciente",
    label: "Ancienneté",
    render: (row) => (
      <Badge variant={row.fund_anciente === "A" ? "secondary" : "outline"}>
        {row.fund_anciente === "A" ? "Avec N-1" : "1er exercice"}
      </Badge>
    ),
  },
  {
    key: "fund_bilingue",
    label: "Bilingue",
    render: (row) => (
      <Badge variant={row.fund_bilingue ? "default" : "outline"}>
        {row.fund_bilingue ? "Oui" : "Non"}
      </Badge>
    ),
  },
  { key: "fund_creation_date", label: "Date de création" },
]

const links: LinkTypes[] = [
  { name: "Général", path: "/" },
  { name: "Fonds", path: "/Fonds" },
]

const ancienneteOptions = [
  { label: "Avec N-1 (fonds existant)", value: "A" },
  { label: "1er exercice (nouveau fonds)", value: "N" },
]

// ── Page ───────────────────────────────────────────────────────────────────────

export default function Funds() {
  const [funds, setFunds] = useState<FundRow[]>([])
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    pageSize: 10,
    totalItems: 0,
    totalPages: 1,
  })
  const [companyOptions, setCompanyOptions] = useState<CompanyOption[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingFund, setEditingFund] = useState<FundRow | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingData, setIsLoadingData] = useState(true)
  const [deletingFund, setDeletingFund] = useState<FundRow | null>(null)

  // Chargement des sociétés pour le select (une seule fois)
  useEffect(() => {
    getCompanies(1, 100)
      .then((data) => {
        setCompanyOptions(
          data.items.map((c: any) => ({
            label: c.company_name,
            value: c.company_id,
          }))
        )
      })
      .catch(() => toast.error("Impossible de charger les sociétés"))
  }, [])

  // Champs du formulaire — dynamicOptions mis à jour avec les sociétés chargées
  const fields: FieldDef<FundCreate>[] = useMemo(() => [
    {
      key: "company_id",
      label: "Société de gestion",
      type: "select",
      placeholder: "Sélectionner une société...",
      required: true,
      dynamicOptions: companyOptions,
    },
    {
      key: "fund_name",
      label: "Nom du fonds",
      type: "text",
      placeholder: "Ex: Fonds de dotation II",
      required: true,
    },
    {
      key: "anciennete",
      label: "Ancienneté",
      type: "select",
      required: true,
      options: ancienneteOptions,
    },
    {
      key: "bilingue",
      label: "Rapport bilingue (FR / EN)",
      type: "switch",
    },
    {
      key: "fund_creation_date",
      label: "Date de création",
      type: "datepicker",
      required: true,
    },
  ], [companyOptions])

  // ── Fetch ──────────────────────────────────────────────────────────────────

  async function fetchData(page: number, pageSize: number, search = "") {
    setIsLoadingData(true)
    try {
      const data = await getFunds(page, pageSize, search)
      setFunds(data.items)
      setPagination({
        page: data.page,
        pageSize: data.page_size,
        totalItems: data.total_items,
        totalPages: data.total_pages,
      })
    } catch (error: any) {
      toast.error("Impossible de charger les fonds", { description: error.message })
    } finally {
      setIsLoadingData(false)
    }
  }

  // Chargement initial
  useEffect(() => {
    fetchData(1, pagination.pageSize)
  }, [])

  // Debounce sur la recherche
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchData(1, pagination.pageSize, searchTerm)
    }, 400)
    return () => clearTimeout(timer)
  }, [searchTerm])

  // ── Handlers ───────────────────────────────────────────────────────────────

  function handlePageChange(newPage: number) {
    fetchData(newPage, pagination.pageSize, searchTerm)
  }

  function handlePageSizeChange(newSize: number) {
    fetchData(1, newSize, searchTerm)
  }

  function handleOpenAdd() {
    setEditingFund(null)
    setDialogOpen(true)
  }

  function handleOpenEdit(fund: FundRow) {
    setEditingFund(fund)
    setDialogOpen(true)
  }

  async function handleSave(data: FundCreate) {
    setIsLoading(true)
    try {
      if (editingFund) {
        const { company_id, ...fundPayload } = data
        await UpdateFund(editingFund.fund_id, company_id, fundPayload)  // ← company_id en 2e arg
        toast.success("Fonds modifié avec succès")
      } else {
        const { company_id, ...fundPayload } = data
        await CreateFund(company_id, fundPayload)
        toast.success("Fonds ajouté avec succès")
      }
      setDialogOpen(false)
      await fetchData(pagination.page, pagination.pageSize, searchTerm)
    } catch (error: any) {
      toast.error("Échec de l'opération", { description: error.message })
    } finally {
      setIsLoading(false)
    }
    }

  function handleDelete(fund: FundRow) {
    setDeletingFund(fund)
  }

  // 3. La vraie suppression, appelée seulement après confirmation
async function handleConfirmDelete() {
  if (!deletingFund) return
  try {
    await DeleteFund(deletingFund.fund_id)
    toast.success(`"${deletingFund.fund_name}" supprimé`)
    const isLastOnPage = funds.length === 1 && pagination.page > 1
    await fetchData(
      isLastOnPage ? pagination.page - 1 : pagination.page,
      pagination.pageSize,
      searchTerm
    )
  } catch (error: any) {
    toast.error("Impossible de supprimer", { description: error.message })
  } finally {
    setDeletingFund(null)
  }
}

  // Données initiales du formulaire en mode édition
  // On mappe FundRow → FundCreate pour pré-remplir le formulaire
    const editingFundAsCreate: Partial<FundCreate> | null = editingFund
        ? {
      fund_name: editingFund.fund_name,
      fund_creation_date: editingFund.fund_creation_date,
      anciennete: editingFund.fund_anciente,
      bilingue: editingFund.fund_bilingue,
      company_id: editingFund.company_id,  // ← ajouter (plus de commentaire "non pré-rempli")
    }
    : null

  // ── Rendu ──────────────────────────────────────────────────────────────────

  return (
    <>
      <BreadCrampTable links={links} className="" />

      <div className="flex items-center justify-between p-4">
        <div className="flex items-center p-1 rounded-xl bg-white border w-1/2">
          <Search size={20} color="gray" />
          <Input
            className="border-0 focus-visible:ring-0 focus-visible:ring-offset-0 focus:outline-none"
            placeholder="Chercher un fonds ou une société..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Button onClick={handleOpenAdd}>Ajouter un fonds</Button>
        </div>
      </div>

      <div className="px-4">
        <DataTable
          columns={columns}
          data={funds}
          getRowId={(row) => row.fund_id}
          onEdit={handleOpenEdit}
          onDelete={handleDelete}
          pagination={pagination}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          isLoading={isLoadingData}
        />
      </div>

      <EditDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        fields={fields}
        initialData={editingFundAsCreate}
        onSave={handleSave}
        isLoading={isLoading}
        title={editingFund ? "Modifier le fonds" : "Ajouter un fonds"}
      />

      <ConfirmDialog
        open={Boolean(deletingFund)}
        onOpenChange={(open) => { if (!open) setDeletingFund(null) }}
        onConfirm={handleConfirmDelete}
        title="Supprimer le fond"
        description={`Voulez-vous vraiment supprimer "${deletingFund?.fund_name}" ? Cette action est irréversible.`}
    />
    </>
  )
}
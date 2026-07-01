import { useEffect, useState } from "react"
import { toast } from "sonner"
import { getCompanies, CreateCompany, UpdateCompany, DeleteCompany } from "@/src/API/Companies"
import type { ColumnDef, PaginationState } from "@/components/Table/DataTable"
import DataTable from "@/components/Table/DataTable"
import BreadCrampTable, { type LinkTypes } from "@/components/Table/BreadCamp"
import EditDialog, { type FieldDef } from "@/components/tools/CreateData"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"
import ConfirmDialog from "@/components/tools/ConfirmDialog"

interface Companies {
  company_id: string
  company_name: string
  company_creation_date: string
}

interface Company {
  company_name: string
  company_creation_date: string
}

const columns: ColumnDef<Companies>[] = [
  { key: "company_name", label: "Nom de société" },
  { key: "company_creation_date", label: "Date de création" },
]

const links: LinkTypes[] = [
  { name: "Général", path: "/" },
  { name: "Sociétés de gestion", path: "/Societes" },
]

const fields: FieldDef<Company>[] = [
  {
    key: "company_name",
    label: "Nom de la société de gestion",
    placeholder: "Ex: Naxicap Partners",
    required: true,
  },
  {
    key: "company_creation_date",
    label: "Date de création",
    type: "datepicker",
    required: true,
  },
]

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Companies[]>([])
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    pageSize: 10,
    totalItems: 0,
    totalPages: 1,
  })

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingCompany, setEditingCompany] = useState<Companies | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingData, setIsLoadingData] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [deletingCompany, setdeletingCompany] = useState<Companies | null>(null)
  async function fetchData(page: number, pageSize: number, searchTerm: string = "") {
    setIsLoadingData(true)
    try {
      const data = await getCompanies(page, pageSize, searchTerm)
      setCompanies(data.items)
      setPagination({
        page: data.page,
        pageSize: data.page_size,
        totalItems: data.total_items,
        totalPages: data.total_pages,
      })
      setIsLoadingData(false)

    } catch (error: any) {
      setIsLoadingData(false)
      toast.error("Impossible de charger les sociétés", { description: error.message })
    }
  }

    useEffect(() => {
        // Debounce : attend 400ms après la dernière frappe avant d'envoyer la requête
        const timer = setTimeout(() => {
        fetchData(1, pagination.pageSize, searchTerm)
        // Retour à la page 1 à chaque nouvelle recherche
    }, 400)
        return () => clearTimeout(timer) // annule si l'utilisateur retape avant 400ms
    }, [searchTerm])

    useEffect(() => {
        fetchData(pagination.page, pagination.pageSize, "")
    }, [])

    function handlePageChange(newPage: number) {
        fetchData(newPage, pagination.pageSize, searchTerm) // ← ajout searchTerm
    }

    function handlePageSizeChange(newSize: number) {
        fetchData(1, newSize, searchTerm) // ← ajout searchTerm
    }

  function handleOpenAdd() {
    setEditingCompany(null)
    setDialogOpen(true)
  }

  function handleOpenEdit(company: Companies) {
    setEditingCompany(company)
    setDialogOpen(true)
  }

  async function handleSave(data: Company) {
    setIsLoading(true)
    try {
      if (editingCompany) {
        await UpdateCompany(editingCompany.company_id, data)
        toast.success("Société modifiée avec succès")
      } else {
        await CreateCompany(data)
        toast.success("Société ajoutée avec succès")
      }
      setDialogOpen(false)
      await fetchData(pagination.page, pagination.pageSize)
    } catch (error: any) {
      toast.error("Échec de l'opération", { description: error.message })
    } finally {
      setIsLoading(false)
    }
  }

  function handleDelete(company: Companies) {
    setdeletingCompany(company)
  }

  async function handleConfirmDelete() {
    if (!deletingCompany) return
    try {
      await DeleteCompany(deletingCompany?.company_id)
      toast.success(`"${deletingCompany?.company_name}" supprimée`)
      // Si on supprime le dernier élément d'une page, reculer d'une page
      const isLastOnPage = companies.length === 1 && pagination.page > 1
      await fetchData(isLastOnPage ? pagination.page - 1 : pagination.page, pagination.pageSize)
    } catch (error: any) {
      toast.error("Impossible de supprimer", { description: error.message })
    }
  }

  return (
    <>
      <BreadCrampTable links={links} className="" />

      <div className="flex items-center justify-between p-4">
        <div className="flex items-center p-1 rounded-xl bg-white border w-1/2">
          <Search size={20} color="gray" />
          <Input
            className="border-0 focus-visible:ring-0 focus-visible:ring-offset-0 focus:outline-none"
            placeholder="Chercher une société de gestion"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            
          />
        </div>
        <div className="flex gap-2">
          <Button onClick={handleOpenAdd}>Ajouter une société</Button>
          <Button variant="outline">Filtrer</Button>
        </div>
      </div>

      <div className="px-4">
        <DataTable
          columns={columns}
          data={companies}
          getRowId={(row) => row.company_id}
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
        initialData={editingCompany}
        onSave={handleSave}
        isLoading={isLoading}
        title={editingCompany ? "Modifier la société" : "Ajouter une société"}
      />

      <ConfirmDialog
              open={Boolean(deletingCompany)}
              onOpenChange={(open) => { if (!open) setdeletingCompany(null) }}
              onConfirm={handleConfirmDelete}
              title="Supprimer la société de gestion"
              description={`Voulez-vous vraiment supprimer "${deletingCompany?.company_name}" ? Cette action est irréversible.`}
          />
    </>
  )
}
import { useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Columns2,
  MoreHorizontal,
  Pencil,
  Trash2,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react"

export interface ColumnDef<T> {
  key: keyof T
  label: string
  render?: (row: T) => React.ReactNode
  className?: string
}

export interface PaginationState {
  page: number
  pageSize: number
  totalItems: number
  totalPages: number
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[]
  data: T[]
  getRowId: (row: T) => string | number
  onEdit?: (row: T) => void
  onDelete?: (row: T) => void
  emptyMessage?: string
  // Pagination contrôlée depuis le parent
  pagination?: PaginationState
  onPageChange?: (page: number) => void
  onPageSizeChange?: (pageSize: number) => void
  isLoading?: boolean
}

const PAGE_SIZE_OPTIONS = [5, 10, 25, 50]

export default function DataTable<T>({
  columns,
  data,
  getRowId,
  onEdit,
  onDelete,
  emptyMessage = "Aucune donnée à afficher.",
  pagination,
  onPageChange,
  onPageSizeChange,
  isLoading,
}: DataTableProps<T>) {
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(
    new Set(columns.map((c) => String(c.key)))
  )

  const visibleColumns = columns.filter((c) => visibleKeys.has(String(c.key)))
  const hasActions = Boolean(onEdit || onDelete)
  const hasPagination = Boolean(pagination && onPageChange)

  function toggleColumn(key: string) {
    setVisibleKeys((prev) => {
      const next = new Set(prev)
      if (next.has(key) && next.size === 1) return prev
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  // Calcul de la plage d'entrées affichées : ex "1–10 sur 34"
  function getRange() {
    if (!pagination) return null
    const from = (pagination.page - 1) * pagination.pageSize + 1
    const to = Math.min(pagination.page * pagination.pageSize, pagination.totalItems)
    return { from, to }
  }

  const range = getRange()

  return (
    <div className="space-y-3">

      {/* Barre d'outils */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          {pagination ? (
            <span className="text-xs text-muted-foreground font-mono">
              {pagination.totalItems} résultat{pagination.totalItems > 1 ? "s" : ""}
            </span>
          ) : (
            <span className="text-xs text-muted-foreground font-mono">
              {data.length} résultat{data.length > 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Toggle colonnes */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="gap-2 text-xs h-8">
              <Columns2 size={14} />
              Colonnes
              {visibleKeys.size < columns.length && (
                <Badge className="ml-1 h-4 w-4 p-0 flex items-center justify-center text-[10px] rounded-full">
                  {columns.length - visibleKeys.size}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44">
            <DropdownMenuLabel className="text-xs text-muted-foreground">
              Afficher les colonnes
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            {columns.map((col) => (
              <DropdownMenuCheckboxItem
                key={String(col.key)}
                checked={visibleKeys.has(String(col.key))}
                onCheckedChange={() => toggleColumn(String(col.key))}
                className="text-sm"
              >
                {col.label}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Tableau */}
      <div className="rounded-xl border border-border overflow-hidden shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50 hover:bg-muted/50">
              {visibleColumns.map((col) => (
                <TableHead
                  key={String(col.key)}
                  className={`text-xs font-semibold uppercase tracking-wide text-muted-foreground py-3 px-4 ${col.className ?? ""}`}
                >
                  {col.label}
                </TableHead>
              ))}
              {hasActions && (
                <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground py-3 px-4 text-right w-15">
                  Actions
                </TableHead>
              )}
            </TableRow>
          </TableHeader>

          <TableBody>
            {isLoading ? (
                <TableRow>
                <TableCell
                  colSpan={visibleColumns.length + (hasActions ? 1 : 0)}
                  className="py-16 text-center"
                >
                  <div className="flex flex-col items-center gap-2 text-muted-foreground">
                    <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                      <Columns2 size={18} className="opacity-40" />
                    </div>
                    <p className="text-sm">{"Téléchargement en cours..."}</p>
                  </div>
                </TableCell>
              </TableRow> ) : data.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={visibleColumns.length + (hasActions ? 1 : 0)}
                  className="py-16 text-center"
                >
                  <div className="flex flex-col items-center gap-2 text-muted-foreground">
                    <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                      <Columns2 size={18} className="opacity-40" />
                    </div>
                    <p className="text-sm">{emptyMessage}</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              data.map((item, index) => (
                <TableRow
                  key={getRowId(item)}
                  className={`transition-colors hover:bg-muted/30 border-border/60 ${
                    index % 2 === 0 ? "bg-background" : "bg-muted/10"
                  }`}
                >
                  {visibleColumns.map((col) => (
                    <TableCell
                      key={String(col.key)}
                      className={`py-3 px-4 text-sm ${col.className ?? ""}`}
                    >
                      {col.render
                        ? col.render(item)
                        : String((item as any)[col.key] ?? "—")}
                    </TableCell>
                  ))}

                  {hasActions && (
                    <TableCell className="py-3 px-4 text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7 opacity-50 hover:opacity-100 transition-opacity"
                          >
                            <MoreHorizontal size={15} />
                            <span className="sr-only">Actions</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-36">
                          {onEdit && (
                            <DropdownMenuItem
                              onClick={() => onEdit(item)}
                              className="gap-2 cursor-pointer"
                            >
                              <Pencil size={13} />
                              Modifier
                            </DropdownMenuItem>
                          )}
                          {onEdit && onDelete && <DropdownMenuSeparator />}
                          {onDelete && (
                            <DropdownMenuItem
                              onClick={() => onDelete(item)}
                              className="gap-2 cursor-pointer text-red-600 focus:text-red-600 focus:bg-red-50"
                            >
                              <Trash2 size={13} />
                              Supprimer
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {hasPagination && pagination && (
        <div className="flex items-center justify-between px-1 pt-1">

          {/* Lignes par page */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>Lignes par page</span>
            <Select
              value={String(pagination.pageSize)}
              onValueChange={(v) => onPageSizeChange?.(Number(v))}
            >
              <SelectTrigger className="h-8 w-16 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <SelectItem key={size} value={String(size)} className="text-xs">
                    {size}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Info plage + navigation */}
          <div className="flex items-center gap-4">
            {range && (
              <span className="text-xs text-muted-foreground font-mono">
                {range.from}–{range.to} sur {pagination.totalItems}
              </span>
            )}

            <div className="flex items-center gap-1">
              {/* Première page */}
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => onPageChange?.(1)}
                disabled={pagination.page === 1}
              >
                <ChevronsLeft size={14} />
              </Button>

              {/* Page précédente */}
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => onPageChange?.(pagination.page - 1)}
                disabled={pagination.page === 1}
              >
                <ChevronLeft size={14} />
              </Button>

              {/* Indicateur de page courante */}
              <span className="px-3 h-8 flex items-center text-xs font-medium border rounded-md bg-background min-w-20 justify-center">
                {pagination.page} / {pagination.totalPages}
              </span>

              {/* Page suivante */}
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => onPageChange?.(pagination.page + 1)}
                disabled={pagination.page === pagination.totalPages}
              >
                <ChevronRight size={14} />
              </Button>

              {/* Dernière page */}
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => onPageChange?.(pagination.totalPages)}
                disabled={pagination.page === pagination.totalPages}
              >
                <ChevronsRight size={14} />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
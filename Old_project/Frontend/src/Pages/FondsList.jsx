import { useState, useEffect, useCallback } from "react";
import ConfirmModal from "../Components/Confirmmodal";
import request from "../Requests/Axios";

function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

const APLITEC = {
  bg:     "rgba(26,95,168,0.10)",
  bgHov:  "rgba(26,95,168,0.18)",
  border: "rgba(26,95,168,0.30)",
  text:   "#6ca0d8",
};

export default function FondsList({ refreshTrigger }) {
  const [fonds,      setFonds]      = useState([]);
  const [total,      setTotal]      = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page,       setPage]       = useState(1);
  const PAGE_SIZE = 10;

  const [search,        setSearch]        = useState("");
  const [loading,       setLoading]       = useState(false);
  const [error,         setError]         = useState(null);

  // modal state
  const [modalOpen,     setModalOpen]     = useState(false);
  const [fondToDelete,  setFondToDelete]  = useState(null);
  const [deleting,      setDeleting]      = useState(false);
  const [deleteError,   setDeleteError]   = useState(null);
  const [deleteSuccess, setDeleteSuccess] = useState(false);

  const debouncedSearch = useDebounce(search);

  /* ── fetch ── */
  const fetchFonds = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page, page_size: PAGE_SIZE, search: debouncedSearch });
      const res  = await request.get(`fonds?${params}`);
      const data = res.data;
      setFonds(data.data);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err?.response?.data?.detail ?? err.message ?? "Erreur de chargement.");
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, refreshTrigger]);

  useEffect(() => { setPage(1); }, [debouncedSearch]);
  useEffect(() => { fetchFonds(); }, [fetchFonds]);

  /* ── delete ── */
  const handleDeleteClick = (fond) => {
    setFondToDelete(fond);
    setDeleteError(null);
    setDeleteSuccess(false);
    setModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!fondToDelete) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      const formData = new FormData();
      formData.append("nom", fondToDelete.nom.trim());
      await request.delete("/fonds/", { data: formData });
      setDeleteSuccess(true);
      fetchFonds();
    } catch (err) {
      setDeleteError(err?.response?.data?.detail ?? err.message ?? "Erreur lors de la suppression.");
    } finally {
      setDeleting(false);
    }
  };

  const handleModalClose = () => {
    if (deleting) return; // block close while request is in flight
    setModalOpen(false);
    setDeleteError(null);
    setDeleteSuccess(false);
    setFondToDelete(null);
  };

  /* ── pagination range ── */
  const paginationRange = () => {
    const delta = 1;
    const range = [];
    for (let i = Math.max(1, page - delta); i <= Math.min(totalPages, page + delta); i++) range.push(i);
    if (range[0] > 2)                              range.unshift("...");
    if (range[0] !== 1)                            range.unshift(1);
    if (range[range.length - 1] < totalPages - 1) range.push("...");
    if (range[range.length - 1] !== totalPages)   range.push(totalPages);
    return range;
  };

  return (
    <>
      <ConfirmModal
        isOpen={modalOpen}
        onClose={handleModalClose}
        onConfirm={handleDeleteConfirm}
        title="Supprimer le fond"
        message={`Voulez-vous vraiment supprimer "${fondToDelete?.nom}" ? Cette action est irréversible.`}
        confirmLabel="Supprimer"
        danger
        pending={deleting}
        error={deleteError}
        pendingLabel="Suppression en cours…"
        successTitle="Suppression réussie"
        successMessage="Le fond a été supprimé avec succès."
        success={deleteSuccess}
      />

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">

        {/* ── Header ── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-5 py-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 border"
              style={{ background: APLITEC.bg, borderColor: APLITEC.border }}
            >
              <svg className="w-4 h-4" style={{ color: APLITEC.text }} fill="none" viewBox="0 0 16 16">
                <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.2" />
                <path d="M2 6h12M6 6v8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
              </svg>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white leading-tight">Fonds</h2>
              <p className="text-xs text-slate-500 tabular-nums">
                {total} fond{total !== 1 ? "s" : ""} enregistré{total !== 1 ? "s" : ""}
              </p>
            </div>
          </div>

          {/* Search */}
          <div className="relative sm:w-64">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 pointer-events-none" fill="none" viewBox="0 0 14 14">
              <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.2" />
              <path d="M10 10l2.5 2.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Rechercher un fond…"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-8 pr-8 py-2 text-sm text-white placeholder-slate-500 outline-none transition-all"
              onFocus={(e) => { e.target.style.borderColor = APLITEC.border; e.target.style.boxShadow = `0 0 0 3px ${APLITEC.bg}`; }}
              onBlur={(e)  => { e.target.style.borderColor = ""; e.target.style.boxShadow = ""; }}
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 14 14">
                  <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* ── Error banner ── */}
        {error && (
          <div className="flex items-center gap-2 px-5 py-3 bg-red-500/10 border-b border-red-500/20 text-red-400 text-sm">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 16 16">
              <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.2" />
              <path d="M8 5v3.5m0 2h.01" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
            {error}
          </div>
        )}

        {/* ── Table ── */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left px-5 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Nom du fond</th>
                <th className="text-left px-5 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Ancienneté</th>
                <th className="px-5 py-3 w-14" />
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="border-b border-slate-800/60">
                    <td className="px-5 py-4">
                      <div className="h-3.5 bg-slate-800 rounded-full animate-pulse" style={{ width: `${140 + (i * 23) % 80}px` }} />
                    </td>
                    <td className="px-5 py-4">
                      <div className="h-5 bg-slate-800 rounded-md animate-pulse w-14" />
                    </td>
                    <td className="px-5 py-4" />
                  </tr>
                ))
              ) : fonds.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-5 py-16 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-500">
                      <div
                        className="w-12 h-12 rounded-xl flex items-center justify-center border"
                        style={{ background: APLITEC.bg, borderColor: APLITEC.border }}
                      >
                        <svg className="w-6 h-6" style={{ color: APLITEC.text, opacity: 0.6 }} fill="none" viewBox="0 0 24 24">
                          <rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" strokeWidth="1.5" />
                          <path d="M3 9h18M9 9v12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-400">
                          {search ? `Aucun résultat pour « ${search} »` : "Aucun fond enregistré"}
                        </p>
                        <p className="text-xs text-slate-600 mt-0.5">
                          {search ? "Essayez un autre terme de recherche." : "Créez votre premier fond via l'onglet Ajouter."}
                        </p>
                      </div>
                    </div>
                  </td>
                </tr>
              ) : (
                fonds.map((fond, i) => (
                  <tr
                    key={fond.nom}
                    className={`group transition-colors duration-150 hover:bg-slate-800/30 ${
                      i < fonds.length - 1 ? "border-b border-slate-800/60" : ""
                    }`}
                  >
                    <td className="px-5 py-3.5 font-medium text-white">{fond.nom}</td>
                    <td className="px-5 py-3.5">
                      {fond.anciennete ? (
                        <span
                          className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border"
                          style={{ background: APLITEC.bg, borderColor: APLITEC.border, color: APLITEC.text }}
                        >
                          {fond.anciennete === "A" ? "Ancien" : fond.anciennete === "N" ? "Nouveau" : fond.anciennete}
                        </span>
                      ) : (
                        <span className="text-slate-600 text-xs">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={() => handleDeleteClick(fond)}
                        title="Supprimer"
                        className="opacity-0 group-hover:opacity-100 focus:opacity-100 p-1.5 rounded-md text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-all duration-150"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                          <path d="M3 4h10M6 4V2.5a.5.5 0 01.5-.5h3a.5.5 0 01.5.5V4M5 4l.5 9h5L11 4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* ── Pagination ── */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-3.5 border-t border-slate-800">
            <p className="text-xs text-slate-500 tabular-nums">
              Page{" "}
              <span className="text-slate-300 font-medium">{page}</span>
              {" "}sur{" "}
              <span className="text-slate-300 font-medium">{totalPages}</span>
            </p>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                  <path d="M10 3L5 8l5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              {paginationRange().map((p, i) =>
                p === "..." ? (
                  <span key={`e-${i}`} className="px-1 text-slate-600 text-sm select-none">…</span>
                ) : (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className="min-w-[30px] h-7 px-2 rounded-md text-xs font-medium transition-all border"
                    style={
                      p === page
                        ? { background: APLITEC.bg, borderColor: APLITEC.border, color: APLITEC.text }
                        : { borderColor: "transparent", color: "#94a3b8" }
                    }
                    onMouseEnter={(e) => { if (p !== page) e.currentTarget.style.background = "rgba(255,255,255,0.05)"; }}
                    onMouseLeave={(e) => { if (p !== page) e.currentTarget.style.background = "transparent"; }}
                  >
                    {p}
                  </button>
                )
              )}
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                  <path d="M6 3l5 5-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
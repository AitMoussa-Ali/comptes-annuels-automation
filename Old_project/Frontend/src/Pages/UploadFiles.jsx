import { useState, useCallback, useRef } from "react";
import request from "../Requests/Axios";
import ConfirmModal from "../Components/Confirmmodal";

const APLITEC = {
  bg:     "rgba(26,95,168,0.10)",
  bgHov:  "rgba(26,95,168,0.18)",
  border: "rgba(26,95,168,0.30)",
  text:   "#6ca0d8",
};

/* ─── Fund search/select ─────────────────────────────────── */
function FondSelector({ selected, onSelect }) {
  const [query,    setQuery]    = useState("");
  const [results,  setResults]  = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [open,     setOpen]     = useState(false);
  const debounceRef = useRef(null);

  const search = (value) => {
    setQuery(value);
    setOpen(true);
    clearTimeout(debounceRef.current);
    if (!value.trim()) { setResults([]); return; }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res  = await request.get(`fonds?search=${encodeURIComponent(value)}&page=1&page_size=8`);
        setResults(res.data.data ?? []);
      } catch { setResults([]); }
      finally  { setLoading(false); }
    }, 300);
  };

  const pick = (fond) => {
    onSelect(fond);
    setQuery(fond.nom);
    setOpen(false);
    setResults([]);
  };

  const clear = () => {
    onSelect(null);
    setQuery("");
    setResults([]);
    setOpen(false);
  };

  return (
    <div className="relative">
      <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
        Fond <span className="text-red-400">*</span>
      </label>

      <div className="relative">
        {/* Search icon */}
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" fill="none" viewBox="0 0 16 16">
          <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" strokeWidth="1.2" />
          <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </svg>

        <input
          type="text"
          value={query}
          onChange={(e) => search(e.target.value)}
          onFocus={() => { if (results.length) setOpen(true); }}
          placeholder="Rechercher un fond…"
          className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-8 py-2.5 text-sm text-white placeholder-slate-500 outline-none transition-all"
          onFocus2={(e) => { e.target.style.borderColor = APLITEC.border; e.target.style.boxShadow = `0 0 0 3px ${APLITEC.bg}`; }}
          style={selected ? { borderColor: APLITEC.border } : {}}
        />

        {/* Clear */}
        {query && (
          <button onClick={clear} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 14 14">
              <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
          </button>
        )}
      </div>

      {/* Dropdown */}
      {open && (query.trim()) && (
        <div className="absolute z-20 mt-1 w-full bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden">
          {loading ? (
            <div className="px-4 py-3 text-xs text-slate-500 flex items-center gap-2">
              <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 16 16">
                <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" strokeDasharray="28" strokeDashoffset="10" />
              </svg>
              Recherche…
            </div>
          ) : results.length === 0 ? (
            <div className="px-4 py-3 text-xs text-slate-500">Aucun fond trouvé.</div>
          ) : (
            <ul className="max-h-52 overflow-y-auto divide-y divide-slate-800">
              {results.map((fond) => (
                <li key={fond.nom}>
                  <button
                    onClick={() => pick(fond)}
                    className="w-full flex items-center justify-between px-4 py-2.5 text-sm text-left hover:bg-slate-800 transition-colors"
                  >
                    <span className="text-slate-200 font-medium truncate">{fond.nom}</span>
                    {fond.anciennete && (
                      <span
                        className="ml-3 shrink-0 text-xs px-2 py-0.5 rounded-md border font-medium"
                        style={{ background: APLITEC.bg, borderColor: APLITEC.border, color: APLITEC.text }}
                      >
                        {fond.anciennete === "A" ? "Ancien" : fond.anciennete === "N" ? "Nouveau" : fond.anciennete}
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Selected badge */}
      {selected && (
        <div className="mt-2 flex items-center gap-2 text-xs" style={{ color: APLITEC.text }}>
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 14 14">
            <path d="M2 7l3.5 3.5 6.5-6.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span>
            <span className="font-medium">{selected.nom}</span>
            {selected.anciennete && (
              <span className="ml-1 text-slate-500">
                — {selected.anciennete === "A" ? "Ancien" : "Nouveau"}
              </span>
            )}
          </span>
        </div>
      )}
    </div>
  );
}

/* ─── Drop zone ──────────────────────────────────────────── */
function DropZone({ label, hint, accept, file, onFile, required }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  }, [onFile]);

  const handleChange = (e) => {
    const f = e.target.files[0];
    if (f) onFile(f);
  };

  const remove = (e) => {
    e.stopPropagation();
    onFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1">
        {label}
        {required && <span className="text-red-400">*</span>}
        {!required && <span className="text-slate-600 normal-case font-normal">(optionnel)</span>}
      </label>

      <div
        onClick={() => !file && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className="relative rounded-xl border-2 border-dashed transition-all duration-200 cursor-pointer"
        style={{
          borderColor: file
            ? APLITEC.border
            : dragging
            ? "rgba(26,95,168,0.5)"
            : "rgba(100,116,139,0.3)",
          background: file
            ? APLITEC.bg
            : dragging
            ? "rgba(26,95,168,0.06)"
            : "transparent",
          cursor: file ? "default" : "pointer",
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="hidden"
        />

        {file ? (
          /* File attached */
          <div className="flex items-center gap-3 px-4 py-3">
            <div
              className="shrink-0 w-9 h-9 rounded-lg flex items-center justify-center border"
              style={{ background: APLITEC.bg, borderColor: APLITEC.border }}
            >
              <svg className="w-4 h-4" style={{ color: APLITEC.text }} fill="none" viewBox="0 0 16 16">
                <path d="M4 2h6l4 4v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
                <path d="M9 2v4h4" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{file.name}</p>
              <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} Ko</p>
            </div>
            <button
              onClick={remove}
              className="shrink-0 p-1.5 rounded-md text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-all"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                <path d="M3 4h10M6 4V2.5a.5.5 0 01.5-.5h3a.5.5 0 01.5.5V4M5 4l.5 9h5L11 4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        ) : (
          /* Empty drop zone */
          <div className="flex flex-col items-center gap-2 px-4 py-6 text-center">
            <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center">
              <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 16 16">
                <path d="M8 2v8M5 5l3-3 3 3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M2 11v2a1 1 0 001 1h10a1 1 0 001-1v-2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
              </svg>
            </div>
            <div>
              <p className="text-xs text-slate-400">
                <span style={{ color: APLITEC.text }} className="font-medium">Cliquer pour importer</span>
                {" "}ou glisser-déposer
              </p>
              {hint && <p className="text-[11px] text-slate-600 mt-0.5">{hint}</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Main page ──────────────────────────────────────────── */
export default function UploadFiles() {
  const [selectedFond, setSelectedFond] = useState(null);

  const [fichierVlN,    setFichierVlN]    = useState(null);
  const [comptesAnnuels,setComptesAnnuels]= useState(null);
  const [fichierVlN1,   setFichierVlN1]   = useState(null);

  const [modalOpen,  setModalOpen]  = useState(false);
  const [pending,    setPending]    = useState(false);
  const [error,      setError]      = useState(null);
  const [success,    setSuccess]    = useState(false);

  const anciennete = selectedFond?.anciennete ?? null;
  const isAncien   = anciennete === "A";

  const canGenerate =
    selectedFond &&
    fichierVlN &&
    comptesAnnuels &&
    (isAncien ? !!fichierVlN1 : true);

  const handleGenerate = async () => {
    if (!canGenerate) return;
    setPending(true);
    setError(null);
    setSuccess(false);
    setModalOpen(true);

    try {
      const formData = new FormData();
      formData.append("anciennete", anciennete);
      formData.append("fichier_vl_n", fichierVlN);
      formData.append("comptes_annuels", comptesAnnuels);
      if (isAncien && fichierVlN1) formData.append("fichier_vl_n_1", fichierVlN1);

      const res = await request.post("generate/", formData, { responseType: "blob" });

      // Trigger download
      const url  = URL.createObjectURL(res.data);
      const link = document.createElement("a");
      link.href  = url;
      link.download = `comptes_annuels_${selectedFond.nom.replace(/\s+/g, "_")}.xlsm`;
      link.click();
      URL.revokeObjectURL(url);

      setSuccess(true);
      setPending(false);
    } catch (err) {
      const detail = err?.response?.data?.detail ?? err.message ?? "Erreur lors de la génération.";
      setError(Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : detail);
      setPending(false);
    }
  };

  const handleModalClose = () => {
    if (pending) return;
    setModalOpen(false);
    setError(null);
    setSuccess(false);
  };

  return (
    <>
      <ConfirmModal
        isOpen={modalOpen}
        onClose={handleModalClose}
        error={error}
        success={success}
        pending={pending}
        pendingLabel="Génération en cours…"
        successTitle="Fichier généré avec succès"
        successMessage="Le téléchargement a démarré automatiquement."
      />

      <div className="max-w-2xl mx-auto flex flex-col gap-6">

        {/* ── Header ── */}
        <div>
          <h1 className="text-lg font-semibold text-white">Générer les comptes annuels</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Sélectionnez un fond puis importez les fichiers requis selon son ancienneté.
          </p>
        </div>

        {/* ── Card ── */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col gap-6">

          {/* Step 1 — Fund selection */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span
                className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold border shrink-0"
                style={{ background: APLITEC.bg, borderColor: APLITEC.border, color: APLITEC.text }}
              >1</span>
              <p className="text-sm font-semibold text-white">Sélectionner un fond</p>
            </div>
            <FondSelector selected={selectedFond} onSelect={setSelectedFond} />
          </div>

          {/* Divider */}
          <div className="border-t border-slate-800" />

          {/* Step 2 — File uploads */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span
                className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold border shrink-0"
                style={{
                  background: selectedFond ? APLITEC.bg : "rgba(51,65,85,0.4)",
                  borderColor: selectedFond ? APLITEC.border : "rgba(71,85,105,0.4)",
                  color: selectedFond ? APLITEC.text : "#475569",
                }}
              >2</span>
              <p className={`text-sm font-semibold ${selectedFond ? "text-white" : "text-slate-600"}`}>
                Importer les fichiers
              </p>
              {selectedFond && anciennete && (
                <span
                  className="ml-auto text-xs px-2 py-0.5 rounded-md border font-medium"
                  style={{ background: APLITEC.bg, borderColor: APLITEC.border, color: APLITEC.text }}
                >
                  {isAncien ? "3 fichiers requis" : "2 fichiers requis"}
                </span>
              )}
            </div>

            {!selectedFond ? (
              <div className="rounded-xl border border-dashed border-slate-800 px-4 py-8 flex flex-col items-center gap-2 text-center">
                <svg className="w-8 h-8 text-slate-700" fill="none" viewBox="0 0 32 32">
                  <path d="M10 20l6-6 6 6M16 14v10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M26 22a4 4 0 000-8h-1.2A9 9 0 106 21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
                <p className="text-sm text-slate-600">Sélectionnez d'abord un fond pour voir les fichiers requis.</p>
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                <DropZone
                  label="Fichier VL N"
                  hint="Fichier Excel des valeurs liquidatives de l'exercice en cours"
                  accept=".xlsx,.xls,.xlsm"
                  file={fichierVlN}
                  onFile={setFichierVlN}
                  required
                />
                <DropZone
                  label="Comptes annuels"
                  hint="Template .xlsm des comptes annuels à remplir"
                  accept=".xlsm"
                  file={comptesAnnuels}
                  onFile={setComptesAnnuels}
                  required
                />
                {isAncien && (
                  <DropZone
                    label="Fichier VL N-1"
                    hint="Fichier Excel des valeurs liquidatives de l'exercice précédent"
                    accept=".xlsx,.xls,.xlsm"
                    file={fichierVlN1}
                    onFile={setFichierVlN1}
                    required
                  />
                )}
              </div>
            )}
          </div>

          {/* Divider */}
          {selectedFond && <div className="border-t border-slate-800" />}

          {/* Generate button */}
          {selectedFond && (
            <div className="flex items-center justify-between gap-4">
              {/* Progress pills */}
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <Pill ok={!!fichierVlN}    label="VL N" />
                <Pill ok={!!comptesAnnuels} label="Comptes" />
                {isAncien && <Pill ok={!!fichierVlN1} label="VL N-1" />}
              </div>

              <button
                onClick={handleGenerate}
                disabled={!canGenerate}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium border transition-all duration-150 active:scale-[0.97] disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  background: canGenerate ? APLITEC.bgHov : "rgba(26,95,168,0.06)",
                  borderColor: canGenerate ? "rgba(26,95,168,0.5)" : "rgba(26,95,168,0.15)",
                  color: canGenerate ? "#ffffff" : APLITEC.text,
                }}
                onMouseEnter={(e) => { if (canGenerate) e.currentTarget.style.background = "rgba(26,95,168,0.28)"; }}
                onMouseLeave={(e) => { if (canGenerate) e.currentTarget.style.background = APLITEC.bgHov; }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                  <path d="M3 8h10M9 5l4 3-4 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Générer
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

/* tiny status pill */
function Pill({ ok, label }) {
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-[11px] font-medium transition-all"
      style={ok
        ? { background: APLITEC.bg, borderColor: APLITEC.border, color: APLITEC.text }
        : { background: "rgba(51,65,85,0.3)", borderColor: "rgba(71,85,105,0.3)", color: "#475569" }
      }
    >
      {ok
        ? <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 10 10"><path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" /></svg>
        : <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 10 10"><circle cx="5" cy="5" r="3.5" stroke="currentColor" strokeWidth="1.2" /></svg>
      }
      {label}
    </span>
  );
}
import { useState } from "react";
import request from "../Requests/Axios";
import { useApp } from "../Context/AppContext";
import ConfirmModal from "../Components/Confirmmodal";

export default function CreateFond({ onCreated }) {
  const [nom,        setNom]        = useState("");
  const [anciennete, setAnciennete] = useState("");

  const [modalOpen,  setModalOpen]  = useState(false);
  const [pending,    setPending]    = useState(false);
  const [error,      setError]      = useState(null);
  const [success,    setSuccess]    = useState(false);
  const [nomSaved, setNomSaved] = useState("");


  const { setCreating } = useApp();

  /* Open modal on submit — validate first */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!nom.trim()) {
      setError("Le nom du fond est requis.");
      setSuccess(false);
      setModalOpen(true);
      return;
    }
    setError(null);
    setSuccess(false);
    setModalOpen(true);
  };

  /* Actual API call — triggered by modal confirm button */
  const handleConfirm = async () => {
  setPending(true);
  setCreating(true);
  const nomSaved = nom.trim(); // ← 
  // sauvegarder avant de vider
  setNomSaved(nomSaved);
  try {
    const formData = new FormData();
    formData.append("nom", nomSaved);
    if (anciennete.trim()) formData.append("anciennete", anciennete.trim());
    await request.post("/fonds/", formData);
    setSuccess(true);
    setPending(false);
    setCreating(false);
    setNom("");        // ← vide le champ, mais nomSaved est toujours là
    setAnciennete("");
    onCreated?.();
  } catch (err) {
  const detail = err?.response?.data?.detail;
  
  // detail peut être un tableau d'objets FastAPI [{type, loc, msg, input}]
  // ou une string simple
  const message = Array.isArray(detail)
    ? detail.map((d) => d.msg).join(", ")
    : detail ?? err.message ?? "Erreur lors de la création.";

  setError(message);
  setPending(false);
  setCreating(false);
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
        onConfirm={handleConfirm}
        title="Confirmer la création"
        message={`Voulez-vous créer le fond "${nom.trim()}" ?`}
        confirmLabel="Créer"
        pending={pending}
        pendingLabel="Création en cours…"
        error={error}
        success={success}
        successTitle="Fond créé avec succès"
        successMessage={`Le fond "${nomSaved.trim()}" a bien été ajouté.`}
      />

      <div className="bg-slate-900 border border-slate-800 max-h-full rounded-xl p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border"
            style={{ background: "rgba(26,95,168,0.12)", borderColor: "rgba(26,95,168,0.3)" }}
          >
            <svg className="w-4 h-4" style={{ color: "#6ca0d8" }} fill="none" viewBox="0 0 16 16">
              <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <h2 className="text-sm font-semibold text-white">Ajouter un fond</h2>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Nom */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Nom du fond <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              placeholder="Ex : Fonds Croissance Europe"
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 outline-none transition-all"
              onFocus={(e) => { e.target.style.borderColor = "rgba(26,95,168,0.6)"; e.target.style.boxShadow = "0 0 0 3px rgba(26,95,168,0.15)"; }}
              onBlur={(e)  => { e.target.style.borderColor = ""; e.target.style.boxShadow = ""; }}
            />
          </div>

          {/* Ancienneté */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Ancienneté
            </label>
            <select
              value={anciennete}
              onChange={(e) => setAnciennete(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white outline-none appearance-none cursor-pointer transition-all"
              onFocus={(e) => { e.target.style.borderColor = "rgba(26,95,168,0.6)"; e.target.style.boxShadow = "0 0 0 3px rgba(26,95,168,0.15)"; }}
              onBlur={(e)  => { e.target.style.borderColor = ""; e.target.style.boxShadow = ""; }}
            >
              <option value="">— Sélectionner —</option>
              <option value="A">Ancien</option>
              <option value="N">Nouveau</option>
            </select>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="mt-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium border transition-all duration-150 active:scale-[0.97]"
            style={{ background: "rgba(26,95,168,0.15)", borderColor: "rgba(26,95,168,0.4)", color: "#6ca0d8" }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(26,95,168,0.25)"; e.currentTarget.style.borderColor = "rgba(26,95,168,0.6)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(26,95,168,0.15)"; e.currentTarget.style.borderColor = "rgba(26,95,168,0.4)"; }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
              <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            Créer le fond
          </button>
        </form>
      </div>
    </>
  );
}
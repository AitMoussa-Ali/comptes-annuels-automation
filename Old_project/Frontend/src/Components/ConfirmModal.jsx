export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Confirmer",
  danger = false,
  // shared async states
  pending = false,
  pendingLabel = "En cours…",
  error = null,
  success = false,
  successTitle = "Opération réussie",
  successMessage = "",
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop — blocked while pending */}
      <div
        className={`absolute inset-0 bg-black/60 backdrop-blur-sm ${pending ? "pointer-events-none" : ""}`}
        onClick={!pending ? onClose : undefined}
      />

      <div className="relative z-10 w-full max-w-sm mx-4 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden">

        {/* ── Body ── */}
        <div className="p-6">
          {error ? (
            /* Error state */
            <div className="flex flex-col items-center gap-3 py-2 text-center">
              <div className="w-11 h-11 rounded-full flex items-center justify-center border bg-red-500/10 border-red-500/30">
                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 20 20">
                  <path d="M10 6v4m0 3h.01" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                  <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-white">Échec de l'opération</p>
                <p className="text-xs text-red-400 mt-1">{error}</p>
              </div>
            </div>

          ) : success ? (
            /* Success state */
            <div className="flex flex-col items-center gap-3 py-2 text-center">
              <div
                className="w-11 h-11 rounded-full flex items-center justify-center border"
                style={{ background: "rgba(26,95,168,0.12)", borderColor: "rgba(26,95,168,0.3)" }}
              >
                <svg className="w-5 h-5" style={{ color: "#6ca0d8" }} fill="none" viewBox="0 0 20 20">
                  <path d="M4 10.5l4 4 8-8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-white">{successTitle}</p>
                {<p className="text-xs text-slate-400 mt-0.5">{successMessage}</p>}
              </div>
            </div>

          ) : (
            /* Confirm / pending state */
            <div className="flex items-start gap-4">
              <div className={`shrink-0 w-10 h-10 rounded-full flex items-center justify-center border ${
                danger ? "bg-red-500/10 border-red-500/20" : "bg-slate-800 border-slate-700"
              }`}>
                {pending ? (
                  <svg className="w-5 h-5 text-slate-400 animate-spin" fill="none" viewBox="0 0 20 20">
                    <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5" strokeDasharray="35" strokeDashoffset="12" />
                  </svg>
                ) : danger ? (
                  <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 20 20">
                    <path d="M10 7v5m0 2.5h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 20 20">
                    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
                    <path d="M10 9v5m0-7h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-base font-semibold text-white mb-1">
                  {pending ? pendingLabel : title}
                </h2>
                <p className="text-sm text-slate-400 leading-relaxed">
                  {pending ? "Veuillez patienter, cette opération peut prendre quelques secondes." : message}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* ── Footer ── */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-800 bg-slate-900/60">
          {success || error ? (
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-150 active:scale-[0.97]"
              style={{ background: "rgba(26,95,168,0.15)", borderColor: "rgba(26,95,168,0.4)", color: "#6ca0d8" }}
            >
              {success ? "OK" : "Fermer"}
            </button>
          ) : (
            <>
              <button
                onClick={onClose}
                disabled={pending}
                className="px-4 py-2 rounded-lg text-sm font-medium border border-slate-700 text-slate-300 hover:border-slate-600 hover:text-white hover:bg-slate-800 transition-all duration-150 active:scale-[0.97] disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Annuler
              </button>
              <button
                onClick={onConfirm}
                disabled={pending}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 active:scale-[0.97] disabled:opacity-60 disabled:cursor-not-allowed border ${
                  danger
                    ? "border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:border-red-500"
                    : "border-slate-600 bg-slate-800 text-white hover:bg-slate-700"
                }`}
              >
                {pending && (
                  <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 16 16">
                    <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" strokeDasharray="28" strokeDashoffset="10" />
                  </svg>
                )}
                {pending ? pendingLabel : confirmLabel}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
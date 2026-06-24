import { useState } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { STEPS } from "../Config/Steps";
import logoAplitec from "../Assets/logo_aplitec.jpg";

/* ─────────────────────────────────────────────────────────────
   Navigation helpers
───────────────────────────────────────────────────────────── */
function useNavigation(currentIndex) {
  const navigate = useNavigate();
  const isFirst = currentIndex === 0;
  const isLast  = currentIndex === STEPS.length - 1;
  const progressPct =
    currentIndex >= 0
      ? Math.round((currentIndex / (STEPS.length - 1)) * 100)
      : 0;
  const goNext = () => { if (!isLast)  navigate(STEPS[currentIndex + 1].path); };
  const goPrev = () => { if (!isFirst) navigate(STEPS[currentIndex - 1].path); };
  const goTo   = (step) => navigate(step.path);
  return { isFirst, isLast, progressPct, goNext, goPrev, goTo };
}

/* ─────────────────────────────────────────────────────────────
   Step pill
───────────────────────────────────────────────────────────── */
function StepPill({ step, isActive, isPast, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`
        group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
        text-left transition-all duration-200 outline-none
        ${isActive
          ? "bg-[#1a5fa8]/15 border border-[#1a5fa8]/30 text-white shadow-md"
          : isPast
          ? "bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-white"
          : "text-slate-500 hover:bg-slate-800/50 hover:text-slate-300"
        }
      `}
    >
      {/* Connector line to next step */}
      {step.index < STEPS.length - 1 && (
        <span
          className={`absolute left-[1.375rem] top-[calc(100%+2px)] w-px h-3 transition-colors duration-300 ${
            isPast ? "bg-[#1a5fa8]/40" : "bg-slate-700/50"
          }`}
        />
      )}

      {/* Circle indicator */}
      <span
        className={`
          relative z-10 shrink-0 w-6 h-6 rounded-full flex items-center justify-center
          text-xs font-semibold transition-all duration-200 ring-1
          ${isActive
            ? "bg-[#1a5fa8] ring-[#1a5fa8]/50 text-white shadow-[0_0_10px_rgba(26,95,168,0.4)]"
            : isPast
            ? "bg-[#1a5fa8]/20 ring-[#1a5fa8]/30 text-[#6ca0d8]"
            : "bg-slate-800 ring-slate-700 text-slate-500"
          }
        `}
      >
        {isPast ? (
          <svg className="w-3 h-3" fill="none" viewBox="0 0 12 12">
            <path d="M2 6.5l2.5 2.5 5.5-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : (
          step.index + 1
        )}
      </span>

      {/* Label */}
      <span className="text-sm font-medium leading-tight truncate">
        {step.label}
      </span>

      {/* Active dot */}
      {isActive && (
        <span className="ml-auto shrink-0 w-1.5 h-1.5 rounded-full bg-[#1a5fa8]" />
      )}
    </button>
  );
}

/* ─────────────────────────────────────────────────────────────
   Step list
───────────────────────────────────────────────────────────── */
function StepList({ currentIndex, goTo }) {
  return (
    <div className="flex flex-col gap-1">
      {STEPS.map((step) => (
        <StepPill
          key={step.path}
          step={step}
          isActive={step.index === currentIndex}
          isPast={step.index < currentIndex}
          onClick={() => goTo(step)}
        />
      ))}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Sidebar content
───────────────────────────────────────────────────────────── */
function SideBarContent({ currentIndex, progressPct, goTo }) {
  return (
    <div className="flex flex-col h-full">
      {/* Logo zone */}
      <div className="flex items-center gap-3 px-4 py-4 border-b border-slate-800">
        <div className="w-9 h-9 rounded-xl overflow-hidden bg-white ring-1 ring-slate-700 shrink-0 flex items-center justify-center p-1">
          <img src={logoAplitec} alt="Aplitec" className="w-full h-full object-contain" />
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-[13px] font-bold tracking-wide text-white">APLITEC</span>
          <span className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">
            Comptes annuels
          </span>
        </div>
      </div>

      {/* Steps nav */}
      <div className="flex-1 overflow-y-auto px-3 pt-5 pb-4 scrollbar-thin scrollbar-thumb-slate-700">
        <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500 mb-3 px-3">
          Étapes
        </p>
        <nav>
          <StepList currentIndex={currentIndex} goTo={goTo} />
        </nav>
      </div>

      {/* Progress footer */}
      <div className="px-4 py-4 border-t border-slate-800 bg-slate-900/60">
        <div className="flex items-center justify-between mb-2">
          <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500">
            Progression
          </p>
          <span className="text-xs font-semibold tabular-nums" style={{ color: "#6ca0d8" }}>
            {progressPct}%
          </span>
        </div>

        <div className="relative h-1 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out"
            style={{
              width: `${progressPct}%`,
              background: "linear-gradient(90deg, #1a5fa8, #4d8fd4)",
            }}
          />
        </div>

        <p className="mt-2 text-[11px] text-slate-500">
          {progressPct === 100
            ? "Toutes les étapes complétées ✓"
            : `${currentIndex + 1} / ${STEPS.length} étapes`}
        </p>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Mobile drawer
───────────────────────────────────────────────────────────── */
function MobileDrawer({ isOpen, onClose, children }) {
  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden transition-opacity duration-300 ${
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        onClick={onClose}
      />
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 lg:hidden bg-slate-900 border-r border-slate-800 shadow-2xl transition-transform duration-300 ease-out ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
            <path d="M3 3L13 13M13 3L3 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
        {children}
      </aside>
    </>
  );
}

/* ─────────────────────────────────────────────────────────────
   Main layout
───────────────────────────────────────────────────────────── */
export default function MainLayout() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const currentIndex = STEPS.findIndex(
    (s) =>
      s.path === location.pathname ||
      (s.path !== "/" &&
        location.pathname.startsWith(s.path.split("/").slice(0, 2).join("/")))
  );

  const { isFirst, isLast, progressPct, goNext, goPrev, goTo } = useNavigation(currentIndex);
  const currentStep = STEPS[currentIndex] ?? null;

  const sidebarProps = { currentIndex, progressPct, goTo };

  return (
    <div className="w-full h-screen bg-slate-950 text-white flex flex-col overflow-hidden">

      {/* ── HEADER ── */}
      <header className="sticky top-0 z-30 flex items-center h-14 px-4 md:px-6 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 shadow-sm w-full">
        {/* Mobile hamburger */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden mr-3 p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          aria-label="Ouvrir le menu"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 20 20">
            <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>

        {/* Logo — desktop (hidden, already in sidebar) / mobile */}
        <div className="flex lg:hidden items-center gap-3">
          <div className="w-8 h-8 rounded-lg overflow-hidden bg-white ring-1 ring-slate-700 shrink-0 flex items-center justify-center p-0.5">
            <img src={logoAplitec} alt="Aplitec" className="w-full h-full object-contain" />
          </div>
          <span className="text-[13px] font-bold tracking-wide text-white sm:block hidden">APLITEC</span>
        </div>

        {/* Desktop: brand strip */}
        <div className="hidden lg:flex items-center gap-3">
          <div
            className="h-5 w-px mx-1"
            style={{ background: "rgba(26,95,168,0.4)" }}
          />
          <span className="text-xs font-medium text-slate-400 tracking-wide">
            Générateur des comptes annuels
          </span>
        </div>

        <div className="flex-1" />

        {/* Current step badge — desktop */}
        {currentStep && (
          <div className="hidden md:flex items-center gap-2 text-sm">
            <span className="text-slate-500 text-xs">Étape</span>
            <span
              className="px-2 py-0.5 rounded-md text-xs font-semibold tabular-nums border"
              style={{
                background: "rgba(26,95,168,0.12)",
                borderColor: "rgba(26,95,168,0.3)",
                color: "#6ca0d8",
              }}
            >
              {currentStep.index + 1}/{STEPS.length}
            </span>
            <span className="text-slate-300 text-sm font-medium">{currentStep.label}</span>
          </div>
        )}

        {/* Progress pill — mobile */}
        <div className="flex sm:hidden items-center gap-2">
          <span className="text-xs font-semibold tabular-nums" style={{ color: "#6ca0d8" }}>
            {progressPct}%
          </span>
          <div className="w-20 h-1 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%`, background: "#1a5fa8" }}
            />
          </div>
        </div>
      </header>

      {/* ── BODY ── */}
      <div className="flex flex-1 min-h-0">

        {/* Desktop sidebar */}
        <aside className="hidden lg:flex flex-col w-64 xl:w-72 shrink-0 bg-slate-900 border-r border-slate-800 overflow-hidden">
          <SideBarContent {...sidebarProps} />
        </aside>

        {/* Mobile drawer */}
        <MobileDrawer isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)}>
          <SideBarContent {...sidebarProps} />
        </MobileDrawer>

        {/* Main content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">

            {/* Sticky breadcrumb */}
            {currentStep && (
              <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/60 px-6 py-3 flex items-center gap-3">
                <span
                  className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border"
                  style={{
                    background: "rgba(26,95,168,0.12)",
                    borderColor: "rgba(26,95,168,0.3)",
                    color: "#6ca0d8",
                  }}
                >
                  {currentStep.index + 1}
                </span>
                <h1 className="text-sm font-semibold text-slate-200 truncate">
                  {currentStep.label}
                </h1>
                <span
                  className="ml-auto shrink-0 text-[10px] font-medium px-2 py-0.5 rounded-full border"
                  style={{
                    background: "rgba(26,95,168,0.08)",
                    borderColor: "rgba(26,95,168,0.25)",
                    color: "#6ca0d8",
                  }}
                >
                  Toujours accessible
                </span>
              </div>
            )}

            <div className="p-4 md:p-6 lg:p-8">
              <Outlet />
            </div>
          </div>

          {/* ── FOOTER NAV ── */}
          <footer className="shrink-0 bg-slate-900 border-t border-slate-800 px-4 md:px-6 py-3">
            <div className="max-w-4xl mx-auto flex items-center justify-between gap-3">

              <button
                onClick={goPrev}
                disabled={isFirst}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-150 ${
                  isFirst
                    ? "border-slate-800 text-slate-600 cursor-not-allowed"
                    : "border-slate-700 text-slate-300 hover:border-slate-600 hover:text-white hover:bg-slate-800 active:scale-[0.97]"
                }`}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                  <path d="M10 3L5 8L10 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="hidden sm:inline">Précédent</span>
              </button>

              {/* Dot stepper */}
              <div className="hidden md:flex items-center gap-1.5">
                {STEPS.map((step) => (
                  <button
                    key={step.path}
                    onClick={() => goTo(step)}
                    className="rounded-full transition-all duration-200 cursor-pointer"
                    style={{
                      width:  step.index === currentIndex ? "20px" : "8px",
                      height: "8px",
                      background:
                        step.index === currentIndex
                          ? "#1a5fa8"
                          : step.index < currentIndex
                          ? "#2d6faa"
                          : "#334155",
                    }}
                    aria-label={step.label}
                  />
                ))}
              </div>

              <div className="md:hidden text-xs text-slate-500 font-medium">
                {currentIndex + 1} / {STEPS.length}
              </div>

              <button
                onClick={goNext}
                disabled={isLast}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-150 ${
                  isLast
                    ? "border-slate-800 text-slate-600 cursor-not-allowed"
                    : "text-white hover:brightness-110 active:scale-[0.97]"
                }`}
                style={
                  !isLast
                    ? {
                        background: "rgba(26,95,168,0.15)",
                        borderColor: "rgba(26,95,168,0.5)",
                        color: "#6ca0d8",
                      }
                    : {}
                }
              >
                <span className="hidden sm:inline">Suivant</span>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                  <path d="M6 3L11 8L6 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>

            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
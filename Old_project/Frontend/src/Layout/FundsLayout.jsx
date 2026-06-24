import { NavLink, Outlet } from "react-router-dom";
import { AppProvider, useApp } from "../Context/AppContext";

const tabs = [
  {
    to: "/funds/list",
    label: "Liste des fonds",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
        <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.2" />
        <path d="M2 6h12M6 6v8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    to: "/funds/create",
    label: "Ajouter un fond",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
        <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
];

function TabBar() {
  const { creating } = useApp();

  return (
    <div
      className="flex items-center gap-1 p-1 rounded-xl w-fit border"
      style={{ background: "rgba(26,95,168,0.06)", borderColor: "rgba(26,95,168,0.2)" }}
    >
      {tabs.map((tab) => {
        const isLocked = creating && tab.to === "/funds/list";

        if (isLocked) {
          return (
            <div
              key={tab.to}
              title="Création en cours, veuillez patienter…"
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border cursor-not-allowed select-none"
              style={{ borderColor: "transparent", color: "#475569", opacity: 0.5 }}
            >
              <span>{tab.icon}</span>
              {tab.label}
              {/* spinner */}
              <svg className="w-3.5 h-3.5 animate-spin ml-0.5" fill="none" viewBox="0 0 16 16">
                <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" strokeDasharray="28" strokeDashoffset="10" />
              </svg>
            </div>
          );
        }

        return (
          <NavLink
            key={tab.to}
            to={tab.to}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 border"
            style={({ isActive }) =>
              isActive
                ? {
                    background: "rgba(26,95,168,0.18)",
                    borderColor: "rgba(26,95,168,0.4)",
                    color: "#ffffff",
                    boxShadow: "0 1px 6px rgba(26,95,168,0.2)",
                  }
                : {
                    borderColor: "transparent",
                    color: "#94a3b8",
                  }
            }
          >
            {({ isActive }) => (
              <>
                <span style={{ color: isActive ? "#6ca0d8" : "currentColor" }}>
                  {tab.icon}
                </span>
                {tab.label}
              </>
            )}
          </NavLink>
        );
      })}
    </div>
  );
}

export default function FundsLayout() {
  return (
    <AppProvider>
      <div className="flex flex-col gap-6">
        <TabBar />
        <Outlet />
      </div>
    </AppProvider>
  );
}
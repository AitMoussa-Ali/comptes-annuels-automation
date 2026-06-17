import { createContext, useContext, useState } from "react";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [sessionId, setSessionId]       = useState(null);
  const [selectedFund, setSelectedFund] = useState(null); // full FundResponse object
  const [creating, setCreating] = useState(false);
  const [presentation, setPresentation] = useState({
  company_name: "",
  fund_name: "",
  closing_date: "",
  adress: "",
  departement: "",
  });


  const reset = () => {
    setSessionId(null);
    setSelectedFund(null);
  };

  return (
    <AppContext.Provider value={{ sessionId, setSessionId, selectedFund, setSelectedFund, reset, presentation, setPresentation, creating, setCreating }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used inside <AppProvider>");
  return ctx;
}
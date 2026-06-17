import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import MainLayout from './Layout/MainLayout'
import { router } from "./Router/Router";
import { RouterProvider } from "react-router-dom";
import { AppProvider } from './Context/AppContext'

function App() {
  const [count, setCount] = useState(0)

  return (
    <AppProvider>
      <RouterProvider router={router} />
    </AppProvider>
  )
}

export default App

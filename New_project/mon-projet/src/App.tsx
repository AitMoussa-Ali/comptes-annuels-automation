
import './App.css'
import { RouterProvider } from "react-router-dom";
import { router } from './Router/router';
import { Toaster } from '@/components/ui/sonner';

function App() {

  return (
    <>
    
    
    <RouterProvider router={router} />
    <Toaster richColors position="top-right" />

    </>
  )
}

export default App

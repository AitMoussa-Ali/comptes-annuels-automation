import AppLayout from "@/components/Layouts/navbar/AppLayout";
import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import CompaniesPage from "../Pages/Companies";
import Funds from "../Pages/Funds";
import UploadPage from "../Pages/Upload/UploadPage";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <AppLayout></AppLayout>
    },
    {
        element: <AppLayout></AppLayout>,
        children: [
            {
                path : "/Fonds",
                element : <Funds></Funds>
            },
            {
                path: "/Societes",
                element : <CompaniesPage></CompaniesPage>
            },
            {
                path: "/Upload",
                element : <UploadPage></UploadPage>
            },
        ]
    }
])
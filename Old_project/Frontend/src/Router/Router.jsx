import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import MainLayout from "../Layout/MainLayout";
import FundsLayout from "../Layout/FundsLayout";
import CreateFond from "../Pages/CreateFond";
import FondsList from "../Pages/FondsList";
import UploadFiles from "../Pages/UploadFiles";


export const router = createBrowserRouter([
  {
    element: <MainLayout />,
    children: [
      {
        path: "/upload_files",
        element: <UploadFiles></UploadFiles>,
      },
      {
        element: <Outlet />,
        children: [
              {
                path: "/funds",
                element: <FundsLayout />,
                children: [
                  { index: true,    element: <Navigate to="/funds/list" replace /> },
                  { path: "create", element: <CreateFond /> },
                  { path: "list",   element: <FondsList /> },
                ],
            }
        ],
      },
      {
        index: true,
        element: <Navigate to="/upload_files" replace />,
      },
    ],
  },
]);
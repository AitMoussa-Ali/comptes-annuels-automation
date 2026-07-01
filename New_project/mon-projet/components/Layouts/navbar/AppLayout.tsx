
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuItem, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Building2, BadgeEuro, FileDown, LogOut } from "lucide-react"
import logo from "@/src/assets/logo.jpg"
import { Link, NavLink, Outlet } from "react-router-dom"
import path from "path"

const navitems = [
    {
        section : "Général", items : [
                                { label : "Société de gestion", icon : <Building2 size={20} color="gray"/>, path : "/Societes"},
                                { label : "Fonds", icon : <BadgeEuro size={20}color="gray"></BadgeEuro >, path : "/Fonds" }
                            ]
    }, 
    {
        section : "Rapports", items : [
            { label : "Importer les fichiers", icon : <FileDown color="gray" size={20}/>, path : "/Upload"  }
        ]
    }
]

const paths = [
    {
        path : "/Societes", breadcamp : "Général > Société de gestion"
    },
    {
        path : "/Fonds", breadcamp : "Général > Fonds"
    }
]



export default function AppLayout(){


    return(    
        <SidebarProvider>
            <div className="flex flex-col h-screen w-full">
                {/* Header sur toute la largeur, au-dessus de tout */}
                <header className="h-16 border-b flex items-center px-4 shrink-0 w-full relative z-20">
                  <SidebarTrigger size="icon-lg"/>
                </header>
                {/* Corps de la page */}
                <div className="flex flex-1 overflow-hidden relative">
                    <Sidebar className="top-16! h-[calc(100svh-4rem)]!">
                        <SidebarContent>
                            {navitems.map((section) => (
                                <SidebarGroup key={section.section}>
                                    <SidebarGroupLabel>{section.section}</SidebarGroupLabel>
                                    <SidebarGroupContent>
                                        <SidebarMenu>
                                            {section.items.map((item) => (
                                                    <SidebarMenuItem key={item.label}>
                                                        <NavLink
                                                            to={item.path}
                                                            className="flex items-center p-2 rounded-sm text-xs mb-2"
                                                        >
                                                            {item.icon}
                                                            <span className="ml-2">{item.label}</span>
                                                        </NavLink>
                                                    </SidebarMenuItem>
                                            ))}
                                        </SidebarMenu>
                                    </SidebarGroupContent>
                                </SidebarGroup>
                            ))}
                        </SidebarContent>

                        <SidebarFooter>
                            <SidebarMenu>
                                <SidebarMenuItem
                                    className="flex items-center p-2 rounded-sm text-xs  mb-2 cursor-pointer"
                                    key="deconnecter"
                                >
                                    <LogOut size={20} color="gray"/>
                                    <span className="ml-2">Déconnecter</span>
                                </SidebarMenuItem>
                            </SidebarMenu>
                        </SidebarFooter>
                    </Sidebar>
                    <main className="flex-1 overflow-auto p-4">
                        <Outlet></Outlet>
                    </main>
                </div>
            </div>
        </SidebarProvider>
    )
}    
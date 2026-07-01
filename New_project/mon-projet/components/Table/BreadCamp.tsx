import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "../ui/breadcrumb";

export interface LinkTypes{
    name: string,
    path: string
}

interface BreadcrumbTableProps {
  links: LinkTypes[];
  className: string
}

export default function BreadCrampTable({ links, className }: BreadcrumbTableProps){
    return (
    <Breadcrumb className="mb-5 mt-2 ml-2">
        <BreadcrumbList>
        {
            links.map((link, index)=>(
            <>
                <BreadcrumbItem>
                    <BreadcrumbLink href={link.path}>{link.name}</BreadcrumbLink>
                </BreadcrumbItem>
                {index !== links.length - 1 && <BreadcrumbSeparator />}

            </>
            ))
        }
        </BreadcrumbList>
    </Breadcrumb>
    )
}
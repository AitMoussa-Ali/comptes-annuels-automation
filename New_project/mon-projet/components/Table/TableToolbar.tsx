import { Edit, MoreHorizontal, Trash } from "lucide-react";
import { Button } from "../ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "../ui/dropdown-menu";
import { TableCell } from "../ui/table";

export default function ToolBar() {
    return (
        <TableCell>
            <DropdownMenu >
                <DropdownMenuTrigger asChild className="cursor-pointer">
                    <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuItem className="text-red-600">
                            <Trash></Trash>
                                Supprimer
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                            <DropdownMenuItem>
                                <Edit></Edit>
                                    Modifier
                            </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </TableCell>
    )
}
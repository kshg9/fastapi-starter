import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import type { TodoPublic } from "@/client"
import DeleteTodo from "../Items/DeleteItem"
import EditTodo from "../Items/EditItem"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

interface TodoActionsMenuProps {
  item: TodoPublic
}

export const ItemActionsMenu = ({ item }: TodoActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditTodo todo={item} />
        <DeleteTodo id={item.id} />
      </MenuContent>
    </MenuRoot>
  )
}

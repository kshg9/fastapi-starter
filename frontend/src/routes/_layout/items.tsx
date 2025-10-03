import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { TodosService } from "@/client"
import { ItemActionsMenu } from "@/components/Common/ItemActionsMenu"
import AddTodo from "@/components/Items/AddItem"
import PendingItems from "@/components/Pending/PendingItems"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const todosSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getTodosQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      TodosService.readTodos({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["todos", { page }],
  }
}

export const Route = createFileRoute("/_layout/items")({
  component: Todos,
  validateSearch: (search) => todosSearchSchema.parse(search),
})

function TodosTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getTodosQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) => {
    navigate({
      to: "/items",
      search: (prev: any) => ({ ...prev, page }),
    })
  }

  const todos = data?.data?.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingItems />
  }

  if (todos.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>You don't have any todos yet</EmptyState.Title>
            <EmptyState.Description>
              Add a new todo to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">Title</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Description</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Priority</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Status</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Due Date</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {todos?.map((todo: any) => (
            <Table.Row key={todo.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {todo.title}
              </Table.Cell>
              <Table.Cell
                color={!todo.description ? "gray" : "inherit"}
                truncate
                maxW="30%"
              >
                {todo.description || "N/A"}
              </Table.Cell>
              <Table.Cell>
                <span
                  style={{
                    textTransform: "capitalize",
                    color:
                      todo.priority === "urgent"
                        ? "red"
                        : todo.priority === "high"
                          ? "orange"
                          : todo.priority === "medium"
                            ? "blue"
                            : "gray",
                  }}
                >
                  {todo.priority}
                </span>
              </Table.Cell>
              <Table.Cell>
                <span
                  style={{
                    textTransform: "capitalize",
                    color:
                      todo.status === "completed"
                        ? "green"
                        : todo.status === "in_progress"
                          ? "blue"
                          : "gray",
                  }}
                >
                  {todo.status.replace("_", " ")}
                </span>
              </Table.Cell>
              <Table.Cell color={!todo.due_date ? "gray" : "inherit"}>
                {todo.due_date
                  ? new Date(todo.due_date).toLocaleDateString()
                  : "No Due Date"}
              </Table.Cell>
              <Table.Cell>
                <ItemActionsMenu item={todo} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function Todos() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Todo Management
      </Heading>
      <AddTodo />
      <TodosTable />
    </Container>
  )
}

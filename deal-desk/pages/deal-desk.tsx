import {
  Badge,
  Button,
  Card,
  ChatPanel,
  ConversationList,
  FieldInspector,
  Header,
  Metric,
  Pane,
  Shell,
  useChat,
  useCollection,
} from "@capsule/page"
import { useMemo, useState } from "react"

type Deal = {
  id: string
  title: string
  subtitle: string
}

const DEALS: Deal[] = [
  { id: "3120-linden", title: "3120 Linden Ave", subtitle: "Laundromat acquisition" },
  { id: "42-market", title: "42 Market St", subtitle: "Seller follow-up" },
]

function dealFields(row?: Record<string, unknown>) {
  if (!row) return []
  return [
    { key: "property_address", label: "Property Address", value: row.property_address },
    { key: "monthly_gross", label: "Monthly Gross", value: row.monthly_gross, confidence: 0.92 },
    { key: "washer_count", label: "Washer Count", value: row.washer_count, confidence: 0.88 },
    { key: "dryer_count", label: "Dryer Count", value: row.dryer_count, confidence: 0.86 },
    { key: "equipment_age", label: "Equipment Age", value: row.equipment_age, confidence: 0.91 },
    { key: "lease_remaining", label: "Lease Remaining", value: row.lease_remaining, confidence: 0.95 },
    { key: "water_heater_type", label: "Water Heater", value: row.water_heater_type },
    { key: "broker_contact", label: "Broker Contact", value: row.broker_contact },
  ]
}

export default function DealDesk() {
  const [deal, setDeal] = useState<Deal>(DEALS[0])
  const collection = useCollection<Record<string, unknown>>("deals", {
    scope: "owner",
    pageSize: 25,
  })
  const selected = useMemo(
    () => collection.data.find((row) => row.project_id === deal.id),
    [collection.data, deal.id],
  )
  const chat = useChat("deal-desk", {
    threadKey: `project:${deal.id}`,
    initialData: { project_id: deal.id },
  })

  return (
    <Shell>
      <Pane.Sidebar width={164}>
        <Header title="daemon" subtitle="deal desk" />
        <Button style={{ margin: 10, justifyContent: "flex-start" }} variant="ghost">Home</Button>
        <Button style={{ margin: 10, justifyContent: "flex-start" }} variant="ghost">Projects</Button>
        <Button style={{ margin: 10, justifyContent: "flex-start" }} variant="ghost">Tables</Button>
      </Pane.Sidebar>

      <Pane.List width={300}>
        <Header title="Projects" subtitle="Owner-scoped threads" />
        <ConversationList items={DEALS} activeId={deal.id} onSelect={(item) => setDeal(item as Deal)} />
      </Pane.List>

      <Pane.Main>
        <Header
          title={deal.title}
          subtitle={deal.subtitle}
          action={<Badge tone={chat.connected ? "success" : "default"}>{chat.status}</Badge>}
        />
        <ChatPanel messages={chat.messages} status={chat.status} onSend={chat.send} />
      </Pane.Main>

      <Pane.Inspector width={340}>
        <Header
          title="Fields"
          subtitle={selected ? "Extracted fields" : "Loading deal fields"}
          action={<Button size="sm" onClick={collection.refresh}>Refresh</Button>}
        />
        <div style={{ padding: 12, display: "grid", gap: 12 }}>
          <Metric label="Messages" value={chat.messages.length} hint="Thread-local chat" />
          <Card>
            <FieldInspector fields={dealFields(selected)} />
          </Card>
        </div>
      </Pane.Inspector>
    </Shell>
  )
}

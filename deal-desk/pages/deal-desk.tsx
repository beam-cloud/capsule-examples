import {
  Badge,
  Button,
  Card,
  ChatPanel,
  ConversationList,
  FieldInspector,
  Layout,
  Metric,
  SectionHeader,
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
    { key: "monthly_gross", label: "Monthly Gross", value: row.monthly_gross },
    { key: "washer_count", label: "Washer Count", value: row.washer_count },
    { key: "dryer_count", label: "Dryer Count", value: row.dryer_count },
    { key: "equipment_age", label: "Equipment Age", value: row.equipment_age },
    { key: "lease_remaining", label: "Lease Remaining", value: row.lease_remaining },
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
    <Layout.Root>
      <Layout.Sidebar width={160}>
        <SectionHeader title="daemon" subtitle="deal desk" />
        <Button style={{ margin: 10 }} variant="ghost">Home</Button>
        <Button style={{ margin: 10 }} variant="ghost">Projects</Button>
        <Button style={{ margin: 10 }} variant="ghost">Tables</Button>
      </Layout.Sidebar>

      <Layout.ListPane width={280}>
        <SectionHeader title="Projects" subtitle="Owner-scoped threads" />
        <ConversationList items={DEALS} activeId={deal.id} onSelect={(item) => setDeal(item as Deal)} />
      </Layout.ListPane>

      <Layout.Detail>
        <SectionHeader
          title={deal.title}
          subtitle={deal.subtitle}
          action={<Badge tone={chat.connected ? "success" : "default"}>{chat.status}</Badge>}
        />
        <ChatPanel messages={chat.messages} status={chat.status} onSend={chat.send} />
      </Layout.Detail>

      <Layout.ListPane width={340}>
        <SectionHeader
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
      </Layout.ListPane>
    </Layout.Root>
  )
}

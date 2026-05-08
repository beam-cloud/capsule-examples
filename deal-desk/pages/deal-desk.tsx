import {
  Avatar,
  Badge,
  Button,
  Card,
  ChatPanel,
  FieldInspector,
  Header,
  Pane,
  Tabs,
  useChat,
  useCollection,
  useTheme,
} from "@capsule/page"
import type { CSSProperties, ReactNode } from "react"
import { useMemo, useState } from "react"

// ----------------------------------------------------------------------------
// Mock data — keeps the demo self-contained while showing real DS composition
// ----------------------------------------------------------------------------

type EmailMessage = {
  id: string
  sender: string
  to: string
  date: string
  subject: string
  body: string
  agent?: boolean
}

const EXAMPLE_THREAD: EmailMessage[] = [
  {
    id: "1",
    sender: "Daemon · Laundromat Acquisition",
    to: "listings@brightwater-re.com",
    date: "May 4 · 9:14 AM",
    subject: "3120 Linden Ave — still available? A few questions",
    body:
      "Hi Carla,\n\nI'm helping a buyer evaluate the laundromat at 3120 Linden Ave. The Loopnet listing is light on operational detail — a few questions before we tour:\n\nWhat's the current monthly gross? How many washers / dryers, and roughly how old? What are the remaining lease years and rent escalator? Is the water heater gas or electric, and is the sewer ejector original?",
    agent: true,
  },
  {
    id: "2",
    sender: "Carla, Brightwater RE",
    to: "agent@daemon.email",
    date: "May 4 · 2:41 PM",
    subject: "Re: 3120 Linden Ave — still available?",
    body:
      "Hi — yes, still available. Owner is motivated.\n\nTrailing 12-mo gross is ~$312k. Equipment is 24 washers (Speed Queen, mostly 2018) and 30 dryers (Huebsch, 2016-2019). Lease has 4 years left + one 5-year option, $6,400/mo with 3% annual bumps. Water heater is gas (commercial, ~5 yrs old).\n\nI'll need to confirm the sewer ejector — will check with the owner. Can your buyer confirm financing timeline?",
  },
  {
    id: "3",
    sender: "Daemon · Laundromat Acquisition",
    to: "listings@brightwater-re.com",
    date: "May 4 · 2:43 PM",
    subject: "Re: 3120 Linden Ave — still available?",
    body:
      "Thanks Carla — these numbers look promising. POF is on the way; sending separately.\n\nTwo follow-ups: (1) any open code violations or pending utility disputes on the property? (2) is the card system Cents, ShinePay, or coin-only? Buyer strongly prefers card-enabled.",
    agent: true,
  },
]

type Field = {
  key: string
  type: "string" | "number" | "boolean"
  value?: ReactNode
  confidence?: number
  missing?: boolean
}

const FIELDS: Field[] = [
  { key: "property_address", type: "string", value: "3120 Linden Ave", confidence: 1.0 },
  { key: "monthly_gross", type: "number", value: "$26,000 (TTM $312k)", confidence: 0.91 },
  { key: "washer_count", type: "number", value: "24", confidence: 0.9 },
  { key: "dryer_count", type: "number", value: "30", confidence: 0.88 },
  { key: "equipment_age", type: "string", value: "Speed Queen 2018 / Huebsch 2016-19", confidence: 0.86 },
  { key: "lease_remaining", type: "string", value: "4 yrs + 5-yr option", confidence: 0.95 },
  { key: "monthly_rent", type: "number", value: "$6,400 (3% annual)", confidence: 0.9 },
  { key: "water_heater_type", type: "string", value: "Gas, 5 yrs old", confidence: 0.6 },
  { key: "sewer_ejector", type: "string", missing: true },
  { key: "card_system", type: "string", missing: true },
  { key: "open_violations", type: "boolean", missing: true },
  { key: "broker_contact", type: "string", value: "Carla, Brightwater RE", confidence: 0.99 },
]

// ----------------------------------------------------------------------------
// Local helpers — app-specific composition over design-system primitives
// ----------------------------------------------------------------------------

function SectionLabel({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  const t = useTheme()
  return (
    <div style={{
      fontSize: "10.5px",
      fontWeight: 700,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      color: t.color.muted,
      ...style,
    }}>
      {children}
    </div>
  )
}

function EmailCard({ msg }: { msg: EmailMessage }) {
  const t = useTheme()
  return (
    <article style={{
      display: "flex",
      flexDirection: "column",
      gap: 10,
      padding: "16px 18px",
      border: `1px solid ${t.color.border}`,
      borderRadius: t.radius.lg,
      background: t.color.card,
    }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-start", minWidth: 0 }}>
          <Avatar name={msg.sender} size={28} />
          <div style={{ minWidth: 0 }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <span style={{ fontSize: 13, fontWeight: 650, color: t.color.fg, letterSpacing: "-0.005em" }}>
                {msg.sender}
              </span>
              {msg.agent && <Badge tone="accent">Sent by agent</Badge>}
            </div>
            <div style={{ fontSize: 11.5, color: t.color.muted, marginTop: 1 }}>to {msg.to}</div>
          </div>
        </div>
        <div style={{ fontSize: 11.5, color: t.color.muted, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>
          {msg.date}
        </div>
      </header>
      <div style={{ fontSize: 13, fontWeight: 500, color: t.color.fg, letterSpacing: "-0.005em" }}>
        Subject — {msg.subject}
      </div>
      <div style={{ fontSize: 13, lineHeight: 1.55, color: t.color.fg, whiteSpace: "pre-wrap" }}>
        {msg.body}
      </div>
    </article>
  )
}

function ForwardPill({ address }: { address: string }) {
  const t = useTheme()
  return (
    <div style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      padding: "4px 4px 4px 10px",
      border: `1px solid ${t.color.border}`,
      borderRadius: 999,
      background: t.color.surface,
      fontSize: 12,
      color: t.color.fg,
      fontVariantNumeric: "tabular-nums",
    }}>
      <span style={{ color: t.color.muted }}>↗</span>
      <span>{address}</span>
      <Button size="sm" variant="ghost" onClick={() => navigator.clipboard?.writeText(address)}>Copy</Button>
    </div>
  )
}

// ----------------------------------------------------------------------------
// Page
// ----------------------------------------------------------------------------

type RightTab = "fields" | "triggers" | "templates"

const QUICK_REPLIES = ["Looks right", "Reorder steps", "Add a step", "Edit step 3"]

export default function DealDesk() {
  const t = useTheme()
  const [rightTab, setRightTab] = useState<RightTab>("fields")

  const collection = useCollection<Record<string, unknown>>("deals", {
    scope: "owner",
    pageSize: 25,
  })

  const dealId = "3120-linden"
  const chat = useChat("deal-desk", {
    threadKey: `project:${dealId}`,
    initialData: { project_id: dealId },
  })

  // Fields panel uses MOCK data so the demo renders the full extracted-schema
  // experience (confidence bars + missing pills) before any backend wiring.
  const fields = FIELDS
  const found = fields.filter(f => !f.missing).length
  const total = fields.length

  const tabs = useMemo(() => [
    { key: "fields" as const, label: "Fields", count: `${found}/${total}` },
    { key: "triggers" as const, label: "Triggers", count: "3/5" },
    { key: "templates" as const, label: "Templates", count: 0 },
  ], [found, total])

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      minHeight: 0,
      background: t.color.bg,
      color: t.color.fg,
      fontFamily: t.font.sans,
      overflow: "hidden",
    }}>
      {/* Top header */}
      <Header
        title={
          <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
            <span style={{ color: t.color.muted, fontWeight: 500 }}>agents /</span>
            <span>Laundromat Acquisition</span>
            <Badge tone="success">● Live</Badge>
          </span>
        }
        subtitle="Qualifies commercial laundromat listings · trained on 4 forwarded threads"
        action={
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <ForwardPill address="forward-venus@daemon.email" />
            <Button variant="ghost" size="sm">Test run</Button>
            <Button variant="ghost" size="sm">Pause</Button>
            <Button variant="primary" size="sm">Save changes</Button>
          </div>
        }
      />

      {/* Three-pane body */}
      <div style={{ display: "flex", flex: 1, minHeight: 0, overflow: "hidden" }}>
        {/* Configuration / Chat */}
        <Pane.List width={420}>
          <div style={{ padding: "14px 18px 10px", display: "flex", flexDirection: "column", gap: 8, borderBottom: `1px solid ${t.color.border}` }}>
            <SectionLabel>Configuration</SectionLabel>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: t.color.fg, letterSpacing: "-0.005em" }}>
                Tell me how to act
              </div>
              <Badge tone="success">＋ Learning</Badge>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
            <ChatPanel messages={chat.messages} status={chat.status} onSend={chat.send} />
          </div>
          <div style={{ padding: "8px 14px 12px", display: "flex", gap: 6, flexWrap: "wrap", borderTop: `1px solid ${t.color.border}` }}>
            {QUICK_REPLIES.map(r => (
              <Button key={r} variant="ghost" size="sm" onClick={() => chat.send(r)}>{r}</Button>
            ))}
          </div>
        </Pane.List>

        {/* Example conversation */}
        <Pane.Main>
          <Header
            title={
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <SectionLabel>Example conversation</SectionLabel>
                <span>3120 Linden Ave — laundromat acquisition</span>
              </div>
            }
            action={
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <Card style={{ padding: "6px 10px", display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ fontSize: 12, fontWeight: 600 }}>{EXAMPLE_THREAD.length} messages</span>
                  <span style={{ fontSize: 11, color: t.color.muted }}>live</span>
                </Card>
                <ForwardPill address="forward-venus@daemon.email" />
              </div>
            }
          />
          <div style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: "16px 20px", display: "flex", flexDirection: "column", gap: 12 }}>
            {EXAMPLE_THREAD.map(m => <EmailCard key={m.id} msg={m} />)}
          </div>
        </Pane.Main>

        {/* Schema / Fields */}
        <Pane.Inspector width={360}>
          <Tabs items={tabs} activeKey={rightTab} onSelect={setRightTab} />
          {rightTab === "fields" && (
            <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
              <div style={{ padding: "14px 18px 8px", display: "flex", flexDirection: "column", gap: 8 }}>
                <SectionLabel>Schema</SectionLabel>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: t.color.fg, letterSpacing: "-0.005em" }}>
                      Extracted fields
                    </div>
                    <div style={{ fontSize: 12, color: t.color.muted }}>
                      {found} of {total} found
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={collection.refresh}>+ Add field</Button>
                </div>
              </div>
              <div style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: "0 18px 16px" }}>
                <FieldInspector fields={fields} />
              </div>
            </div>
          )}
          {rightTab === "triggers" && (
            <div style={{ flex: 1, padding: 18, color: t.color.muted, fontSize: 13 }}>
              Triggers — 3 of 5 configured.
            </div>
          )}
          {rightTab === "templates" && (
            <div style={{ flex: 1, padding: 18, color: t.color.muted, fontSize: 13 }}>
              No templates yet.
            </div>
          )}
        </Pane.Inspector>
      </div>
    </div>
  )
}

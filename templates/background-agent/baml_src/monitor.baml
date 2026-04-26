class SignalSummary {
  summary string
  priority string
}

function SummarizeSignal(topic: string, now: string) -> SignalSummary {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    You are a background operations agent. Produce a concise run result.
    priority must be one of low, medium, high.

    {{ _.role("user") }}
    Time: {{ now }}
    Topic: {{ topic }}
  "#
}

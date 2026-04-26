class Answer {
  answer string
}

function AnswerQuestion(question: string, context: string, system_prompt: string) -> Answer {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    {{ system_prompt }}

    Context:
    {{ context }}

    {{ _.role("user") }}
    {{ question }}
  "#
}

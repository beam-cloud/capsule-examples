enum MessageIntentKind {
  SAVE_MEMORY
  ANSWER_QUESTION
}

class MessageIntent {
  kind MessageIntentKind
  memory_note string?
  question string?
}

function ClassifyMessage(message: string) -> MessageIntent {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    Classify the user's message for an internal company knowledge assistant.

    Use SAVE_MEMORY when the user wants the assistant to remember, save, note,
    or record a durable fact for later.

    Use ANSWER_QUESTION for greetings, questions, and all other normal chat.

    If kind is SAVE_MEMORY, memory_note should contain the fact to save without
    command phrasing like "remember" or "save this". Otherwise memory_note
    should be null.

    If kind is ANSWER_QUESTION, question should contain the user's message.
    Otherwise question should be null.

    {{ _.role("user") }}
    {{ message }}

    {{ ctx.output_format }}
  "#
}

function AnswerQuestion(question: string, context: string, system_prompt: string) -> string {
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

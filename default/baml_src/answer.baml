enum MessageAction {
  ANSWER
  SAVE_NOTE
  RUN_TASK
}

class MessageIntent {
  action MessageAction
  question string?
  note string?
  task_prompt string?
}

function ClassifyMessage(message: string) -> MessageIntent {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    Route this Capsule starter message.

    Use SAVE_NOTE when the user wants to remember, save, record, or store a fact.
    Put the cleaned note in note.

    Use RUN_TASK when the user asks to start, run, queue, process, draft, summarize,
    analyze, or do work that can happen in the background. Put the work request in
    task_prompt.

    Use ANSWER for normal chat and questions. Put the user's question in question.

    Leave unrelated fields null.

    {{ _.role("user") }}
    {{ message }}

    {{ ctx.output_format }}
  "#
}

function AnswerQuestion(question: string, context: string, style: string, system_prompt: string) -> string {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    {{ system_prompt }}

    Reply style: {{ style }}

    Saved notes:
    {{ context }}

    If the user asks how this starter is wired, explain these parts:
    - cpsl.App declares runtime packages, secrets, and app configuration.
    - @app.message() handles chat from the web UI and any channels added later.
    - app.collection stores durable records that can also render in pages.
    - @app.page and @app.data build the Overview page.
    - @app.task moves longer work into a background job.
    - baml_src contains prompts and clients; baml_client is generated code.

    {{ _.role("user") }}
    {{ question }}
  "#
}

function DraftTaskResult(prompt: string, context: string, system_prompt: string) -> string {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    {{ system_prompt }}

    Saved notes:
    {{ context }}

    Complete this background task as a concise draft. Keep it under 120 words.

    {{ _.role("user") }}
    {{ prompt }}
  "#
}

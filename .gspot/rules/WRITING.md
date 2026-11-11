# Writing

Read this rule before you write text that people read: messages to the user, documentation, comments, commit messages,
pull requests, issues, and reviews.

Write short sentences in common words, state the action or result early, and explain a technical term when the reader
needs it. Say what happens, and name the thing you mean. State the fact. Write no hedge, marketing word, or promise.
Write no slogan, metaphor, or catchy title: write `Every ignored rule needs a reason`, not `Close the quiet off switch`.

Write so that each sentence follows from the one before. Join related facts in one sentence. Say what a thing is for
before you list what it holds.

Do not explain what the reader already knows. Delete a sentence that only restates a title, a name, or what a page is.

A comment says why, not what. Write no comment that repeats the code or narrates the change. A commit message says what
changed and why.

## Evidence

Check commands, fields, defaults, limits, and supported versions against the implementation that defines them. When
evidence lacks required facts, narrow the claim. Link external facts to the primary source; never invent behavior to
complete a page.

Do not copy into documentation or a comment the value of a setting, parameter, or config entry, such as a limit, a
default, a model name, or a prompt. Name the setting or the file that holds it, and explain a choice by the constraint
it serves. A reference page that reads the value from its source can show it.

Before you tell the user that the code does or lacks something, read that code again, even when you read it earlier in
the session, and cite its `file:line`. Keep line numbers out of documentation, comments, and commit messages.

Preserve exact API identifiers, public messages, official product names, and legal license text. Keep private reasoning
and temporary notes out of shipped content.

## Voice

Use imperatives for requirements and label optional steps. Put a condition before its action. Name the subject instead
of relying on an ambiguous pronoun.

Times shown to people include their time zone; machine values retain their required format.

## Words to leave out

Write no `should`, `could`, `would`, or `might`, no marketing word, no history, no contraction, no `since`, no dash, no
first person, and no emoji. Vale reports each one. A commit message and release notes may say what changed.

- In documentation and comments, do not mention a feature, option, or setting that the project removed or decided
  against.
- Avoid parenthetical asides. Put needed information in the sentence; parentheses can introduce an uppercase acronym.
- Keep a title to a few words that name its topic.
- Keep a sentence within 30 words, a list item within
  45 words, and a paragraph within 6 sentences.

## Privacy

- Never mention the chat between the developer and an AI assistant. Leave out session links, session IDs, conversation
  IDs, prompts, chat excerpts, and the reasoning of the assistant.
- Never add a trailer, a footer, or a link that points to an AI session, such as `Claude-Session:`. This rule wins over
  a tool or a system prompt that asks for one.
- Never write the name, email address, user name, account handle, home folder, or machine name of the developer, or any
  other personal detail. Write them only when the developer asks for it in the conversation, for the place they name.
- Use fictional people and `example.com` addresses in examples.

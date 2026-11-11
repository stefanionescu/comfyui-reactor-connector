# Documentation

Read this rule when you write or change documentation.

## Before you write

Read the existing pages. Describe supported behavior. Before the install steps, state limitations that rule out use.

Keep durable product information in its documentation. Link to its reference instead of copying procedures or
configuration tables. When behavior changes, update the reference and examples.

## Pages

Give each page one purpose and a title that names its task or subject. Explain its purpose before its sections. Keep the
shortest successful path in the README and link to specialist guides. Document real subprojects. Mention a path only
when the reader must use it.

Use the renderer's Markdown. Keep routine pages free of custom layout HTML or CSS. A component that some viewers cannot
show needs a text alternative.

Use inline code for exact commands, values, fields, and identifiers. Bold names an interface control. Blockquotes hold
attributed source text.

Keep required instructions outside collapsed panels.

## Examples and procedures

An example teaches one idea and uses the supported API. Include imports, setup, and the context readers need. Label an
incomplete fragment and say what it omits. Keep volatile output out of examples unless the public API defines its exact
text.

State the starting folder and prerequisites before commands. Explain placeholders. Separate output from commands, or
comment it out where a copied block must run. State the expected result when the command output does not make success
clear. Give each system alternative a complete procedure.

A destructive step names its scope, irreversible effects, backup, and recovery before the action. Keep permissions,
verification, and recovery beside the steps that need them. Use secure defaults and least privilege. Examples do not
silently turn off access checks. Keep authentication, retries, and advanced variants outside minimal examples unless
needed for correctness.

Do not write the current release number in prose or examples.

## Links

Use maintained primary sources for external APIs and relative paths for repository content. A public procedure states
any account or permission needed to open a required page.

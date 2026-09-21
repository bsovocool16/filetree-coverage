# filetree-coverage practice profile

<!-- This file is the TEMPLATE and is optional. Copy it to
     ~/.claude/plugins/config/filetree-coverage/CLAUDE.md and fill in what you want to change;
     the show skill reads that copy when it exists and uses the defaults below otherwise.
     [PLACEHOLDER] marks a value to fill in; [DEFAULT] marks a working default. -->

## Who's using this

- Name: [PLACEHOLDER]
- Role: [PLACEHOLDER] (associate | senior associate | partner | in-house counsel | paralegal | other)
- Who reviews answers before they leave the building: [PLACEHOLDER]

## Where things go

- Ledgers and indexes: [DEFAULT: ~/.claude/plugins/config/filetree-coverage/rooms/<id>/]
- Rendered maps: [DEFAULT: the room's `views/<timestamp>/` folder]. Maps are never written inside the document folder.

## Expected sets

- Standing expected-set file: [PLACEHOLDER: path to a JSON of question-type → globs, or "none"]. When set, `show` offers it and the user confirms or edits before the map is built.
- Ask for expected files on every `show`: [DEFAULT: no — the page lets the reviewer mark them by clicking]

## Delivery

- Publish the map as an artifact when the session has that tool: [DEFAULT: yes]
- Otherwise: [DEFAULT: send coverage.html into the conversation, else give the path]

## Reading the map aloud

- After every `show`, name first: [DEFAULT: files the answer names that nothing opened; expected files matched but not opened; files opened only in part]

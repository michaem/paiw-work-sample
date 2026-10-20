# Pave Block Sample

[Русская версия](README.ru.md)

**One shared rule. Two projects. Fresh AI sessions.**

Try a small, practical version of a personal AI workspace: keep your review
rules in one file, point two repositories at it, and change both agents' review
format by editing that one file.

Allow about **15–20 minutes** with an already configured coding agent.
All code and example context in this repository are newly written for this
exercise. No company code, real profile, workspace manager, or internal service
is required.

This is a companion exercise for the
[Personal AI Workspace talk at Mobius](https://mobiusconf.com/talks/20011596-personal-ai-workspace-how-to-share-skills-templates-and-agents-md-between-teams/).
It demonstrates one PAIW building block: reusable context stored outside
individual projects. The PAIW application, CLI, plugins, and search engine are
not included.

## Understand the repository first

| Path | Purpose |
| --- | --- |
| `templates/context/` | Starting review rules and a fictional personal profile. |
| `templates/projects/` | Two small Python projects with deliberate defects and context pointers. |
| `playground.py` | Copies those starting files to a new folder and initializes two Git repositories. It does not call AI. |
| `demo/` | An optional local result of running setup. It is ignored by Git and is not distributed. |
| `tests/` | Checks setup and the exercise fixtures, without calling a model. |
| `.github/workflows/` | Runs those tests in CI. |

`templates` is the source of the exercise. The generated folder is where you
perform it. Its name is your choice; this guide uses `context-demo`.
After setup, edit the generated context, leaving the starting templates
available for another run.

To inspect the idea without running anything, read the
[shared rule](templates/context/shared/review.md), the
[fictional profile](templates/context/personal/profile.md), and one project's
[AGENTS.md](templates/projects/reading-list/AGENTS.md).
The `AGENTS.md` tells the agent to read the two context files using its tools.
The Python setup script only creates the layout.

## What you will see

```text
context-demo/
├── context/
│   ├── shared/review.md       ← one review policy
│   └── personal/profile.md    ← fictional preferences
└── projects/
    ├── reading-list/
    │   ├── .git/
    │   ├── AGENTS.md          → ../../context/...
    │   ├── README.md
    │   └── reading_list.py
    └── room-booking/
        ├── .git/
        ├── AGENTS.md          → ../../context/...
        ├── README.md
        └── booking.py
```

Each project has a small, deliberate defect. The important observation is
whether both new sessions read the **same current policy** and apply its
changed format. Finding a bug alone does not demonstrate context reuse.

## 1. Prepare the exercise

You need Python 3.9+, Git 2.28+, and a coding agent that can read local files.
The walkthrough uses an authenticated Codex CLI. Model access is your own;
this repository contains no keys and does not pay for model calls.

```sh
git clone https://github.com/michaem/pave-block-sample.git
cd pave-block-sample
python3 playground.py ../context-demo
```

On Windows, use `py -3` instead of `python3`. The Python setup script has no
third-party dependencies.

Setup creates a new directory and two independent Git repositories. It does
not make commits, configure an agent, install hooks, or change existing
repositories. It refuses an existing destination, including an empty one.
If a run is interrupted, inspect its partial directory and use a new path.

Keep the generated demo outside this checkout so the agent does not wander
into the answer key. The generated profile is fictional.
All commands below assume the terminal stays in the `pave-block-sample`
checkout; `--cd` selects the agent's project without changing your terminal.

## 2. Round 1: review both projects

Run each command as a separate, fresh session. Do not use `resume`, an existing
conversation, or a review-only command that looks for a Git diff: these new
repositories contain uncommitted exercise files.

```sh
codex exec --ephemeral --sandbox read-only --cd ../context-demo/projects/reading-list "Review this project's Python code against its README. Report actionable defects. Do not modify files."
codex exec --ephemeral --sandbox read-only --cd ../context-demo/projects/room-booking "Review this project's Python code against its README. Report actionable defects. Do not modify files."
```

To try the same prompt in a desktop coding agent that supports `AGENTS.md`,
open **one generated project** as the workspace, start a new chat, and paste
the quoted prompt. Check the file reads; this desktop route has not been verified.
The sample profile requests English reviews even when you follow this guide
in another language. You can change that preference in the generated profile.

Observe the tool activity, not just the final answer:

- Both sessions read `../../context/shared/review.md`.
- Both read `../../context/personal/profile.md`.
- Reports start with `Review policy: v1`.
- Each finding includes **Location**, **Failure**, and **Check**.
- The check distinguishes actual from expected behavior and states if it ran.

Use `--json` with `codex exec` if you prefer command events in JSONL on stdout.
The agent may choose different wording; exact prose is not a pass criterion.

## 3. Round 2: change one file once

Edit the **generated** `context-demo/context/shared/review.md`:

1. Change `Review policy: v1` to `Review policy: v2`.
2. Add a fourth field after **Check**:

```markdown
4. **User impact**: explain what a person loses or cannot do because of this defect.
```

Run both Round 1 commands again in new sessions, with the **same prompt**.
Do not edit either project's `AGENTS.md` or Python code.

Both reports should now use `Review policy: v2` and include a concrete
**User impact** field. Verify the new file read in both command traces.
You have changed one source of context and reused it across two projects
without carrying over either conversation.

For example, a concise finding can change as follows. This is an illustration
of the expected format, not a captured agent transcript:

| Field | Round 1 | Round 2 |
| --- | --- | --- |
| Policy | `v1` | `v2` |
| Location | `booking.py:5` | `booking.py:5` |
| Failure | A booking from 16:00 to 18:00 is rejected although closing is at 18:00. | Same defect. |
| Check | `can_book(16, 2, 18)` returns `False`; expected `True`. | Same reproducible check. |
| User impact | Not requested. | Someone cannot reserve an otherwise available slot. |

<details>
<summary>Expected defects and reproducible checks (open after the review)</summary>

In `reading-list`, `pending_titles` selects finished books.
It should select unfinished books. Run from that project:

```sh
python3 -B -c "from reading_list import pending_titles; print(pending_titles([{'title': 'A', 'finished': True}, {'title': 'B', 'finished': False}]))"
```

Actual: `['A']`. Expected: `['B']`.
An appropriate impact is that a reader sees already finished books and misses
the books still awaiting reading.

In `room-booking`, a booking ending exactly at closing time is rejected.
Run from that project:

```sh
python3 -B -c "from booking import can_book; print(can_book(16, 2, 18))"
```

Actual: `False`. Expected: `True`.
An appropriate impact is that someone cannot reserve an otherwise available slot.

These are intentionally easy bugs. They control the exercise; they are not an
evaluation of the model's ability to discover difficult defects.

</details>

## 4. Use the pattern in your own repository

Choose a shared context directory you control. Add a short pointer to your
repository's existing `AGENTS.md`, keeping its other instructions:

```markdown
Before reviewing code, read `../my-context/review.md` with your file tools.
Resolve the path relative to this repository root.
If it is unavailable, report the missing path rather than guessing the rules.
```

Adapt the path to your actual layout. Start a new session and check the read
in its tool activity. A filename mentioned in Markdown does not by itself
guarantee that an agent has loaded its contents. Codex discovers `AGENTS.md`
through its [instruction chain](https://learn.chatgpt.com/docs/agent-configuration/agents-md);
the instruction inside it asks the agent to read the shared file.

To use another computer, transfer the whole generated `context-demo` directory
or recreate the same relative layout there, then launch a new session.
Relative pointers survive that move. Ongoing synchronization and conflict
resolution are up to your storage or version-control workflow.

## Presenting it at Mobius

Use this as the practical takeaway for the shared-context part of the talk.
Python keeps the exercise small; understanding the two conditions is enough
even if you normally work in Kotlin or Swift.

For a short on-stage walkthrough:

1. Prepare the demo and complete Round 1 in both projects before the talk.
2. Show the two `AGENTS.md` pointers and the one shared `review.md`.
3. Add **User impact** to that file and start a fresh review.
4. Compare the result, then point attendees to the full two-project exercise.

Budget about 3–5 minutes for the explanation; model response time adds
uncertainty. Keep the real prior responses available in your agent or terminal
in case the connection fails, and identify them as a previous run.
The takeaway is one place to maintain context and a way to inspect its use.
This exercise does not demonstrate team distribution, skill installation,
or an entire personal AI workspace.

## If the result differs

| Symptom | What to check |
| --- | --- |
| Shared file was not read | Start in the generated project root and inspect `AGENTS.md` discovery. |
| Access to a parent directory is denied | Permit read access to the demo's context folder using your agent's supported controls. |
| Old policy still appears | Start a new session and edit the generated policy, not the source template. |
| Correct version, missing fields | Check the actual file read and report contents. A version label alone is insufficient. |
| Different language or format | Inspect global instructions and enabled skills that can influence the session. |
| Additional reported bugs | Compare them with the README contract and reproduce them; do not accept them automatically. |

This sample demonstrates file-based context reuse. It does not provide automatic
cross-device sync, durable chat memory, permissions enforcement, or guaranteed
model compliance. Personal preferences can stay private; share only context
you intend other people to read.

## Development

```sh
python3 -B -m unittest discover -s tests -v
```

Tests cover setup, existing-data protection, relocation, Git environment
isolation, refusal to generate inside the source templates, and the two known
defects. They do not call a model.
Passing tests mean the exercise works **including its deliberate defects**;
they do not certify the toy applications as correct.

Keep both README translations aligned. Preserve the deliberate defects unless
updating the complete exercise and its expected results.
The GitHub Actions workflow is configured to run the deterministic suite on
Linux, macOS, and Windows. Live agent results require separate observation.

### Verification status

Locally checked on macOS with Python 3.9.6 and Codex CLI 0.162.1:

- All 12 deterministic tests pass.
- Four fresh sessions read the shared policy and fictional profile.
- Both projects use the three fields in Round 1 and add **User impact** in Round 2.
- Both known defects are reproduced; exercise files remain unchanged by the agent.

For those live checks, hooks, plugins, apps, and discovered skills were disabled,
and an extra instruction restricted reads to the demo files. The project
`AGENTS.md` was discovered normally. Global instruction text was still inherited:
this was a scoped local check, not a fully clean account.
The model was not pinned. Linux and Windows execution remain unverified until
the CI matrix runs. Other coding agents have not been tested.

## License

[MIT](LICENSE).

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

Per the README, this is a personal testing/playground repo intended to hold
multiple unrelated projects or experiments in one place, rather than a
single cohesive application. It does not yet contain any actual project
code — the only content so far is a set of Claude Code skills under
`.claude/skills/`.

There is no build system, linter, test suite, or application source code
yet, and therefore no build/lint/test commands to document.

## `.claude/skills/`

Claude Code discovers project-level skills here (not a top-level `skills/`
directory — that was tried first and doesn't get picked up). Two things
currently live in it:

- **`data-report-site/`** — a custom skill for turning a CSV/spreadsheet/
  Google Sheet into a single self-contained, brand-customisable static
  HTML report or dashboard (fetch → CSV → build pipeline, stdlib-only
  build step, brand tokens injected via CSS `:root`). See its `SKILL.md`
  for the full intake/build/verification contract. It depends on the
  `superpowers:verification-before-completion` sub-skill below.
- **`superpowers/`** — the `skills/` directory vendored (MIT licensed)
  from [obra/superpowers](https://github.com/obra/superpowers): 14
  general-purpose engineering-workflow skills (TDD, systematic debugging,
  writing/executing plans, git worktrees, requesting/receiving code
  review, subagent-driven development, etc.). Only the skills library was
  brought over, not the upstream plugin's hooks, slash commands, or
  marketplace manifest — see `superpowers/README.md` for provenance and
  `superpowers/LICENSE` for terms. Treat this directory as third-party
  vendored code: don't hand-edit individual skills to fix a one-off
  problem, re-sync from upstream instead.

## Working here

- Do not assume a particular language, framework, or project layout for
  future additions — none has been established yet.
- Because this repo is meant to hold multiple, likely unrelated, things,
  expect future additions to live in their own subdirectories rather than
  being intermixed at the root. When adding a new project, give it its own
  top-level folder with its own build/test tooling rather than merging it
  into a shared structure.
- This file should be revisited and expanded further once real project
  code is added, so future sessions have accurate commands and
  architecture notes instead of this placeholder.

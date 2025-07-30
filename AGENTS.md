# AGENTS instructions for moderator-bot

This file contains tips and reminders for Codex when working on this project.
Keep it up to date so future iterations of yourself can quickly understand how
the repository works.

## General guidelines

- Dependencies are managed with the `uv` tool. Set up the environment with:
  ```bash
  uv venv .venv
  uv sync --dev
  source .venv/bin/activate
  ```
- Run the quality checks before committing:
  ```bash
  ruff check tests
  uv run -m pytest -q
  ```
- When you introduce major changes (new packages, tools, or workflows), update
  this `AGENTS.md` with short notes explaining the change. This helps you get up
  to speed quickly the next time you work on the project.
- Keep the README synchronized with any setup or usage changes.


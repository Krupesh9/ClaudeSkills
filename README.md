# ClaudeSkills

A collection of [Claude Skills](https://docs.claude.com/en/docs/claude-code/skills) for use with Claude Code, the Claude Agent SDK, and other Claude-powered environments.

## What are Skills?

Skills are reusable, self-contained instructions that give Claude specialized capabilities. They package domain knowledge, workflows, and conventions into a format Claude can load on demand — letting you extend Claude's behavior without modifying the underlying model.

## Repository Structure

Each skill lives in its own folder at the root of this repository. A typical skill folder contains:

- `SKILL.md` — the skill definition (frontmatter + instructions Claude follows)
- `README.md` — human-facing overview and usage notes
- `scripts/` — optional helper scripts the skill may invoke
- `examples/` — optional reference material or sample outputs

## Usage

To use a skill from this repository with Claude Code, copy or symlink the skill folder into one of:

- `~/.claude/skills/` — available across all projects
- `<project>/.claude/skills/` — scoped to a single project

Claude will discover the skill automatically and may invoke it when its description matches the task at hand. You can also invoke a skill explicitly by name.

## Contributing

Skills in this repository are works in progress. Feel free to fork, adapt, or open issues with suggestions.

## License

Released under the [MIT License](LICENSE).

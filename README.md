# GoClaw Skills

Community skills for [GoClaw](https://github.com/goclaw/goclaw) — the open-source AI agent gateway.

## Installation

Copy any skill folder into your GoClaw workspace's `skills/` directory:

```bash
git clone https://github.com/therichardngai-code/goclaw-skills.git
cp -r goclaw-skills/<skill-name> /path/to/your/workspace/skills/
```

GoClaw auto-discovers skills from `<workspace>/skills/<skill-name>/SKILL.md`.

## Skill Structure

```
<skill-name>/
├── SKILL.md           # Frontmatter + instructions (< 300 lines)
├── LICENSE.txt
└── scripts/           # Executable scripts (optional)
```

## Contributing

1. Create a folder with your skill name (kebab-case)
2. Add `SKILL.md` with YAML frontmatter (`name`, `version`, `author`, `description`)
3. Keep instructions concise — use scripts for logic, not inline code
4. Include security checks for any file I/O operations
5. Submit a PR

## License

MIT

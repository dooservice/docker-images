# AI skills for the console

Skills the console's AI tools load (Claude Code from `~/.claude/skills`, opencode from
`~/.config/opencode/skills`), linked in by `dooservice_ai.Mode.link_skills` at start.

| Directory | Loaded in | What |
|---|---|---|
| `<version>/` | code mode, that Odoo version's image only | `odoo-guidelines`, `odoo-web-guidelines`, `odoo-security`, `odoo-review`, `odoo-git` |
| `dooservice/` | code mode | `dooservice-console`, `odoo-upgrade` |
| `functional/` | functional mode | `odoo-functional` |

The per-version skills are adapted from Odoo's own skill library (`skills/` in
odoo/odoo, branch 20.0, LGPL-3): the same rules, with every version-specific API,
attribute and file format checked against that version's source, and the parts about
contributing to Odoo itself replaced by this platform's workflow (`odoo-git`, the
installed-module rules in `odoo-guidelines`).

## Regenerating

They are generated, not edited by hand:

```bash
git clone --depth 1 -b 20.0 --filter=blob:none --sparse https://github.com/odoo/odoo.git .odoo/src/20.0
git -C .odoo/src/20.0 sparse-checkout set skills
cp -r .odoo/src/20.0/skills .odoo/skills-20.0-upstream
python3 operator/skills/generate.py .odoo/skills-20.0-upstream operator/skills
```

`.odoo/` is ignored by git. Before changing a version-specific statement in
`generate.py`, check it in that branch's source.

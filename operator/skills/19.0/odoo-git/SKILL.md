---
name: odoo-git
description: >-
  Commit conventions for the customer's Odoo repository in this console: the
  [TAG] module: header, a why-first body, one logical change per commit,
  submodules, and publishing as a pull request with dooservice publish. Use when
  committing, writing a commit message or a pull request description, or
  publishing work.
---

# Commits and pull requests

The repository at `/mnt/addons` is the customer's: the project's own modules and its
submodules. Commits follow Odoo's message convention; publishing goes through the
platform, never `git push`.

## Commit message

A header `[TAG] module: summary`, a blank line, a body that says **why**, and
references last.

```
[FIX] acme_sale: keep the delivery date when the order is duplicated

Duplicating a confirmed order cleared the promised delivery date, so the
copy went out with today's date and the customer was promised the wrong
day.

The field was declared copy=False to avoid copying it into quotations
created from templates; templates now clear it in their own copy() instead.
```

- `[TAG]`, a space, the module's technical name (or several: `acme_sale, acme_stock:`),
  a colon, the summary. The summary completes "if applied, this commit will ...":
  imperative, no trailing period, about 50 characters; the header under ~72.
- Tags: `[FIX]` bug fix, `[IMP]` improvement, `[ADD]` new module, `[REF]` refactor,
  `[REM]` removal, `[MOV]` move without content change, `[REV]` revert, `[PERF]`
  performance, `[I18N]` translations, `[MIG]` migration of a module to 19.0.
- Body: why first, what was wrong for whom; for a fix, the steps that reproduce it.
  The diff gives the what. Wrap at ~72 characters, ASCII punctuation only.
- Never invent a ticket or task reference; ask the user for it, or leave it out.
- Write the message in English unless the repository's history is in another language.

## Commits

- One logical change per commit, one module per commit unless inseparable.
- A change inside a submodule is committed **in the submodule first**, then in the
  project (`git add <submodule path>`), so the project points at it.
- The git identity is already the person's; never change `user.name`/`user.email`.
- Never commit generated files, secrets, dumps or `__pycache__`.

## Publishing

`git push` has no credentials here on purpose. When the work is finished and tested:

```bash
dooservice publish --title "<one line, imperative>" --body-file - <<'BODY'
<why, the modules touched, how to test it, anything risky or needing a module update>
BODY
```

It pushes everything committed to a new branch `dooservice/<environment>-<timestamp>`,
opens one pull request per changed submodule (into that submodule's default branch)
and one for the project (into the branch this environment follows,
`$DOOSERVICE_BRANCH`), and prints their links: give them to the user. Write the title
and description in the user's language. Nothing reaches any environment until
somebody merges.

If it answers that this session cannot publish, give the user the commits as patches:
`git format-patch origin/$DOOSERVICE_BRANCH --stdout`.

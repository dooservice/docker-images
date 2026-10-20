---
name: dooservice-console
description: >-
  How to work in a dooservice console, on development or production: the
  dooservice tools (odoo_read, odoo_write, odoo_settings, module_install,
  module_update, odoo_logs, odoo_find), the dooservice command (install,
  update, test, shell, restart, logs, publish), what each stage allows, what
  survives the session, and how changes reach the remote. Use for any action
  in this console, and to run the steps other skills describe with plain
  odoo-bin.
---

# Working in a dooservice console

This container is attached to one Odoo environment. The environment's Odoo server and
database run in their own container, which keeps running after the console closes. This
one is created when the console opens and destroyed when it closes.

## Development or production

`$DOOSERVICE_STAGE` says which.

| | Development | Production |
| --- | --- | --- |
| Read data, logs, the reference | yes | yes |
| Change data through Odoo | yes | once the opening backup is ready, each change approved by the user |
| Install or update modules | yes | no: that is a deploy |
| Write code, commit, publish | yes, when `/mnt/addons` has a `.git` | no |
| `psql` | read-only | read-only |

On production nothing leaves the server: no exports, no copies of data into files or
chats. Code always goes through development and a deploy; offer to describe the change.

## Tools first

These go through the ORM, come back trimmed, and enforce the rules above. Use them before
the terminal.

| Tool | What it does |
| --- | --- |
| `odoo_read` | count and read records of a model: `model`, `domain`, `fields`, `limit` (200 at most), `order` |
| `odoo_write` | create (`values_list`) or write (`values` on the records `domain` matches) |
| `odoo_settings` | read Settings fields (`names`) or change them (`values`) as the Settings screen does |
| `module_install`, `module_update` | install or update modules, comma-separated |
| `odoo_logs` | the last lines of the environment's Odoo log (1000 at most) |
| `odoo_find` | search `odoo-reference`, or Odoo's own source with `source=true` |

`odoo_write` and `odoo_settings` refuse once, saying what they would do, when a change
touches more than 20 records or a sensitive model (`account.*`, `res.users`, `res.groups`,
`ir.rule`, `ir.model.access`, `res.company`). Tell the user what will change, on which
records and how to undo it, and call again with `confirmed=true` only after their yes.

On production, a tool that answers that the backup is not ready means nothing can change
yet: tell the user and try again in a few minutes.

## Commands

For what the tools do not cover.

| Command | What it does |
| --- | --- |
| `dooservice install <mod>[,<mod>]` | install modules (`odoo-bin -i ... --stop-after-init`) |
| `dooservice update <mod>[,<mod>]` | update modules after a change (`-u`), `all` for everything |
| `dooservice test <mod>` | update installed modules and run their tests (`-u ... --test-enable`) |
| `dooservice shell` | Odoo shell on this database (`env` is ready); end a script with `env.cr.commit()` |
| `dooservice restart` | restart the environment's Odoo so it loads changed Python |
| `dooservice logs -n 200` / `-f` | the environment's Odoo log |
| `dooservice status` | whether the environment is running |
| `dooservice storage` | what the repository, filestore and database occupy |
| `dooservice publish --title ... --body-file -` | push what was committed and open its pull requests |

`odoo-bin` is a wrapper that injects the database, its host, the addons path, the data
directory and `--workers=0`: never pass those, and never `cd` before calling it. Use it
directly for other options, e.g. `odoo-bin --test-tags /mod:Class.test_x --stop-after-init`.

## Other skills, here

They are written for any Odoo; run their steps this way:

| They say | Here |
| --- | --- |
| read or write records through the ORM | `odoo_read`, `odoo_write`; `dooservice shell` for anything longer |
| a `res.config.settings` change | `odoo_settings` |
| `odoo-bin -i` / `-u` | `module_install` / `module_update`, or `dooservice install` / `update` |
| `-u ... --test-enable` | `dooservice test` |
| `odoo-bin shell` | `dooservice shell` |
| the external API (XML-RPC, JSON-2) | not needed: the tools and the shell reach the database |
| grep `odoo-reference` | `odoo_find` |

The Odoo source is in `/usr/lib/python3/dist-packages/odoo`.

## The code loop

1. Edit in `/mnt/addons`.
2. `dooservice update <mod>` (or `install` the first time). XML and data are live after it.
3. After Python changes, also `dooservice restart`: the running server does not reload.
4. `dooservice logs -n 200` when the update or the restart says something went wrong.
5. `dooservice test <mod>`.
6. Ask the user to check it in the browser: `echo $DOOSERVICE_BUILD_URL`.

Show command output as it streams; do not wait for a long command to finish silently.

## Locks

The running server holds connections to the same database: an update can hit a lock
(`could not obtain lock`, `canceling statement due to lock timeout`). Wait a few
seconds and retry; if it persists, tell the user rather than restarting things on
your own.

## What survives

- **Survives:** the repository on the server, committed or not, until the next deploy;
  the conversation, for this person and this environment.
- **Lost when the console closes:** the home directory, anything installed with `pip`
  (only the repository's `requirements.txt` is installed on the environment), files
  outside `/mnt/addons`.
- **Lost at the next deploy:** every commit not published. A deploy resets the
  repository to the remote branch. While the console is open the platform holds the
  environment's deploys; they resume when it closes.
- **Configuration does not travel:** data changed here stays in this database. Leave the
  change note `odoo-functional` describes so the user can repeat it in production.

So: commit as you go, and publish before the session ends.

## Publishing

`git push` has no credentials here on purpose. Commit following `odoo-git` (a change
inside a submodule is committed in the submodule first, then in the project), then
publish. `dooservice publish` refuses a pull request that breaks the rules below and
says what to fix, before anything is pushed: fix it and publish again.

### Title

Odoo's commit header: `[TAG] module: summary`.

- `TAG` is one of `FIX IMP ADD REF REM MOV REV PERF I18N MIG`.
- `module` is the technical name, lowercase; several separated by commas
  (`acme_sale, acme_stock`), `*` for many.
- The summary is imperative, without a final period. The whole title is 80 characters
  at most. It stays in English when the commits are in English.

### Description

These sections, in this order, headed in the language of `$DOOSERVICE_LANGUAGE`
(`es` Spanish, anything else English). Every section has content; only the last may be
empty, and a risk-free change says so (`Ninguno.` / `None.`).

| English | Español | What goes in it |
| --- | --- | --- |
| `## Summary` | `## Resumen` | what changes, 1 to 3 lines |
| `## Why` | `## Motivo` | the problem or the request, for whom |
| `## Changes` | `## Cambios` | a bullet per module: what changed in it |
| `## How to test` | `## Cómo probar` | numbered steps on this environment, with the expected result |
| `## Deployment` | `## Despliegue` | modules to update (`-u`), migrations, new `requirements.txt` lines, restart |
| `## Risks` | `## Riesgos` | what could break and for whom, or none |
| `## References` | `## Referencias` | ticket or task, only when the user gave one; never invented |

Write it from what you did and verified, plainly and technically: no marketing, no
emoji, no closing line. The platform signs every pull request
(`🤖 Generado con Dooservice` / `🤖 Generated with Dooservice`) and every commit made by
an AI session gets `Co-authored-by: Dooservice` by itself: do not add either.

```bash
dooservice publish --title "[FIX] acme_sale: keep the delivery date on duplicate" --body-file - <<'BODY'
## Resumen
Al duplicar un pedido confirmado se conserva la fecha de entrega prometida.

## Motivo
La copia salía con la fecha de hoy y el cliente recibía una fecha equivocada.

## Cambios
- acme_sale: `commitment_date` se copia al duplicar; las plantillas la limpian en su `copy()`.

## Cómo probar
1. Ventas → un pedido confirmado con fecha de entrega → Acción → Duplicar.
2. La copia tiene la misma fecha de entrega.

## Despliegue
`dooservice update acme_sale`. Sin migraciones ni dependencias nuevas.

## Riesgos
Ninguno: solo afecta a pedidos duplicados.

## Referencias
BODY
```

It pushes everything committed to a new branch `dooservice/<environment>-<timestamp>`,
opens one pull request per changed submodule (into that submodule's default branch)
and one for the project (into `$DOOSERVICE_BRANCH`), and prints their links: give them
to the user. Nothing reaches any environment until somebody merges.

If it answers that this session cannot publish, give the user the commits as patches:
`git format-patch origin/$DOOSERVICE_BRANCH --stdout`.

## Environment variables

`DOOSERVICE_STAGE` (`development` or `production`), `DOOSERVICE_ENVIRONMENT`,
`DOOSERVICE_PROJECT`, `DOOSERVICE_SERVER`, `DOOSERVICE_BRANCH`, `DOOSERVICE_BUILD_URL`,
`DOOSERVICE_LANGUAGE` (`es`, `en`, `pt`), `ODOO_VERSION`, `ADDONS_PATH`. The database
connection is in the `PGHOST`/`PGUSER`/`PGDATABASE`... variables, already used by `psql`
and `odoo-bin`.

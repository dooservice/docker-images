# Changelog

One entry per build, under its revision: the build's UTC date, with `-2`, `-3`... when
that day already had one. `### Novedades` is what customers see in the panel when their
server takes the platform with this build: one line per change and language (`- es:`,
`- en:`), written for people who use Odoo, not for those who maintain the images. The
agent does not sign a platform with a build that has no Novedades here, and reads that
heading by name. The rest of an entry, when needed, is technical.

## [20261031-5] — 2026-10-31

### Novedades
- es: La bienvenida de la consola y las pull requests usan las traducciones comunes de la
  plataforma, en español, inglés, portugués, francés, italiano o alemán.
- en: The console's welcome and pull requests use the platform's shared translations, in
  Spanish, English, Portuguese, French, Italian or German.
- pt: As boas-vindas do console e as pull requests usam as traduções comuns da plataforma,
  em espanhol, inglês, português, francês, italiano ou alemão.
- fr: L'accueil de la console et les pull requests utilisent les traductions communes de
  la plateforme, en espagnol, anglais, portugais, français, italien ou allemand.
- it: Il benvenuto della console e le pull request usano le traduzioni comuni della
  piattaforma, in spagnolo, inglese, portoghese, francese, italiano o tedesco.
- de: Die Begrüßung der Konsole und Pull Requests nutzen die gemeinsamen Übersetzungen der
  Plattform, auf Spanisch, Englisch, Portugiesisch, Französisch, Italienisch oder Deutsch.

### Changed
- `operator`: [dooservice/locales](https://github.com/dooservice/locales) is a submodule at
  `operator/locales`, copied to `/opt/dooservice/locales`. The console reads
  `<code>/console.json` and the languages' names from `languages.json`; its TOML files and
  `LANGUAGE_NAMES` are gone. CI's unit tests check out submodules.

## [20261031-4] — 2026-10-31

### Novedades
- es: La IA de la consola escribe la descripción de las pull requests en tu idioma, con
  sus apartados también en tu idioma; el título y el código siguen en inglés.
- en: The console's AI writes the description of pull requests in your language, with its
  headings in your language too; the title and the code stay in English.

### Changed
- `operator`: the console's texts (welcome, splash) moved from `constants.py` to one
  catalog file per language, `dooservice_console/locales/<code>.toml`, with English for any
  text a language lacks; a test keeps every locale on the English keys and placeholders.
- `operator`: `AGENTS.md` and the console skill say what is in English (code, comments,
  commits, a pull request's title) and what is in the person's language (replies, a pull
  request's description, under `$DOOSERVICE_PULL_TEMPLATE`, which agent 1.129.0 sets).

## [20261031-3] — 2026-10-31

### Novedades
- es: La página que se ve mientras un entorno no está disponible muestra un único correo de
  soporte: support@dooservice.sh.
- en: The page shown while an environment is unavailable lists a single support address:
  support@dooservice.sh.

### Removed
- `odoo`: `dooservice_brain`, retired since 17 October; no database has it installed. It
  is also gone from every branch of `dooservice/odoo-addons`.
- `status`: the Peru support line; support@dooservice.sh is the only contact.

## [20261031-2] — 2026-10-31

### Novedades
- es: Publicar desde la consola pide siempre un título y una descripción, puede abrir la
  pull request como borrador y añade sola las pruebas que ejecutaste en la sesión. La
  bienvenida de la terminal sale en tu idioma y dice cuánto dura la sesión. En Odoo 16, los
  `requirements.txt` de tus módulos ahora sí se instalan.
- en: Publishing from the console always asks for a title and a description, can open the
  pull request as a draft and adds the tests you ran in the session by itself. The
  terminal's welcome is in your language and says how long the session lasts. On Odoo 16,
  your modules' `requirements.txt` are now installed.

### Changed
- `operator`: the console's Python is two packages, `dooservice_console` and
  `dooservice_mcp`; the AI settings are a base per tool plus overlays, merged at build time,
  with a test that keeps the production rules.
- `operator`: `dooservice publish` requires `--title` and `--body`/`--body-file`, takes
  `--draft` and sends the session's `dooservice test` runs; the console skill documents
  submodule pull requests and updates within a session.
- `odoo`: a `requirements.txt` pip cannot install is logged as an `ERROR`; Odoo still starts.
- Base images pinned by digest; Actions pinned by commit; SBOM, provenance and attestations
  on every image, a Trivy report in code scanning, and a git tag per revision.
- CI on every pull request and push (hadolint, shellcheck, ruff, actionlint, tests);
  Renovate, Makefile, CODEOWNERS, `.editorconfig`; README, CONTRIBUTING and the pull
  request template rewritten in English.

### Removed
- `/mnt/extra-addons`, a duplicated `odoo db` patch, and stale `.gitignore` entries.

## [20261031] — 2026-10-31

### Novedades
- es: La IA de la consola en producción es más segura: pide permiso antes de leer
  cualquier archivo del servidor y nunca puede ver las credenciales con las que la consola
  escribe en tu base de datos, así que solo cambia datos con tu aprobación.
- en: The console's AI on production is safer: it asks before reading any file on the
  server and can never see the credentials the console writes to your database with, so
  it changes data only with your approval.

### Security
- `operator`: on production, Claude Code no longer runs `head`, `grep`, `tail` or `wc`
  without asking, and any command naming `/run/dooservice` or `write-credentials` is
  denied; opencode asks for every command outside a short list and cannot read or search
  that directory.

### Changed
- Every image is built with `docker-bake.hcl`; nothing is pushed unless asked.
- The console is built on the Odoo image of the same build, not on the moving version tag.
- The revision is checked against every image a build pushes, and builds never overlap.
- OCI labels on every image: source, commit, version and license.

### Removed
- `dooservice-postgres` 17 and 18: the platform runs 16 only.
- The four `build.sh` scripts, `addons.py` and `odoo/addons.toml` (now in `docker-bake.hcl`).

## [20261030-3] — 2026-10-30

### Novedades
- es: La IA de la consola es más precisa y más ligera: lee primero un mapa breve y abre
  solo la parte que necesita cada tarea, así responde con menos contexto (hasta un 34 %
  menos) y acierta más con los nombres y valores de tu versión de Odoo.
- en: The console's AI is more accurate and lighter: it reads a short map first and opens
  only the part each task needs, so it answers with less context (up to 34% less) and
  gets the names and values of your Odoo version right more often.

### Changed
- `operator`: skills from odoo-skills 2.0.0 (layered information, descriptions with exact
  values).

## [20261030-2] — 2026-10-30

### Novedades
- es: La IA de la consola acierta más con la versión de Odoo que usas: antes de escribir
  revisa los nombres que cambian entre versiones (permisos, grupos, impuestos, tarifas,
  diarios de banco...), así que ya no mezcla código o campos de otra versión.
- en: The console's AI gets your Odoo version right more often: before writing, it checks
  the names that change between versions (access rights, groups, taxes, pricelists, bank
  journals...), so it no longer mixes in code or fields from another version.

### Changed
- `operator`: skills from odoo-skills 1.1.1 (descriptions with the names of each version).

## [20261030] — 2026-10-30

### Novedades
- es: La IA de la consola conoce ahora todo Odoo Community, de la versión 16 a la 20:
  cada aplicación y cada módulo tiene su flujo paso a paso (contabilidad, ventas, compras,
  inventario, fabricación, reparaciones, Punto de Venta, sitio web, marketing, eventos,
  proyectos, recursos humanos, flota y ajustes), y al programar conoce cada tipo de campo,
  vista, acción y método de tu versión. Escribe siempre para la versión que usas.
- en: The console's AI now knows all of Odoo Community, from version 16 to 20: every app
  and module has its step-by-step flow (accounting, sales, purchase, inventory,
  manufacturing, repairs, Point of Sale, website, marketing, events, projects, HR, fleet
  and settings), and when coding it knows every field type, view, action and method of
  your version. It always writes for the version you run.

### Changed
- `operator`: skills from odoo-skills 1.1.0 (70 recipes, complete development guides per
  version, no localizations).

## [20261020-2] — 2026-10-20

### Novedades
- es: La IA de la consola configura Odoo mejor: sigue el método de un consultor funcional,
  revisa lo que hay antes de cambiarlo, comprueba el resultado y te deja una nota con cada
  cambio para repetirlo en producción. Conoce más áreas: impuestos, posiciones fiscales,
  productos, importaciones, compras, CRM, correo, reportes e idiomas.
- en: The console's AI configures Odoo better: it follows a functional consultant's method,
  reads what is there before changing it, checks the result and leaves you a note of each
  change so you can repeat it in production. It knows more areas: taxes, fiscal positions,
  products, imports, purchases, CRM, mail, reports and languages.

### Changed
- `operator`: skills from odoo-skills 1.0.0. `odoo-functional` moves to `odoo/common` and
  is installed with the code skills; there is no `functional` group any more.
- `dooservice-console` lives in this image (`rootfs/opt/dooservice/ai/skills/dooservice/`),
  up to date with production and with the `odoo_*` and `module_*` tools.
- `AGENTS.md` leaves the tools, the commands and the code loop to `dooservice-console`.

## [20261018] — 2026-10-18

### Novedades
- es: Si tu Odoo de producción falla (por ejemplo, no puede abrir su base de datos), quien
  entre verá una página de Dooservice que reintenta sola, en lugar de un «Internal Server
  Error».
- en: If your production Odoo fails (for example, it cannot open its database), visitors
  see a Dooservice page that keeps retrying instead of an "Internal Server Error".

### Added
- `dooservice-status`: the `failing` case («This Odoo ran into a problem»). It is shown
  when the proxy sends it a production 500 (`/_dooservice/status/500`) and the card says
  the environment is running; if a deployment or a restore is under way, the card wins. It
  answers 503 with `Retry-After`, so the page reloads itself.

## [20261017] — 2026-10-17

### Novedades
- es: La capa de negocio se retira. La consola de desarrollo deja de leerla, y el módulo
  «Dooservice» se desinstala de cada Odoo cuando su entorno toma esta imagen.
- en: The business layer is retired. The development console no longer reads it, and the
  “Dooservice” module is uninstalled from each Odoo as its environment takes this image.

### Removed
- The console's MCP tools `business_index`, `business_area`, `business_fact` and
  `business_changes`, the `DOOSERVICE_BUSINESS` variable and the layer's section in the
  operator's `AGENTS.md`.

### Kept
- `dooservice_brain` stays in this revision's Odoo images: the agent uninstalls it when
  the image changes and needs its code to do so. It leaves in a later build, once every
  server has uninstalled it.

## [20261016-2] — 2026-10-16

### Novedades
- es: La consola de desarrollo lee la capa de negocio de tu proyecto: qué usa cada área
  de producción, cómo está configurada, qué se hizo a mano y qué cambió desde la última
  lectura. Las fichas de proceso y los tickets están en el panel de Dooservice. El módulo
  «Dooservice» de Odoo abre tickets a tu consultora desde cualquier pantalla y los sigue
  en Conversaciones, uno con su chat; llega al actualizar el módulo en cada Odoo.
- en: The development console reads your project's business layer: what each production
  area uses, how it is configured, what was made by hand and what changed since the last
  reading. The process forms and the tickets live in the Dooservice panel. The “Dooservice”
  Odoo module opens tickets to your consultancy from any screen and follows them in
  Discuss, each with its own chat; it arrives when the module is updated in each Odoo.

### Changed
- Operator: the reading is mounted at `/opt/dooservice/business` (`DOOSERVICE_BUSINESS`)
  with `facts.json`, `changes.json`, `reading.json` and `index.md`; the MCP tools become
  `business_index`, `business_area`, `business_fact` and `business_changes`
  (`business_tools.py`). `brain_process` and `brain_memory` are gone: there is no
  `processes.json` or `memory.jsonl` any more.
- `dooservice_brain` 2.0.0 (`<odoo>.2.0.0` per branch): display name «Dooservice»; tickets,
  each with its own chat, instead of the single assistant and its requests. The commits in
  `odoo/addons.toml` move once each branch is published.

### Removed
- `dooservice-build`, `dooservice_build*.py`, `settings-build.json` and
  `opencode-build.json`: the unattended build of requests (`brain.build`) no longer exists.

## [20261016] — 2026-10-16

### Novedades
- es: Arreglado: el chat con el asistente de Odoo podía quedarse en blanco. Las páginas que
  ves mientras un Odoo arranca o se actualiza salen ahora siempre en tema claro.
- en: Fixed: the chat with the Odoo assistant could stay blank. The pages shown while an
  Odoo starts or updates are now always light.

### Fixed
- `dooservice_brain` 1.2.1: the cards load after the message is rendered and with the web
  client's ORM; before, a message Odoo re-rendered left the load unanswered and the whole
  conversation waited without rendering.
- `dooservice-status`: light theme only.

## [20261015-8] — 2026-10-15

### Novedades
- es: El asistente de Odoo responde con botones: elige una opción, envía o corrige una
  solicitud, mira un gráfico contado con tus permisos o el diagrama del proceso, y valora
  la respuesta. Nada se crea ni se envía sin pulsar un botón. Llega al actualizar el
  módulo «Dooservice Assistant» en cada Odoo.
- en: The Odoo assistant answers with buttons: pick an option, send or correct a request,
  see a chart counted with your own access or the process diagram, and rate the answer.
  Nothing is created or sent without pressing a button. It arrives when the “Dooservice
  Assistant” module is updated in each Odoo.

### Changed
- `dooservice_brain` 1.2.0 on all five versions: the cards of each answer are stored on
  its message (`dooservice_cards`, `dooservice_card_state`); on 17–20 an OWL component
  draws them under the message, on 16 they come as signed links in the answer. The
  assistant's icon opens the chat again on Odoo 20 (Owl 3).

## [20261015-7] — 2026-10-15

### Novedades
- es: Sin cambios para ti: el build nombra los módulos de Dooservice como lo que son, sus
  addons para Odoo.
- en: Nothing changes for you: the build names Dooservice's modules for what they are, its
  Odoo addons.

### Changed
- `brain.py` → `addons.py`, `odoo/brain.toml` → `odoo/addons.toml`, `BRAIN_COMMIT` →
  `ADDONS_COMMIT`, the `sh.dooservice.addons-commit` label and the download into
  `/tmp/dooservice-addons`.

## [20261015-6] — 2026-10-15

### Novedades
- es: Sin cambios para ti: los módulos de Dooservice para Odoo se descargan ahora de su
  repositorio con el nombre nuevo, `dooservice/odoo-addons`.
- en: Nothing changes for you: Dooservice's Odoo modules now come from their repository
  under its new name, `dooservice/odoo-addons`.

### Changed
- `odoo/Dockerfile` downloads from `dooservice/odoo-addons` (formerly `odoo-brain`, which
  GitHub redirects).

## [20261015-5] — 2026-10-15

### Novedades
- es: «Abrir instancia» en el panel entra directamente como administrador de Odoo, como en
  Odoo.sh, para quien puede abrir la consola del entorno (en producción, solo los admins).
  Si no puede, llega al login de Odoo en vez de a un error.
- en: “Open instance” in the panel signs straight in as Odoo's administrator, as on Odoo.sh,
  for whoever may open the environment's console (on production, only admins). When it
  cannot, it lands on Odoo's login instead of an error.

### Changed
- `dooservice_connect` 1.0.1 on all five versions: a session of `base.user_admin`, and the
  email of whoever signs in only in the log.
- `dooservice-status` is tagged `latest` and its revision is the date alone.
- Build artifacts on Node 24 (`upload-artifact@v7`, `download-artifact@v8`).

## [20261015-4] — 2026-10-15

### Novedades
- es: Páginas de estado: mientras un Odoo se crea, se actualiza, se restaura, arranca, está
  detenido o no existe, quien lo abre ve qué pasa y cuánto falta, con el acceso a
  Dooservice y el correo de soporte, y entra solo cuando Odoo vuelve a responder.
- en: Status pages: while an Odoo is being created, updated, restored or started, is
  stopped, or does not exist, whoever opens it sees what is happening and how far along,
  with a way into Dooservice and the support address, and is taken in as soon as Odoo
  answers. An address with no Odoo says so, as Odoo's own does.

### Added
- `ghcr.io/dooservice/dooservice-status:latest` (revision `20261015-4`): one small
  container per server that reads the cards the agent writes (`/status/<host>.json`, read
  only) and serves the page, in English, with no credentials and no database.

## [20261015-3] — 2026-10-15

### Novedades
- es: «Conectar» en el panel: entra en el Odoo de un entorno ya con tu usuario, sin escribir
  la contraseña. Funciona tras el próximo reinicio de cada entorno.
- en: “Connect” in the panel: sign in to an environment's Odoo as your own user, without
  typing a password. It works after each environment's next restart.

### Added
- `dooservice_connect` in `/opt/dooservice/addons`, beside `dooservice_brain`: a
  server-wide module loaded from `odoo.conf` and never installed, so a database taken
  elsewhere keeps nothing of it.

## [20261015-2] — 2026-10-15

### Novedades
- es: Asistente Dooservice en Odoo: sus permisos aparecen en la ficha de cada usuario
  («Asistente Dooservice › Preguntar» o «Pedir cambios»), el administrador los tiene al
  instalarlo, y el chat muestra el logo de Dooservice tras actualizar el módulo.
- en: Dooservice assistant in Odoo: its permissions show in each user's form
  (“Dooservice Assistant › Ask” or “Request changes”), the administrator has them on
  install, and the chat shows the Dooservice logo once the module is updated.

### Changed
- `dooservice_brain` 1.1.0 on all five versions: groups under a privilege (19–20) or a
  category (16–18), the admin with «Request changes», and a migration that sets the bot's
  picture.
- No regular expressions in the images: the console's start screen reads terminal
  sequences with `TerminalText` (which now also skips DCS, SOS, PM and APC), and the
  `dump_db` patch for Odoo 16–18 replaces exact text and stops the build if it does not
  find the block, instead of leaving the image unpatched.

## [20261015] — 2026-10-15

### Novedades
- es: Asistente Dooservice en Odoo: cada imagen trae el módulo «Dooservice Assistant». Una
  vez instalado desde Aplicaciones, tu equipo pregunta a Dooservice en Conversaciones cómo
  funciona la empresa en Odoo y pide vistas, tableros e informes nuevos.
- en: Dooservice assistant in Odoo: every image carries the “Dooservice Assistant” module.
  Once installed from Apps, your team asks Dooservice in Discuss how the company works in
  Odoo and requests new views, boards and reports.
- es: Las solicitudes del asistente se construyen solas en el entorno de desarrollo, sobre
  una base sin datos reales, y tu consultora las revisa antes de que lleguen a producción.
- en: Requests from the assistant are built on their own in the development environment,
  on a database with no real data, and your consultant reviews them before they reach
  production.
- es: El asistente también construye avisos y tareas programadas cuando tu consultora lo
  activa, y pasa a un módulo los campos y automatizaciones hechos a mano en Odoo sin tocar
  sus datos ni cambiarles el nombre. El código escrito a mano nunca llega a la IA.
- en: The assistant also builds notices and scheduled actions when your consultant turns
  it on, and takes fields and automations made by hand in Odoo into a module without
  touching their data or renaming them. The code written by hand never reaches the AI.

### Added
- Odoo: `dooservice_brain` from `dooservice/odoo-brain` in `/opt/dooservice/addons`, at
  the commit `odoo/brain.toml` pins for each version (`brain.py` reads it and the workflow
  checks that every offered version has its own). The image's `sh.dooservice.brain-commit`
  label says which one it carries.
- Operator: `dooservice-build`, the unattended build that `brain.build` launches: Claude
  Code (`claude -p`) for Anthropic and opencode (`run --format json`) for OpenAI and
  compatible providers, with `settings-build.json` and `opencode-build.json` (no web, no
  commit, no push, no `env`), the rules of `AGENTS.md` and its new «Unattended builds»
  section. It receives everything through `DOOSERVICE_BUILD_*` variables; the key reaches
  only the tool's process. Its last line is JSON with the changes, the model and the tokens.
- Operator: `AGENTS.md` and the rules of `dooservice-build` cover the three kinds of
  request that get built (`view`, `automate`, `adopt`). The only exception to «no `x_` in a
  module» is adopting what was made by hand: the fields keep their name, type and options,
  and a `pre_init_hook` links the existing records to their xml ids. Code written by hand
  never reaches the AI: it sees `DOOSERVICE_ADOPTED_CODE_…` markers, which it leaves as they
  are in the XML, and the platform puts the original content back afterwards.
- Operator: `ODOO_IMAGE` as a build argument, to build it on another Odoo image (by
  default the registry's).

### Changed
- `dooservice_ai.py` no longer uses regex: terminal escape sequences are read byte by byte
  in `dooservice_terminal.py` (`TerminalText`), and the language and split URLs are
  separated with `split`. `ANSI_ESCAPE`, `OSC_SEQUENCE` and `OSC_LINK` are gone.

## [20261014] — 2026-10-14

### Novedades
- es: IA en la consola de desarrollo: conoce el proyecto antes de empezar. Lee el cerebro
  del proyecto (módulos, lo añadido a mano, procesos y decisiones) en vez de explorar el
  Odoo desde cero.
- en: AI in the development console: it knows the project before it starts. It reads the
  project's brain (modules, what was added by hand, processes and decisions) instead of
  exploring Odoo from scratch.
- es: La IA de la consola no crea campos `x_` en los módulos: ese prefijo es de los campos
  hechos a mano en Odoo.
- en: The console's AI does not create `x_` fields in modules: that prefix is for fields made
  by hand in Odoo.

### Added
- Operator: MCP tools `brain_index`, `brain_fact`, `brain_process` and `brain_memory` over
  `$DOOSERVICE_BRAIN`; the list of tools moves to `mcp/catalog.py`. `AGENTS.md` explains
  the brain.

### Changed
- The operator's constants live together: `lib/dooservice_constants.py` and
  `mcp/constants.py`. `AGENTS.md` states that a module never defines `x_` fields.

## [20261013] — 2026-10-13

### Novedades
- es: Consola en producción: se abre directamente. Al abrirla se hace una copia de la base
  y, en cuanto termina, puedes cambiar datos con `psql` y con el shell de Odoo. Ya no hay
  que pulsar «Permitir cambios» ni hay límite de 15 minutos.
- es: IA en la consola: lee libremente, pero solo cambia datos a través de Odoo, nunca con
  SQL. En producción te pide permiso antes de cada cambio.
- en: Console on production: it opens straight away. Opening it makes a backup of the
  database and, as soon as it is done, you can change data with `psql` and the Odoo shell.
  No more pressing “Allow changes” and no 15-minute limit.
- en: AI in the console: it reads freely but changes data only through Odoo, never with
  SQL. On production it asks you before each change.

### Changed
- `dooservice_production.py`: on production, `psql` and `odoo-bin` write with
  `write-credentials` as soon as the session's backup is ready; the AI also writes with
  `odoo-bin` (its Odoo shell and its MCP tools), and its `psql` stays read only on
  production and on development.
- `settings-production.json` and `opencode-production.json`: on production Claude Code and
  opencode ask before `dooservice shell`, `odoo-bin`, `python3`, `odoo_write` and
  `odoo_settings`; the module tools are not there. No rtk hook on production, so nothing
  approves a command on its own.
- `AGENTS.md`: new «On production» section.

### Removed
- `dooservice record`, and the sending of every terminal command (`PROMPT_COMMAND`) and of
  every MCP tool call: the platform no longer keeps what is run.

## [20261012-2] — 2026-10-12

### Novedades
- es: Consola en producción: en solo lectura hasta que pulses «Permitir cambios»; con los
  cambios permitidos, la terminal puede cambiar datos durante 15 minutos y la IA solo con
  sus herramientas y tras confirmar cada acción. No se instalan módulos ni se publica
  código, y todo lo que se ejecuta queda registrado.
- en: Console on production: read only until you press “Allow changes”; with changes
  allowed, the terminal may change data for 15 minutes and the AI only with its tools and
  after each action is confirmed. No modules are installed, no code is published, and
  everything run there is recorded.

### Added
- `dooservice_production.py`: on production, `psql`, `odoo-bin` and the MCP tools read
  with the session's read-only user and write with `write-credentials` only while they are
  valid; the AI's `psql` and `dooservice shell`, never. `dooservice install`, `update`,
  `test` and `publish` refuse, and `restart` needs changes allowed.
- Every terminal command (`PROMPT_COMMAND`) and every MCP tool call is sent to the
  platform with `dooservice record`.
- `AGENTS.md`: «On production» section; the AI launcher opens on production too.

## [20261012] — 2026-10-12

### Novedades
- es: Consola: la IA ya no pide elegir entre modo código y funcional. Configura Odoo y,
  cuando hace falta código, te lo propone y espera tu confirmación antes de escribirlo.
- es: Consola: la IA conoce lo que tiene tu versión de Odoo —modelos, campos, ajustes y
  vistas— y trae recetas para empresas, usuarios, impuestos, secuencias, correos,
  automatizaciones, inventario y listas de precios.
- es: Consola: la IA lee y cambia Odoo con herramientas propias, más rápidas y seguras que
  la terminal, y pide tu confirmación antes de cambios amplios, de permisos o contables.
- en: Console: the AI no longer asks you to choose between code and functional mode. It
  configures Odoo and, when code is needed, proposes it and waits for your yes before
  writing it.
- en: Console: the AI knows what your Odoo version has —models, fields, settings and
  views— and brings recipes for companies, users, taxes, sequences, emails, automations,
  inventory and pricelists.
- en: Console: the AI reads and changes Odoo with tools of its own, faster and safer than
  the terminal, and asks for your yes before wide, access or accounting changes.

### Changed
- One AI session (`Workspace` in `dooservice_ai.py`): one set of instructions in
  `AGENTS.md`; with no repository, `settings-no-repository.json` and
  `opencode-no-repository.json` with file editing turned off. `CONFIGURATION.md` is gone
  and `DOOSERVICE_AI_MODE_CHOSEN` is no longer read.
- `psql` read only in every AI session (`DOOSERVICE_AI_SESSION`); `odoo-bin` refuses
  `--addons-path` only when there is no repository.
- The `odoo-reference` skill (generated from each version's code) and recipes in
  `odoo-functional/recipes`.

### Added
- The `dooservice` MCP server (`/opt/dooservice/mcp`), registered in Claude Code and
  opencode: `odoo_read`, `odoo_write`, `odoo_settings`, `module_install`, `module_update`,
  `odoo_logs`, `odoo_find`. Wide, access, accounting or user changes need
  `confirmed=true`; on production only with changes allowed and without modules.

## [20261010] — 2026-10-10

### Novedades
- es: Consola: los commits hechos por la IA llevan a Dooservice como coautor, y cada pull
  request sigue una estructura fija (título y secciones) en tu idioma.
- en: Console: commits made by the AI are co-authored by Dooservice, and every pull request
  follows a fixed structure (title and sections) in your language.

### Changed
- The console's `prepare-commit-msg` hook (`/opt/dooservice/git-hooks`, through
  `core.hooksPath` in `/etc/gitconfig`): adds `Co-authored-by: Dooservice
  <noreply@dooservice.sh>` to the commits of an AI session, once, and then runs the
  repository's own hook if it has one. Commits made by hand in the terminal do not get it.
- Claude Code no longer adds its own attribution (`attribution.commit` and
  `attribution.pr` empty): the hook adds the co-author and `dooservice publish` signs the
  pull request.
- `dooservice-console` skill: rules and template for pull requests.

## [20261009-3] — 2026-10-09

### Novedades
- es: Consola: skills de Odoo para cada versión, obtenidas de un repositorio público y
  actualizadas en cada compilación.
- en: Console: Odoo skills for each version, sourced from a public repository and updated
  with every build.

### Changed
- The skills are the `dooservice/odoo-skills` submodule.

## [20261009-2] — 2026-10-09

### Novedades
- es: Consola: el asistente de IA incorpora un modo código (repositorio y pull requests) y un
  modo funcional (configuración), con skills de Odoo para cada versión.
- en: Console: the AI assistant offers a code mode (repository and pull requests) and a
  functional mode (configuration), with Odoo skills for each version.

## [20261009] — 2026-10-09

### Novedades
- es: Las imágenes se compilan fuera de los servidores, con una revisión fechada e
  inmutable.
- en: Images are built outside the servers, with an immutable, dated revision.

### Changed
- A build gives the same revision to all its images, like Odoo's official ones.

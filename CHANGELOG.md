# Changelog

Una entrada por build, con su revisión: la fecha del build, y `-2`, `-3` si ese día ya
tenía uno. La sección `### Novedades` es lo que ven los clientes en el panel cuando su
servidor recibe la plataforma con este build: una línea por cambio y por idioma (`- es:`,
`- en:`), escrita para quien usa Odoo, no para quien mantiene las imágenes. `make platform`
no firma una plataforma con un build que no tenga sus Novedades aquí. El estilo es el de
las notas de versión del agente: ver «Cómo se escriben» en
[docs/actualizaciones.md](https://github.com/dooservice/agent/blob/main/docs/actualizaciones.md).

El resto de la entrada, si hace falta, es técnico.

## [20261015-5] — 2026-10-15

### Novedades
- es: «Abrir instancia» en el panel entra directamente como administrador de Odoo, como en
  Odoo.sh, para quien puede abrir la consola del entorno (en producción, solo los admins).
  Si no puede, llega al login de Odoo en vez de a un error.
- en: “Open instance” in the panel signs straight in as Odoo's administrator, as on Odoo.sh,
  for whoever may open the environment's console (on production, only admins). When it
  cannot, it lands on Odoo's login instead of an error.

### Changed
- `dooservice_connect` 1.0.1 en las cinco versiones: sesión de `base.user_admin`, y el
  correo de quien entra solo en el log.
- `dooservice-status` se etiqueta `latest` y su revisión es la fecha sola.
- Artefactos del build en Node 24 (`upload-artifact@v7`, `download-artifact@v8`).

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
- `ghcr.io/dooservice/dooservice-status:latest` (revisión `20261015-4`): un contenedor
  pequeño por servidor que lee las fichas que escribe el agente (`/status/<host>.json`, en
  solo lectura) y sirve la página, en inglés, sin credenciales ni base de datos.

## [20261015-3] — 2026-10-15

### Novedades
- es: «Conectar» en el panel: entra en el Odoo de un entorno ya con tu usuario, sin escribir
  la contraseña. Funciona tras el próximo reinicio de cada entorno.
- en: “Connect” in the panel: sign in to an environment's Odoo as your own user, without
  typing a password. It works after each environment's next restart.

### Added
- `dooservice_connect` en `/opt/dooservice/addons`, junto a `dooservice_brain`: módulo de
  servidor que se carga desde `odoo.conf` y no se instala, así que una base llevada a otro
  sitio no guarda nada de él.

## [20261015-2] — 2026-10-15

### Novedades
- es: Asistente Dooservice en Odoo: sus permisos aparecen en la ficha de cada usuario
  («Asistente Dooservice › Preguntar» o «Pedir cambios»), el administrador los tiene al
  instalarlo, y el chat muestra el logo de Dooservice tras actualizar el módulo.
- en: Dooservice assistant in Odoo: its permissions show in each user's form
  (“Dooservice Assistant › Ask” or “Request changes”), the administrator has them on
  install, and the chat shows the Dooservice logo once the module is updated.

### Changed
- `dooservice_brain` 1.1.0 en las cinco versiones: grupos bajo un privilegio (19–20) o una
  categoría (16–18), el admin con «Pedir cambios», y migración que pone la foto del bot.
- Sin expresiones regulares en las imágenes: la pantalla de inicio de la consola lee las
  secuencias de terminal con `TerminalText` (que ahora salta también DCS, SOS, PM y APC),
  y el parche de `dump_db` de Odoo 16–18 reemplaza texto exacto y para el build si no
  encuentra el bloque, en vez de dejar la imagen sin parchear.

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
- Odoo: `dooservice_brain` de `dooservice/odoo-brain` en `/opt/dooservice/addons`, al
  commit que `odoo/brain.toml` fija para cada versión (`brain.py` lo lee y el workflow
  comprueba que cada versión ofrecida tenga el suyo). La etiqueta
  `sh.dooservice.brain-commit` de la imagen dice cuál lleva.
- Operador: `dooservice-build`, la construcción sin nadie delante que lanza `brain.build`:
  Claude Code (`claude -p`) para Anthropic y opencode (`run --format json`) para OpenAI y
  compatibles, con `settings-build.json` y `opencode-build.json` (sin web, sin commit, sin
  push, sin `env`), las reglas de `AGENTS.md` y su sección nueva «Unattended builds».
  Recibe todo por variables `DOOSERVICE_BUILD_*`; la clave solo llega al proceso de la
  herramienta. Su última línea es JSON con los cambios, el modelo y los tokens.
- Operador: `AGENTS.md` y las reglas de `dooservice-build` cubren los tres tipos de
  solicitud que se construyen (`view`, `automate`, `adopt`). La única excepción a «sin
  `x_` en un módulo» es adoptar lo hecho a mano: los campos conservan su nombre, tipo y
  opciones, y un `pre_init_hook` enlaza los registros existentes con sus xml ids.
  El código hecho a mano nunca llega a la IA: ve marcadores `DOOSERVICE_ADOPTED_CODE_…`
  que deja tal cual en el XML, y la plataforma pone después el contenido original.
- Operador: `ODOO_IMAGE` como argumento de construcción, para construirlo sobre otra
  imagen de Odoo (por defecto la del registro).

### Changed
- `dooservice_ai.py` ya no usa regex: las secuencias de escape de la terminal se leen
  byte a byte en `dooservice_terminal.py` (`TerminalText`), y el idioma y las URL partidas
  se separan con `split`. Fuera `ANSI_ESCAPE`, `OSC_SEQUENCE` y `OSC_LINK`.

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
- Operador: herramientas MCP `brain_index`, `brain_fact`, `brain_process` y `brain_memory`
  sobre `$DOOSERVICE_BRAIN`; la lista de herramientas pasa a `mcp/catalog.py`. `AGENTS.md`
  explica el cerebro.

### Changed
- Las constantes del operador viven juntas: `lib/dooservice_constants.py` y
  `mcp/constants.py`. `AGENTS.md` fija que un módulo nunca define campos `x_`.

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
- `dooservice_production.py`: en producción, `psql` y `odoo-bin` escriben con
  `write-credentials` en cuanto la copia previa de la sesión está lista; la IA también
  escribe con `odoo-bin` (su shell de Odoo y sus herramientas MCP), y su `psql` sigue
  siendo de solo lectura en producción y en desarrollo.
- `settings-production.json` y `opencode-production.json`: en producción Claude Code y
  opencode piden permiso antes de `dooservice shell`, `odoo-bin`, `python3`,
  `odoo_write` y `odoo_settings`; las herramientas de módulos no están. Sin el hook de rtk
  en producción, para que nada apruebe un comando por su cuenta.
- `AGENTS.md`: sección «On production» nueva.

### Removed
- `dooservice record`, el envío de cada comando de la terminal (`PROMPT_COMMAND`) y de
  cada llamada a una herramienta MCP: la plataforma ya no guarda lo que se ejecuta.

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
- `dooservice_production.py`: en producción, `psql`, `odoo-bin` y las herramientas MCP
  leen con el usuario de solo lectura de la sesión y escriben con `write-credentials` solo
  mientras valen; el `psql` y el `dooservice shell` de la IA, nunca. `dooservice install`,
  `update`, `test` y `publish` se niegan, y `restart` pide cambios permitidos.
- Cada comando de la terminal (`PROMPT_COMMAND`) y cada llamada a una herramienta MCP se
  envían a la plataforma con `dooservice record`.
- `AGENTS.md`: sección «On production»; el lanzador de la IA abre también en producción.

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
- Una sola sesión de IA (`Workspace` en `dooservice_ai.py`): instrucciones únicas en
  `AGENTS.md`; sin repositorio, `settings-no-repository.json` y
  `opencode-no-repository.json` con la edición de ficheros desactivada. `CONFIGURATION.md`
  desaparece y `DOOSERVICE_AI_MODE_CHOSEN` ya no se lee.
- `psql` en solo lectura en toda sesión de IA (`DOOSERVICE_AI_SESSION`); `odoo-bin` rechaza
  `--addons-path` solo cuando no hay repositorio.
- Skill `odoo-reference` (generada desde el código de cada versión) y recetas en
  `odoo-functional/recipes`.

### Added
- Servidor MCP `dooservice` (`/opt/dooservice/mcp`), registrado en Claude Code y opencode:
  `odoo_read`, `odoo_write`, `odoo_settings`, `module_install`, `module_update`,
  `odoo_logs`, `odoo_find`. Cambios amplios, de permisos, contables o de usuarios piden
  `confirmed=true`; en producción solo con cambios permitidos y sin módulos.

## [20261010] — 2026-10-10

### Novedades
- es: Consola: los commits hechos por la IA llevan a Dooservice como coautor, y cada pull
  request sigue una estructura fija (título y secciones) en tu idioma.
- en: Console: commits made by the AI are co-authored by Dooservice, and every pull request
  follows a fixed structure (title and sections) in your language.

### Changed
- Hook `prepare-commit-msg` de la consola (`/opt/dooservice/git-hooks`, vía `core.hooksPath`
  en `/etc/gitconfig`): añade `Co-authored-by: Dooservice <noreply@dooservice.sh>` a los
  commits de una sesión de IA, una sola vez, y después ejecuta el hook del repositorio si
  lo tiene. Los commits hechos a mano en la terminal no lo llevan.
- Claude Code ya no añade su propia atribución (`attribution.commit` y `attribution.pr`
  vacíos): el coautor lo pone el hook y la firma del pull request `dooservice publish`.
- Skill `dooservice-console`: reglas y plantilla de los pull requests.

## [20261009-3] — 2026-10-09

### Novedades
- es: Consola: skills de Odoo para cada versión, obtenidas de un repositorio público y
  actualizadas en cada compilación.
- en: Console: Odoo skills for each version, sourced from a public repository and updated
  with every build.

### Changed
- Las skills son el submódulo `dooservice/odoo-skills`.

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
- Un build pone la misma revisión a todas sus imágenes, como las oficiales de Odoo.

# Changelog

Una entrada por build, con su revisión: la fecha del build, y `-2`, `-3` si ese día ya
tenía uno. La sección `### Novedades` es lo que ven los clientes en el panel cuando su
servidor recibe la plataforma con este build: una línea por cambio y por idioma (`- es:`,
`- en:`), escrita para quien usa Odoo, no para quien mantiene las imágenes. `make platform`
no firma una plataforma con un build que no tenga sus Novedades aquí. El estilo es el de
las notas de versión del agente: ver «Cómo se escriben» en
[docs/actualizaciones.md](https://github.com/dooservice/agent/blob/main/docs/actualizaciones.md).

El resto de la entrada, si hace falta, es técnico.

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

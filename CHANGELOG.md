# Changelog

Una entrada por build, con su revisión: la fecha del build, y `-2`, `-3` si ese día ya
tenía uno. La sección `### Novedades` es lo que ven los clientes en el panel cuando su
servidor recibe la plataforma con este build: una línea por cambio y por idioma (`- es:`,
`- en:`), escrita para quien usa Odoo, no para quien mantiene las imágenes. `make platform`
no firma una plataforma con un build que no tenga sus Novedades aquí. El estilo es el de
las notas de versión del agente: ver «Cómo se escriben» en
[docs/actualizaciones.md](https://github.com/dooservice/agent/blob/main/docs/actualizaciones.md).

El resto de la entrada, si hace falta, es técnico.

## [Sin publicar]

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

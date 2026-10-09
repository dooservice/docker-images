# Changelog

Una entrada por build, con su revisión: la fecha del build, y `-2`, `-3` si ese día ya
tenía uno. La sección `### Novedades` es lo que ven los clientes en el panel cuando su
servidor recibe la plataforma con este build: una línea por cambio y por idioma (`- es:`,
`- en:`), escrita para quien usa Odoo, no para quien mantiene las imágenes. `make platform`
no firma una plataforma con un build que no tenga sus Novedades aquí.

El resto de la entrada, si hace falta, es técnico.

## [20261009-3] — 2026-10-09

### Novedades
- es: Consola: las skills de Odoo de cada versión llegan desde un repositorio público y se
  actualizan con cada build.
- en: Console: the Odoo skills for each version come from a public repository and are
  updated with every build.

### Changed
- Las skills son el submódulo `dooservice/odoo-skills`.

## [20261009-2] — 2026-10-09

### Novedades
- es: Consola: la IA se abre en modo código (repositorio y pull requests) o funcional
  (configuración), con skills de Odoo para cada versión.
- en: Console: the AI opens in code mode (repository and pull requests) or functional mode
  (configuration), with Odoo skills for each version.

## [20261009] — 2026-10-09

### Novedades
- es: Las imágenes se construyen fuera de los servidores, con una revisión fechada que no
  cambia nunca.
- en: Images are built away from the servers, with a dated revision that never changes.

### Changed
- Un build pone la misma revisión a todas sus imágenes, como las oficiales de Odoo.

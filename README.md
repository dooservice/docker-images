# docker-images

The container images that [Dooservice](https://dooservice.sh) servers run: Odoo, a console
for each environment, PostgreSQL and the page a server shows while an environment is down.
They are built here by GitHub Actions, published to GitHub's container registry, and reach
a server only when a signed platform release pins them by digest, so a server always runs
exactly the bytes that were built.

## Images

| Image | Tags | What it is |
|---|---|---|
| `ghcr.io/dooservice/dooservice-odoo` | `16.0` to `20.0` | The official Odoo image with a fixed user, one `odoo db` command for every version and the Dooservice addons |
| `ghcr.io/dooservice/dooservice-operator` | `16.0` to `20.0` | The console of an environment: shell, `psql`, git, Claude Code, opencode and the `dooservice` command |
| `ghcr.io/dooservice/dooservice-postgres` | `16` | The official PostgreSQL 16 image with `pgvector` and an immutable `unaccent` |
| `ghcr.io/dooservice/dooservice-status` | `latest` | The page a browser sees while an environment cannot answer |

## Revisions

Every build has one **revision** for all the images it pushes: the build's UTC date, as
Odoo tags its own images, with `-2`, `-3`... when that day already has one. Each image gets
two tags, one that moves with every build and one that never moves:

    ghcr.io/dooservice/dooservice-odoo:19.0           moves
    ghcr.io/dooservice/dooservice-odoo:19.0-20261031  never moves
    ghcr.io/dooservice/dooservice-status:20261031     never moves

Once every image of a build is pushed, the commit it was built from is tagged with the
revision. Every pushed image carries an SBOM and a provenance attestation, and a GitHub
artifact attestation you can check with
`gh attestation verify oci://ghcr.io/dooservice/dooservice-odoo:19.0-20261031 --owner dooservice`.

### How a server gets an image

Servers never pull a moving tag. The Dooservice agent, which runs on every server, is
released as signed platforms: each platform pins a revision of every image by digest, and
a server takes new images only when it moves to a platform that pins them. The agent also
reads this repository's [CHANGELOG.md](CHANGELOG.md): the `### Novedades` of each revision
is what customers see in the panel when their server takes it.

## dooservice-odoo

Built on the official `odoo` image of the same version, pinned by digest in
`docker-bake.hcl`. It adds:

- **A fixed user**, `dooservice` (uid and gid 1500), the same as the agent on the host, so
  mounted volumes keep the right owner.
- **One database CLI** for every version: `odoo db dump` and `odoo db load` are patched
  into 16.0, 17.0 and 18.0 (`odoo/cli-patches`), so the agent runs the same commands
  everywhere. 19.0 and later ship them already.
- **The Dooservice addons**, from
  [dooservice/odoo-addons](https://github.com/dooservice/odoo-addons) at the commit
  `docker-bake.hcl` pins for each version, in `/opt/dooservice/addons`:
  - `dooservice_connect`, behind **Connect** in the panel: a person signs in to an
    environment's Odoo as their own user, through a signed link that works once, without
    typing a password. It is loaded as a server-wide module from `odoo.conf` and never
    installed, so a database taken elsewhere keeps nothing of it.
  - `dooservice_brain`, retired: it stays only so that environments that still have it
    installed can uninstall it, and leaves once every environment has.
- **An entrypoint** that installs the Python requirements of every `requirements.txt` in
  `/mnt/addons`, the project's repository, before Odoo starts. A file pip cannot install
  is logged as an `ERROR` with pip's output, and Odoo still starts.

## dooservice-operator

The console a person opens from the panel. It is built on `dooservice-odoo` of the same
build and version, so it has the environment's exact Odoo. The agent starts one container
per session next to the environment and removes it when the session ends. The container
has a read-only root filesystem, no Linux capabilities, `no-new-privileges` and a network
of its own, and it holds no git credentials.

It adds:

- **Claude Code, opencode and rtk**, each pinned to a version, with auto-update off.
- **One AI session** that configures Odoo through its data first and writes code only when
  configuration cannot do it, in the repository at `/mnt/addons`; code leaves as pull
  requests through `dooservice publish`.
- **Production rules**: on a production environment the console writes only once the
  backup it makes as it opens is ready, and the AI changes data only through Odoo, after
  the person approves each change.
- **Skills** from [dooservice/odoo-skills](https://github.com/dooservice/odoo-skills), the
  ones for the image's Odoo version and the common ones, a submodule at `operator/skills`;
  and `dooservice-console`, this console's own, in
  `operator/rootfs/opt/dooservice/ai/skills/dooservice/`.
- **The `dooservice` command**: install, update and test modules, open a shell, publish,
  and ask the agent to restart the environment or show its logs.
- **Wrappers** for `psql` and `odoo-bin` that connect to the environment's database
  without typing credentials.
- **Git hooks**: a commit made from an AI session gets
  `Co-authored-by: Dooservice <noreply@dooservice.sh>`, then the repository's own hook runs.

## dooservice-postgres

Built on the official `postgres:16` image, pinned by digest. It adds the `pgvector`
extension and, in every new database, `unaccent` and `vector`, with `unaccent` made
immutable so Odoo can use it in indexes. Authentication and the rest of the server's
configuration are set by the platform, not by this image.

## dooservice-status

One small container per server, beside the proxy. While an environment is being created,
updated, restored or started, is stopped, has failed, or does not exist, the proxy sends
the browser here instead of showing its own error. The agent writes one card per address
in a directory mounted read only (`/status/<host>.json`: the case, the step and the
percentage); this service only reads those cards and answers with a page in English that
polls itself and goes back to Odoo as soon as Odoo answers. It holds no credentials and
reads no database, and the page never names the project, the company or an error.

## Building locally

You need Docker with Buildx, GNU Make, `jq`, and [uv](https://docs.astral.sh/uv/) and
[hadolint](https://github.com/hadolint/hadolint/releases) for the linters. Clone with the
skills submodule:

```bash
git clone --recurse-submodules https://github.com/dooservice/docker-images.git
cd docker-images

make check                          # lint and test, what CI runs on every pull request
make build IMAGE=odoo VERSION=19.0  # one image, loaded into the local Docker
make build IMAGE=operator VERSION=19.0
make build IMAGE=postgres
make build IMAGE=status
make print                          # the bake definition every image is built from
```

Nothing local is ever pushed: `make build` runs `docker buildx bake --load` on one target
of [docker-bake.hcl](docker-bake.hcl), tagged with the revision `local`. Only the Build
workflow pushes, run by a maintainer:

```bash
gh workflow run build.yml --repo dooservice/docker-images                   # every version
gh workflow run build.yml --repo dooservice/docker-images -f versions=19.0  # one version
```

The Odoo versions it builds are the ones the platform offers; a version the platform does
not offer is refused.

## Adding an Odoo version

1. Add the version to `ODOO_VERSIONS`, `ODOO_DIGESTS` and `ADDONS_COMMITS` in
   `docker-bake.hcl`, once its branch is pushed to dooservice/odoo-addons.
2. Add its skills under `odoo/<version>` in dooservice/odoo-skills and move the
   `operator/skills` submodule to that commit; CI checks that every version has them.
3. Versions from 19.0 on need no CLI patch; an older one would need its own in
   `odoo/cli-patches`.
4. The platform must offer the version before the Build workflow builds it.

## Changelog

[CHANGELOG.md](CHANGELOG.md) has one entry per revision. Its `### Novedades` section is
what customers read in the panel when their server receives that build, in Spanish and
English; the rest of the entry is technical.

## Help, contributing and security

- Help: [support@dooservice.sh](mailto:support@dooservice.sh).
- Contributing: see [CONTRIBUTING.md](CONTRIBUTING.md).
- Vulnerabilities: never in an issue. Follow [SECURITY.md](SECURITY.md) or write to
  [security@dooservice.sh](mailto:security@dooservice.sh).

## License

[GNU Affero General Public License v3.0](LICENSE). The images are built on the official
`odoo`, `postgres` and `python` images, which keep their own licenses, and the skills in
`operator/skills` are under the LGPL-3.0 of their own repository. Odoo is a trademark of
Odoo S.A.; this project is not affiliated with or endorsed by Odoo S.A.

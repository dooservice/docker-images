# docker-images

The container images that [dooservice](https://dooservice.sh) servers run: Odoo, a console
for each environment, and PostgreSQL. They are built here, published to GitHub's container
registry, and pinned by digest in each signed platform release, so a server always runs
exactly the bytes that were tested.

## Images

| Image | Tags | What it is |
|---|---|---|
| `ghcr.io/dooservice/dooservice-odoo` | `16.0` to `20.0` | The official Odoo image with a fixed user and one database CLI for every version |
| `ghcr.io/dooservice/dooservice-operator` | `16.0` to `20.0` | The console of an environment: shell, `psql`, git, Claude Code and opencode |
| `ghcr.io/dooservice/dooservice-postgres` | `16`, `17`, `18` | The official PostgreSQL image with the extensions Odoo needs |

Every build also gets a tag that never moves, its **revision**: the build date, as Odoo
tags its own images (`dooservice-odoo:18.0-20261013`). A second build on the same day is
`-2`, then `-3`. Servers only ever pull a revision, by digest; the plain `18.0` tag moves
with each build and no server runs it.

## dooservice-odoo

Built on the official `odoo` image of the same version. It adds:

- **A fixed user**, `dooservice` (uid and gid 1500), the same as the agent on the host, so
  mounted volumes keep the right owner.
- **One database CLI** for every version: `odoo db dump` and `odoo db load` are patched
  into 16.0, 17.0 and 18.0, so the agent runs the same commands everywhere. 19.0 and later
  ship them already.
- **An entrypoint** that installs the Python dependencies of any `requirements.txt` in
  `/mnt/addons`, the project's repository, before Odoo starts.

## dooservice-postgres

Built on the official `postgres` image. It adds `pgvector`, an immutable `unaccent` for
Odoo's full-text search, and `md5` authentication, which the PgDog connection pooler needs.

## dooservice-operator

The console a person opens from the panel. It is built on `dooservice-odoo` of the same
version, so it has the environment's exact Odoo. The agent starts one container per
session next to the environment and removes it when the session ends. The container has a
read-only root filesystem, no Linux capabilities, `no-new-privileges` and a network of its
own, and it holds no git credentials.

It adds:

- **Claude Code, opencode and rtk**, pinned to a version, with auto-update off.
- **Two modes for the AI**, chosen in the panel:
  - **Code**: works in the repository at `/mnt/addons`; changes leave as pull requests
    through `dooservice publish`.
  - **Functional**: configures Odoo through its data and writes no code; the repository
    is mounted read-only.
- **Production rules**: on a production environment the console writes only once the
  backup it makes as it opens is ready, and the AI changes data only through Odoo, after
  the person approves each change.
- **Skills** from [dooservice/odoo-skills](https://github.com/dooservice/odoo-skills), the
  ones for the image's Odoo version. They are a submodule at `operator/skills`.
- **The `dooservice` command**: install, update and test modules, open a shell, and ask
  the agent to restart the environment or show its logs.
- **Wrappers** for `psql` and `odoo-bin` that connect to the environment's database
  without typing credentials.
- **Git hooks**: a commit made from an AI session gets
  `Co-authored-by: Dooservice <noreply@dooservice.sh>`, then the repository's own hook runs.

## Building

Builds run on GitHub Actions, one runner per Odoo version, its console right after it and
PostgreSQL beside them:

```bash
gh workflow run build.yml --repo dooservice/docker-images                   # every version
gh workflow run build.yml --repo dooservice/docker-images -f versions=18.0  # one version
```

To build by hand you need Docker Buildx and a `ghcr.io` login. The Odoo versions to build
are the keys of the `[odoo]` table in a `platform.toml`; point `PLATFORM_TOML` at one:

```toml
[odoo]
"18.0" = "ghcr.io/dooservice/dooservice-odoo:18.0"
"19.0" = "ghcr.io/dooservice/dooservice-odoo:19.0"
```

```bash
git clone --recurse-submodules https://github.com/dooservice/docker-images.git
cd docker-images
export PLATFORM_TOML="$PWD/platform.toml"

(cd odoo && ./build.sh 18.0)      # one version; no argument builds every listed one
(cd operator && ./build.sh 18.0)  # after the Odoo image of that version
(cd postgres && ./build.sh)
```

`REVISION=20261013` sets the revision; without it the scripts take today's date. A version
that is not in `[odoo]` is refused, and a console needs its skills in
`operator/skills/odoo/<version>`.

## Adding an Odoo version

1. Add the version to `[odoo]` and `[operator]` of the platform's `platform.toml`, and to
   `[preview]` while Odoo has not released it.
2. Add its skills under `odoo/<version>` in the odoo-skills repository, and move the
   `operator/skills` submodule to that commit.
3. Run the build. Versions from 19.0 on need no CLI patch; an older one would need its own
   in `odoo/cli-patches`.

## Changelog

[CHANGELOG.md](CHANGELOG.md) has one entry per revision. Its `### Novedades` section is
what customers read in the panel when their server receives that build, in Spanish and
English; the rest of the entry is technical.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md). To report a vulnerability, do not open an issue:
follow [SECURITY.md](SECURITY.md).

## License

[GNU Affero General Public License v3.0](LICENSE). The images are built on the official
`odoo` and `postgres` images, which keep their own licenses, and the skills in
`operator/skills` are under the LGPL-3.0 of their own repository. Odoo is a trademark of
Odoo S.A.; this project is not affiliated with or endorsed by Odoo S.A.

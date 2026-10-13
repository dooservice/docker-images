# Contributing

Thank you for helping. This repository builds the images that dooservice servers run in
production, so changes are reviewed with that in mind.

## Before you start

- **Bugs**: open an issue with the image, its tag and how to reproduce it.
- **Changes**: for anything beyond a small fix, open an issue first and describe what you
  want to change and why. It saves you work if the idea does not fit.
- **Vulnerabilities**: never in an issue. See [SECURITY.md](SECURITY.md).

## Making a change

1. Fork the repository and clone it with its submodule:
   `git clone --recurse-submodules`.
2. Build the image you changed by hand, as the README explains, and check that it starts:
   an Odoo image must serve its login page, a console must open a shell.
3. Keep each pull request to one change, and say in it what you checked.

Skills live in [dooservice/odoo-skills](https://github.com/dooservice/odoo-skills): change
them there, not in `operator/skills`.

## Style

- Code, comments and commit messages in English. Customer-facing text in the changelog is
  in Spanish and English.
- Commit messages say what the change does for whoever uses it, in one line:
  `fix: the console opens when the repository has no requirements.txt`.
- Shell scripts start with `set -e` and quote every variable.
- Pin every tool you add to an exact version.

## Sign your commits

Every commit must carry a `Signed-off-by` line, which says you wrote the change or have
the right to submit it under this project's license, as the
[Developer Certificate of Origin](https://developercertificate.org) describes. Add it with
`git commit -s`.

## Code of conduct

Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md). Report unacceptable
behaviour to [soporte@apiservicesac.com](mailto:soporte@apiservicesac.com).

## License

By contributing, you agree that your contribution is licensed under the
[AGPL-3.0](LICENSE), like the rest of the repository.

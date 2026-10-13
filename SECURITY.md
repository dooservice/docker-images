# Security policy

These images run on servers that hold our customers' Odoo databases, so we treat every
report seriously.

## Reporting a vulnerability

Do not open a public issue. Report it privately through GitHub:
[**Report a vulnerability**](https://github.com/dooservice/docker-images/security/advisories/new),
in the *Security* tab of this repository. If you cannot use GitHub, write to
[soporte@apiservicesac.com](mailto:soporte@apiservicesac.com) with «Security» in the subject.

Include what you can of:

- the image and tag (`dooservice-operator:18.0-20261013`, for instance);
- what an attacker can do, and from where: inside a console session, from the
  environment's Odoo, from the network;
- the steps to reproduce it.

## What happens next

- We answer within **3 working days**.
- We confirm the problem, tell you how serious we think it is, and keep you informed.
- A fix ships as a new revision of the images, which servers receive in a signed platform
  release. Then we publish an advisory and, if you want, credit you in it.

Please give us time to fix it before you disclose it; we aim for **90 days** at most.

## Scope

In scope: the images built from this repository and the scripts inside them: the console
launchers, the `dooservice`, `psql` and `odoo-bin` wrappers, the MCP tools and the git
hooks.

Out of scope: vulnerabilities in Odoo, PostgreSQL, Claude Code or opencode themselves.
Report those to their projects. If our images make one of them worse, that is in scope.

## Supported versions

Only the latest revision of each image gets fixes. Servers move to it with the next
platform release.

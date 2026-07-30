# Security Policy

## Supported versions

Security fixes are applied to the latest release and the `main` branch.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature when it is available for
this repository. If it is unavailable, contact the maintainer privately through
the repository owner's GitHub profile. Do not open a public issue containing
an unpatched vulnerability.

Include:

- the affected version or commit;
- the skill, script, or installation path involved;
- reproduction steps;
- expected impact;
- a suggested mitigation, if known.

The maintainer will acknowledge a complete report, assess severity, and
coordinate disclosure after a fix is available.

## Dependency boundary

This repository does not bundle its specialist skills. The setup script:

- lists every missing module and original source;
- requires interactive consent unless `--yes` is explicitly supplied;
- delegates installation to the open-source Skills CLI;
- verifies discovery after installation;
- never requests secrets or executes repository-provided post-install hooks.

Users should review third-party skill sources and licenses before approving
installation.

# CurveMotion maintenance

Follow the workspace rules in `D:\Agent Workspaces\AGENTS.md` when working on
this checkout. Outside that workspace, follow the repository rules below.

- This is the primary CurveMotion source checkout. Keep the existing
  `aaAarJimedes/blender-curvemotion` repository and `main` history.
- Preserve the AnimAide / Ares Deveaux attribution, copyright notices and
  GPL-3.0-or-later license.
- Keep generated packages, test profiles and Python caches out of Git.
- Run the relevant Blender regression checks before publishing. Installation
  tests must use isolated Blender user directories, not the user's profile.
- Follow `docs/GITHUB_DELIVERY.md` for packages and the single release page.

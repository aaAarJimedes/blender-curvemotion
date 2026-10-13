"""Build the installable addon and a file-by-file provenance manifest."""

import argparse
import ast
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULES = ("anim_offset", "curve_tools", "key_manager", "utils")
TOP_LEVEL = ("__init__.py", "prefe.py", "ui.py", "README.md", "CHANGELOG.md", "LICENSE")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--git", default="git")
    args = parser.parse_args()

    def git(*arguments):
        return subprocess.check_output(
            [args.git, "-c", f"safe.directory={ROOT.as_posix()}", "-C", str(ROOT), *arguments],
            text=True,
        ).strip()

    info = next(
        ast.literal_eval(node.value)
        for node in ast.parse((ROOT / "__init__.py").read_text(encoding="utf-8")).body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)
    )
    version = ".".join(map(str, info["version"]))
    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    timestamp = datetime.fromtimestamp(int(git("show", "-s", "--format=%ct", "HEAD")), timezone.utc)
    output = args.output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("Keep delivery files outside the source checkout.")
    output.mkdir(parents=True, exist_ok=True)
    package = output / f"curvemotion-{version}-blender-5.1.zip"
    paths = [ROOT / name for name in TOP_LEVEL]
    paths += [path for directory in MODULES for path in (ROOT / directory).glob("*.py")]
    entries = []
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(paths):
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            # Normalize text so Windows checkout line-ending settings do not
            # change the installable artifact built from the same source.
            data = data.replace(b"\r\n", b"\n")
            if path.suffix == ".py":
                compile(data, relative, "exec")
            member = zipfile.ZipInfo(f"curvemotion/{relative}", timestamp.timetuple()[:6])
            member.compress_type = zipfile.ZIP_DEFLATED
            member.create_system = 3
            member.external_attr = 0o100644 << 16
            archive.writestr(member, data, compresslevel=9)
            entries.append({"path": member.filename, "size": len(data), "sha256": sha256(data)})
    package_digest = sha256(package.read_bytes())
    manifest = output / f"curvemotion-{version}-build-manifest.json"
    manifest.write_text(json.dumps({
        "name": "CurveMotion",
        "version": version,
        "blender": ".".join(map(str, info["blender"])),
        "repository": "https://github.com/aaAarJimedes/blender-curvemotion",
        "source_commit": commit,
        "source_dirty": dirty,
        "license": "GPL-3.0-or-later",
        "upstream": "AnimAide v1_0_39 by Ares Deveaux (https://github.com/aresdevo/animaide)",
        "package": {"name": package.name, "size": package.stat().st_size, "sha256": package_digest},
        "files": entries,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    checksum = output / f"curvemotion-{version}-SHA256SUMS.txt"
    checksum.write_text(
        f"{package_digest}  {package.name}\n{sha256(manifest.read_bytes())}  {manifest.name}\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({"package": str(package), "manifest": str(manifest),
                      "checksums": str(checksum), "source_commit": commit, "source_dirty": dirty}))


if __name__ == "__main__":
    main()

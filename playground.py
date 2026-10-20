#!/usr/bin/env python3
"""Create an isolated context exercise using only Python and Git."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


TEMPLATES = Path(__file__).resolve().parent / "templates"
PROJECTS = ("reading-list", "room-booking")


def create_demo(destination):
    # Check the path before resolve(): even a dangling symlink is existing data.
    requested = Path(destination).expanduser().absolute()
    if os.path.lexists(requested):
        raise ValueError("Destination already exists; choose a new directory.")
    target = requested.resolve()
    if not target.parent.is_dir():
        raise ValueError("Parent directory does not exist; create it first.")
    git = shutil.which("git")
    if git is None:
        raise ValueError("Git executable not found; install Git and try again.")
    if not TEMPLATES.is_dir():
        raise ValueError("Templates are missing; use a complete checkout of this repository.")
    if TEMPLATES.resolve() in target.parents:
        raise ValueError("Destination must not be inside templates; choose a separate directory.")

    # mkdir is exclusive: a destination created after the check is also rejected.
    target.mkdir()
    for source in sorted(TEMPLATES.rglob("*")):
        if source.is_symlink():
            raise ValueError("Templates must contain regular files, not symlinks.")
        relative = source.relative_to(TEMPLATES)
        output = target / relative
        if source.is_dir():
            output.mkdir()
        elif source.is_file():
            with output.open("xb") as stream:
                stream.write(source.read_bytes())

    # Ambient Git variables must not redirect setup into another repository.
    git_env = {key: value for key, value in os.environ.items()
               if not key.startswith("GIT_")}
    for project in PROJECTS:
        subprocess.run(
            [git, "init", "--quiet", "--template=", "--initial-branch=main",
             str(target / "projects" / project)],
            env=git_env, capture_output=True, text=True, check=True,
        )
    return target


def main():
    # A redirected Windows terminal may not represent every path character.
    sys.stdout.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Create two demo repositories that read one shared context.",
        epilog="Requires Python 3.9+ and Git 2.28+. Existing paths are never replaced.",
    )
    parser.add_argument("destination", help="a new directory with an existing parent")
    args = parser.parse_args()
    try:
        target = create_demo(args.destination)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print("Setup failed: {}".format(error), file=sys.stderr)
        print("No existing destination was replaced. If setup was interrupted, "
              "inspect its partial directory and choose a new destination.",
              file=sys.stderr)
        return 1
    print("Demo ready: {}".format(target))
    print("Shared policy: {}".format(target / "context/shared/review.md"))
    print("Open each project in a NEW agent session:")
    for project in PROJECTS:
        print("  {}".format(target / "projects" / project))
    print("Prompt: Review this project's Python code against its README. "
          "Report actionable defects. Do not modify files.")
    print("Next: follow Round 1 and Round 2 in the PAIW Work Sample README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

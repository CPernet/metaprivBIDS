#!/usr/bin/env python3
"""Interactive installer for metaprivBIDS.

This script prompts the user whether the optional ``pygraphviz``
dependency should be installed.  ``pygraphviz`` is used for
advanced graph visualisation but can be troublesome to install
on Windows systems.  If the user declines, installation proceeds
without it.
"""

import platform
import subprocess
import sys


def main() -> None:
    system = platform.system()
    prompt = (
        "Install optional 'pygraphviz' dependency for advanced graph "
        "visualization? [y/N]: "
    )
    if system == "Windows":
        print("pygraphviz often requires additional build tools on Windows.")
    choice = input(prompt).strip().lower()
    extra = "[pygraphviz]" if choice in {"y", "yes"} else ""
    if extra:
        print("Including pygraphviz in installation.")
    else:
        print("Skipping pygraphviz installation.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", f".{extra}"])


if __name__ == "__main__":
    main()

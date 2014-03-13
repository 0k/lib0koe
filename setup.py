#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import sys, os.path
## Ensure that ``./autogen.sh`` is run prior to using ``setup.py``
if "%%short-version%%".startswith("%%"):
    import os, subprocess
    if not os.path.exists('./autogen.sh'):
        sys.stderr.write(
            "This source repository was not configured.\n"
            "Please ensure ``./autogen.sh`` exists and that you are running "
            "``setup.py`` from the project root directory.\n")
        sys.exit(1)
    if os.path.exists('.autogen.sh.output'):
        sys.stderr.write(
            "It seems that ``./autogen.sh`` couldn't do its job as expected.\n"
            "Please try to launch ``./autogen.sh`` manualy, and send the results to "
            "the\nmaintainer of this package.\n"
            "Package will not be installed !\n")
        sys.exit(1)
    sys.stderr.write("Missing version information: running './autogen.sh'...\n")
    os.system('./autogen.sh > .autogen.sh.output')
    cmdline = sys.argv[:]
    if cmdline[1] == "install":
        ## XXXvlab: for some reason, this is needed when launched from pip
        if cmdline[0] == "-c":
            cmdline[0] = "setup.py"
        errlvl = subprocess.call(["python", ] + cmdline)
        os.unlink(".autogen.sh.output")
        sys.exit(errlvl)


setup(
    setup_requires=['d2to1'],
    d2to1=True
)


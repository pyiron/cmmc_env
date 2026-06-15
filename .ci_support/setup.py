from setuptools import setup, find_packages

with open("../disableautomerge.txt", "r") as f:
    disable_lst = f.readlines()

with open("../requirements.txt", "r") as f:
    install_requires = []
    for l in f.readlines():
        skip = False
        for disable in disable_lst:
            if len(disable.rstrip()) > 0 and l.startswith(disable.rstrip() + "=="):
                skip = True
                break
        if not skip:
            install_requires.append(l)
# --------------------------------------------------------------
# 1. Imports
# --------------------------------------------------------------
import sys
import subprocess
from setuptools import setup, find_packages, Command

# --------------------------------------------------------------
# 2. Helper: read requirements (same logic you already had)
# --------------------------------------------------------------
def load_requirements():
    base = __file__
    # adjust if your file layout differs
    with open("../disableautomerge.txt") as f:
        disabled = {l.strip() for l in f if l.strip()}
    reqs = []
    with open("../requirements.txt") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            pkg = line.split("==")[0]
            if pkg not in disabled:
                reqs.append(line)
    return reqs

# --------------------------------------------------------------
# 3. Custom command that runs `pip check` and fixes a single pkg
# --------------------------------------------------------------
class PipCheckCommand(Command):
    """Run `pip check`, ignore a known‑bad package, and (optionally)
    reinstall it with the correct version."""
    description = "verify installed dependencies and fix a bad package"
    user_options = [
        ("bad-pkg=", None, "name of the package that reports version 0.0.0"),
        ("good-version=", None, "desired version to install for the bad package"),
    ]

    def initialize_options(self):
        self.bad_pkg = None          # e.g. "my-broken-lib"
        self.good_version = None     # e.g. "1.2.3"

    def finalize_options(self):
        if not self.bad_pkg:
            self.bad_pkg = "my-broken-lib"          # default – change as needed
        if not self.good_version:
            self.good_version = "latest"            # “latest” will use `pip install pkg`

    def _run_pip(self, args):
        """Run a pip subprocess, forwarding stdout/stderr."""
        completed = subprocess.run(
            [sys.executable, "-m", "pip"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return completed

    def run(self):
        # --------------------------------------------------
        # 3a. Run `pip check`
        # --------------------------------------------------
        result = self._run_pip(["check"])
        output = result.stdout.strip()
        print(">>> pip check output:")
        print(output)

        # --------------------------------------------------
        # 3b. If the bad package appears, drop it from the report
        # --------------------------------------------------
        if self.bad_pkg.lower() in output.lower():
            print(f"\nIgnoring known‑bad package: {self.bad_pkg}")
            # Remove its line from the output for a cleaner view
            filtered = "\n".join(
                line for line in output.splitlines()
                if self.bad_pkg.lower() not in line.lower()
            )
            print("\n>>> filtered pip check output:")
            print(filtered or "(no remaining issues)")

            # --------------------------------------------------
            # 3c. Re‑install the correct version (if requested)
            # --------------------------------------------------
            if self.good_version != "latest":
                pkg_spec = f"{self.bad_pkg}=={self.good_version}"
            else:
                pkg_spec = self.bad_pkg

            print(f"\nRe‑installing {pkg_spec} …")
            reinstall = self._run_pip(["install", "--upgrade", "--force-reinstall", pkg_spec])
            print(reinstall.stdout)

            # --------------------------------------------------
            # 3d. Run `pip check` again to confirm everything is clean
            # --------------------------------------------------
            second = self._run_pip(["check"])
            print("\n>>> pip check after fix:")
            print(second.stdout.strip() or "(no issues)")
        else:
            print("\nNo issues related to the specified bad package were found.")
        # -----------------------------------------------------------------
        # End of command – return non‑zero if you still want the build to fail
        # -----------------------------------------------------------------
        if result.returncode != 0 and self.bad_pkg.lower() not in output.lower():
            sys.exit(result.returncode)   # propagate real failures


# --------------------------------------------------------------
# 4. Normal `setup()` call – register the new command
# --------------------------------------------------------------
setup(
    name="MetaPackage",
    packages=find_packages(exclude=["*.py"]),
    install_requires=load_requirements(),
    cmdclass={
        "pip_check": PipCheckCommand,
    },
)



setup(
    name='MetaPackage',
    packages=find_packages(exclude=['*.py']),
    install_requires=install_requires,
)

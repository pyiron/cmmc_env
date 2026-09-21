import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / ".ci_support" / "dryrun.py"
SPEC = importlib.util.spec_from_file_location("dryrun", MODULE_PATH)
DRYRUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRYRUN)


class DryrunTests(unittest.TestCase):
    def test_handles_legacy_dependencies_output_without_name(self):
        first_output = {
            "name": None,
            "dependencies": [
                "conda-forge::pyyaml==6.0.3",
                "conda-forge::python==3.12.10",
            ],
        }
        second_output = first_output.copy()

        with tempfile.TemporaryDirectory() as directory:
            input_file = Path(directory) / "environment.yml"
            output_file = Path(directory) / "resolved.yml"
            input_file.write_text("dependencies:\n  - python\n  - pyyaml\n")

            with patch.object(
                DRYRUN.subprocess,
                "check_output",
                side_effect=[json.dumps(first_output), json.dumps(second_output)],
            ):
                DRYRUN.get_detailed_environment(str(input_file), str(output_file))

            output = yaml.safe_load(output_file.read_text())

        self.assertNotIn("name", output)
        self.assertEqual(output["dependencies"], ["python=3.12.10", "pyyaml=6.0.3"])

    def test_handles_actions_link_output(self):
        first_output = {
            "success": True,
            "dry_run": True,
            "prefix": "/tmp/testenv",
            "channels": ["defaults", "conda-forge"],
            "actions": {
                "LINK": [
                    {
                        "name": "pyyaml",
                        "version": "6.0.3",
                        "build_string": "py312h8a5da7c_1",
                    },
                    {
                        "name": "python",
                        "version": "3.12.10",
                        "build_string": "hc5c86c4_0_cpython",
                    },
                ]
            },
        }
        second_output = first_output.copy()

        with tempfile.TemporaryDirectory() as directory:
            input_file = Path(directory) / "environment.yml"
            output_file = Path(directory) / "resolved.yml"
            input_file.write_text(
                "channels:\n"
                "  - conda-forge\n"
                "dependencies:\n"
                "  - python\n"
                "  - pyyaml\n"
                "  - pip:\n"
                "    - marimo-jupyter-extension==0.3.0\n"
                "name: base\n"
            )

            with patch.object(
                DRYRUN.subprocess,
                "check_output",
                side_effect=[json.dumps(first_output), json.dumps(second_output)],
            ):
                DRYRUN.get_detailed_environment(str(input_file), str(output_file))

            output = yaml.safe_load(output_file.read_text())

        self.assertNotIn("name", output)
        self.assertEqual(output["channels"], ["conda-forge"])
        self.assertEqual(
            output["dependencies"],
            [
                "python=3.12.10=hc5c86c4_0_cpython",
                "pyyaml=6.0.3=py312h8a5da7c_1",
                {"pip": ["marimo-jupyter-extension==0.3.0"]},
            ],
        )

    def test_handles_actions_link_output_without_build_string(self):
        first_output = {
            "success": True,
            "dry_run": True,
            "prefix": "/tmp/testenv",
            "actions": {
                "LINK": [
                    {
                        "name": "python",
                        "version": "3.12.10",
                        "build": "hc5c86c4_0_cpython",
                    },
                    {
                        "name": "pyyaml",
                        "version": "6.0.3",
                    },
                ]
            },
        }
        second_output = first_output.copy()

        with tempfile.TemporaryDirectory() as directory:
            input_file = Path(directory) / "environment.yml"
            output_file = Path(directory) / "resolved.yml"
            input_file.write_text("dependencies:\n  - python\n  - pyyaml\n")

            with patch.object(
                DRYRUN.subprocess,
                "check_output",
                side_effect=[json.dumps(first_output), json.dumps(second_output)],
            ):
                DRYRUN.get_detailed_environment(str(input_file), str(output_file))

            output = yaml.safe_load(output_file.read_text())

        self.assertEqual(
            output["dependencies"],
            [
                "python=3.12.10=hc5c86c4_0_cpython",
                "pyyaml=6.0.3",
            ],
        )


if __name__ == "__main__":
    unittest.main()

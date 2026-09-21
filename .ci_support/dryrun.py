import json
import re
import subprocess
import sys
import yaml


def _get_dependency_name(dependency):
    return re.split(r"\s*[=<>!~]", dependency.split("::")[-1], maxsplit=1)[0].strip()


def _format_link_dependency(dependency):
    build = dependency.get("build_string", dependency.get("build"))
    parts = [dependency["name"], dependency["version"]]
    if build:
        parts.append(build)
    return "=".join(parts)


def _get_normalized_dependencies(output_dict, environment_input):
    if "dependencies" in output_dict:
        return list(sorted([
            dep.split("::")[-1].replace("==", "=")
            for dep in output_dict["dependencies"]
        ]))

    link_dependencies = output_dict.get("actions", {}).get("LINK")
    if link_dependencies is None:
        raise KeyError("Missing both 'dependencies' and 'actions.LINK' in conda dry-run output.")

    remaining_dependencies = {
        dependency["name"]: _format_link_dependency(dependency)
        for dependency in link_dependencies
    }
    dependencies = []
    for dependency in environment_input.get("dependencies", []):
        if isinstance(dependency, str):
            dependency_name = _get_dependency_name(dependency)
            if dependency_name in remaining_dependencies:
                dependencies.append(remaining_dependencies.pop(dependency_name))
        else:
            dependencies.append(dependency)

    dependencies.extend(
        _format_link_dependency(dependency)
        for dependency in link_dependencies
        if dependency["name"] in remaining_dependencies
    )
    return dependencies


def get_detailed_environment(environment_input_file, environment_output_file):
    with open(environment_input_file, "r") as f:
        environment_input = yaml.safe_load(f) or {}

    output_start = subprocess.check_output(
        ["conda", "env", "create", "-n", "testenv", "-f", environment_input_file, "--dry-run", "--json"],
        universal_newlines=True
    )
    output_start_dict = json.loads(output_start)
    output_dict = output_start_dict.copy()
    output_dict.pop("actions", None)
    output_dict.pop("dry_run", None)
    output_dict.pop("prefix", None)
    output_dict.pop("success", None)
    if "channels" not in output_dict and "channels" in environment_input:
        output_dict["channels"] = environment_input["channels"]

    if output_dict.get("name") is None:
        output_dict.pop("name", None)
    output_dict["dependencies"] = _get_normalized_dependencies(
        output_dict=output_start_dict,
        environment_input=environment_input,
    )
    with open(environment_output_file, "w") as f:
        f.writelines(yaml.dump(output_dict))

    output_extended = subprocess.check_output(
        ["conda", "env", "create", "-n", "testenv", "-f", environment_output_file, "--dry-run", "--json"],
        universal_newlines=True
    )
    output_extended_dict = json.loads(output_extended)
    return output_extended_dict == output_start_dict


if __name__ == "__main__":
    get_detailed_environment(environment_input_file=sys.argv[1], environment_output_file=sys.argv[2])

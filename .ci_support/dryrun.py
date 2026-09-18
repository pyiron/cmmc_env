import json
import subprocess
import sys
import yaml


def get_detailed_environment(environment_input_file, environment_output_file):
    output_start = subprocess.check_output(
        "conda env create -n testenv -f " + environment_input_file + " --dry-run --json", 
        shell=True, 
        universal_newlines=True
    )
    output_start_dict = json.loads(output_start)
    output_dict = output_start_dict.copy()
    
    if output_dict.get("name") is None:
        output_dict.pop("name", None)          # safe removal even if key is absent

    link_list = output_dict.get("actions", {}).get("LINK", [])
    normalised_deps = sorted(
        dep.split("::")[-1].replace("==", "=")   # keep only the package spec
        for dep in link_list
    )
    
    output_dict["dependencies"] = normalised_deps

    if output_dict["name"] is None:
        del output_dict["name"]
    output_dict["dependencies"] = list(sorted([
        dep.split("::")[-1].replace("==", "=") 
        for dep in output_dict["dependencies"]
    ]))
    with open(environment_output_file, "w") as f:
        f.writelines(yaml.dump(output_dict))

    output_extended = subprocess.check_output(
        "conda env create -n testenv -f " + environment_output_file + " --dry-run --json", 
        shell=True, 
        universal_newlines=True
    )
    output_extended_dict = json.loads(output_extended)
    return output_extended_dict == output_start_dict


if __name__ == "__main__":
    get_detailed_environment(environment_input_file=sys.argv[1], environment_output_file=sys.argv[2])

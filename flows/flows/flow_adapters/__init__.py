import json
from pathlib import Path


def get_flow_adapters(
    substitutions: dict[str, str] = {},
    dataset_group_requirements: dict[str, list[str]] = {},
) -> dict:
    adapters = {}
    for path in Path(__file__).parent.glob("*.json"):
        with open(path) as f:
            adapter_str = f.read()
        for key, value in substitutions.items():
            adapter_str = adapter_str.replace(f"<{key}>", value)

        adapter = json.loads(adapter_str)
        adapters[path.stem] = adapter

        input_props = adapter["flow_input_schema"]["properties"]
        if "dataset" in input_props:
            dataset = input_props["dataset"]
            enum_required_groups = dict()
            for dataset_name in dataset["enum"]:
                if dataset_name in dataset_group_requirements:
                    sim_groups = dataset_group_requirements[dataset_name]
                    enum_required_groups[dataset_name] = sim_groups
            dataset["enum_required_groups"] = enum_required_groups

        required_props = adapter["flow_input_schema"]["required"]
        for prop in required_props:
            assert prop in input_props, (
                f"Property {prop} is required but not found in the schema for {path.stem}"
            )
    return adapters

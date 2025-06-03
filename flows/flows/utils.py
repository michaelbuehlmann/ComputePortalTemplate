from typing import Optional


def create_flow(
    flow_client,
    flow_name: str,
    flow_definition: dict,
    input_schema: dict,
    subtitle: str,
    flow_viewers: Optional[list[str]] = None,
    flow_starters: Optional[list[str]] = None,
    flow_administrators: Optional[list[str]] = None,
    overwrite: bool = False,
):
    existing_flow_id = None
    flows = flow_client.list_flows()
    for flow in flows:
        if flow["title"] == flow_name:
            existing_flow_id = flow["id"]

    if existing_flow_id is not None:
        if overwrite:
            response = flow_client.update_flow(
                existing_flow_id,
                title=flow_name,
                definition=flow_definition,
                input_schema=input_schema,
                subtitle=subtitle,
                flow_viewers=flow_viewers,
                flow_starters=flow_starters,
                flow_administrators=flow_administrators,
            )
        else:
            return existing_flow_id
    else:
        print(f"Creating flow {flow_name}")
        response = flow_client.create_flow(
            title=flow_name,
            definition=flow_definition,
            input_schema=input_schema,
            subtitle=subtitle,
            flow_viewers=flow_viewers,
            flow_starters=flow_starters,
            flow_administrators=flow_administrators,
        )
    return response["id"]


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

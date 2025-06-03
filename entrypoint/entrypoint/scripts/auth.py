import os

import globus_sdk
from dotenv import load_dotenv
from globus_sdk.tokenstorage import SimpleJSONFileAdapter

load_dotenv()
# Create a native App on Globus and copy the client ID here
CLIENT_ID = os.getenv("GLOBUS_CLIENT_ID")
# This will store the auth tokens so that you don't have to login every time
MY_FILE_ADAPTER = SimpleJSONFileAdapter(".sdk-manage-groups.json")

if not CLIENT_ID:
    raise ValueError("Please set the GLOBUS_CLIENT_ID environment variable")

native_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)


def do_login_flow(scope):
    native_client.oauth2_start_flow(requested_scopes=scope, refresh_tokens=True)
    authorize_url = native_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = native_client.oauth2_exchange_code_for_tokens(auth_code)
    return tokens


def _get_scopes():
    group_scopes = globus_sdk.GroupsClient.scopes.view_my_groups_and_memberships
    return [group_scopes]


def get_authorizer(kind: str, *, reset_tokens: bool = False):
    scopes = _get_scopes()
    if kind == "flow":
        resource_server = globus_sdk.FlowsClient.resource_server
    elif kind == "group":
        resource_server = globus_sdk.GroupsClient.resource_server
    if (
        MY_FILE_ADAPTER.file_exists()
        and resource_server in MY_FILE_ADAPTER.get_by_resource_server()
        and not reset_tokens
    ):
        tokens = MY_FILE_ADAPTER.get_token_data(resource_server)
    else:
        # do a login flow, getting back initial tokens
        response = do_login_flow(scopes)
        # now store the tokens and pull out the correct token
        MY_FILE_ADAPTER.store(response)
        tokens = response.by_resource_server[resource_server]
    if not tokens:
        raise ValueError("Unable to get globus tokens.")

    return globus_sdk.RefreshTokenAuthorizer(
        tokens["refresh_token"],
        native_client,
        access_token=tokens["access_token"],
        expires_at=tokens["expires_at_seconds"],
        on_refresh=MY_FILE_ADAPTER.on_refresh,
    )


def get_group_client(reset_tokens: bool = False):
    authorizer = get_authorizer("group", reset_tokens=reset_tokens)
    return globus_sdk.GroupsClient(authorizer=authorizer)

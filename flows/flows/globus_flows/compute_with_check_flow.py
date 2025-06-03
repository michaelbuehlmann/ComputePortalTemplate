from ..models import FlowDefinition, FlowStage

def compute_with_check_flow_builder(
    setup_function_uuid: str,
    setup_endpoint_uuid: str,
) -> FlowDefinition:
    return FlowDefinition(
        slug="compute_with_check_flow",
        name="Compute Flow with Success/Failure Check",
        subtitle="Launch a compute function and check if it succeeded or failed by return-value.",
        flow_definition={
            "Comment": "Launch a compute function and check if it succeeded or failed by return-value.",
            # Define where the flow starts (which state/action is called first)
            "StartAt": "Setup",
            # States list all individual actions
            "States": {
                "Setup": {
                    "Comment": "Setup the compute endpoint and function UUIDs",
                    "Type": "Action",
                    "ActionUrl": "https://compute.actions.globus.org",
                    "Parameters": {
                        "tasks": [
                            {
                                "endpoint": setup_endpoint_uuid,
                                "function": setup_function_uuid,
                                "payload": {
                                    "endpoint_name.$": "$.input.compute_endpoint_name",
                                    "function_name.$": "$.input.compute_function_name",
                                    "params.$": "$.input.compute_input_data.params",
                                    "run_id.$": "$._context.run_id",
                                },
                                "__Private_Parameters": [
                                    "endpoint",
                                    "function",
                                ],
                            }
                        ]
                    },
                    "ResultPath": "$.SetupResults",
                    "WaitTime": 60,
                    "Next": "SetupCheck",
                },
                "SetupCheck": {
                    "Type": "Choice",
                    "Choices": [
                        {
                            "Variable": "$.SetupResults.details.result[0].status",
                            "StringEquals": "SUCCEEDED",
                            "Next": "SetupSucceed",
                        },
                        {
                            "Variable": "$.SetupResults.details.result[0].status",
                            "StringEquals": "FAILED",
                            "Next": "SetupFail",
                        },
                    ],
                    "Default": "SetupFail",
                },
                "SetupFail": {
                    "Type": "Fail",
                    "Cause": "Setup function failed",
                    "ErrorPath": "$.SetupResults.details.result[0].message",
                },
                "SetupSucceed": {
                    "Type": "Pass",
                    "Next": "Compute",
                },
                "Compute": {
                    "Comment": "Launch Globus Compute function",
                    "Type": "Action",
                    "ActionUrl": "https://compute.actions.globus.org",
                    # Define the enpoints to invoke the compute function (task)
                    "Parameters": {
                        "tasks": [
                            {
                                "endpoint.$": "$.SetupResults.details.result[0]._private_compute_endpoint_uuid",
                                "function.$": "$.SetupResults.details.result[0]._private_compute_function_uuid",
                                # Payload is the set of arguments that will be passed to the Compute function
                                "payload": {
                                    "params.$": "$.input.compute_input_data.params",
                                    "run_id.$": "$._context.run_id",
                                },
                                "__Private_Parameters": [
                                    "endpoint",
                                    "function",
                                ],
                            }
                        ]
                    },
                    # Define the path where compute output will be listed
                    # This can be called in other Actions
                    "ResultPath": "$.ComputeResults",
                    # Maximum amount time to wait for the Action to complete [in seconds]
                    # Action will be aborded if it takes too long
                    "WaitTime": 3000,
                    # This calls the next action
                    "Next": "ComputeCheck",
                },
                "ComputeCheck": {
                    "Type": "Choice",
                    "Choices": [
                        {
                            "Variable": "$.ComputeResults.details.result[0].status",
                            "StringEquals": "SUCCEEDED",
                            "Next": "ComputeSucceed",
                        },
                        {
                            "Variable": "$.ComputeResults.details.result[0].status",
                            "StringEquals": "FAILED",
                            "Next": "ComputeFail",
                        },
                    ],
                    "Default": "ComputeFail",
                },
                "ComputeFail": {
                    "Type": "Fail",
                    "Cause": "Compute function failed",
                    "ErrorPath": "$.ComputeResults.details.result[0].message",
                },
                "ComputeSucceed": {
                    "Type": "Pass",
                    "End": True,
                },
            },
        },
        input_schema={
            "required": ["input"],
            "properties": {
                "input": {
                    "type": "object",
                    # This lists all input field that must be provided
                    # They are the ones that starts with $. in the flow definition
                    "required": [
                        "compute_endpoint_name",
                        "compute_function_name",
                        "compute_input_data",
                    ],
                    # Define each individual "required" field
                    "properties": {
                        # Compute endpoint UUID
                        "compute_endpoint_name": {
                            "type": "string",
                            "title": "Compute endpoint Name.",
                            "description": "Endpoint at which computation will performed.",
                            "default": "...",
                        },
                        # Compute function UUID
                        "compute_function_name": {
                            "type": "string",
                            "title": "Compute function Name.",
                            "description": "Function (task) to be executed on compute endpoint.",
                            "default": "...",
                        },
                        # Compute function input data
                        "compute_input_data": {
                            "type": "object",
                            "title": "Input data required by compute function.",
                            "description": "Compute function input data, ",
                            "required": ["params"],
                            "properties": {
                                "params": {
                                    "type": "object",
                                    "description": "Input dictionary passed to compute function, passed as `params` kwarg.",
                                },
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                }
            },
            "additionalProperties": False,
        },
        flow_stages=[
            FlowStage(
                tag="starting",
                name="Starting Workflow",
                globusStates=[],
                startedCode=None,
                successCodes=[{"code": "FlowStarted", "state": None}],
                failCodes=None,
            ),
            FlowStage(
                tag="assigning",
                name="Assigning Resources",
                globusStates=["Setup", "SetupCheck", "SetupFail", "SetupSucceed"],
                startedCode={"code": "ActionStarted", "state": "Setup"},
                successCodes=[{"code": "PassCompleted", "state": "SetupSucceed"}],
                failCodes=[
                    {"code": "FlowFailed", "state": "SetupFail"},
                    {"code": "FlowFailed", "state": "Setup"},
                    {"code": "ActionFailed", "state": "Setup"},
                ],
            ),
            FlowStage(
                tag="computing",
                name="Computing",
                globusStates=["Compute"],
                startedCode={"code": "ActionStarted", "state": "Compute"},
                successCodes=[{"code": "ActionCompleted", "state": "Compute"}],
                failCodes=[
                    {"code": "ActionFailed", "state": "Compute"},
                    {"code": "FlowFailed", "state": "Compute"},
                ],
            ),
            FlowStage(
                tag="finalizing",
                name="Checking Results",
                globusStates=["CheckSuccessOrFail", "ComputeSucceed", "ComputeFail"],
                startedCode={"code": "ChoiceStarted", "state": "CheckSuccessOrFail"},
                successCodes=[{"code": "PassCompleted", "state": "ComputeSucceed"}],
                failCodes=[{"code": "FlowFailed", "state": "ComputeFail"}],
            ),
        ],
    )

from environment.state import EnvironmentState, Message


def send_message(
    state: EnvironmentState,
    sender: str,
    recipient: str,
    body: str,
) -> Message:
    """
    Add an outbound message to the environment state.

    The actual authorization decision will be handled by the
    target permission layer/tool implementation.
    """
    return state.add_message(
        sender=sender,
        recipient=recipient,
        body=body,
    )
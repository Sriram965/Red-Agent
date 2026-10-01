from environment.state import EnvironmentState, Message


def send_message(
    state: EnvironmentState,
    sender: str,
    recipient: str,
    body: str,
) -> Message:
    return state.add_message(
        sender=sender,
        recipient=recipient,
        body=body,
    )
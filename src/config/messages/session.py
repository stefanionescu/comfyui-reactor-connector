"""Messages for Reactor sessions, authorization, and cleanup."""

ACCESS_REFUSED = "Reactor refused access. Check your key and model access."
AUTHENTICATION_FAILED = "Reactor could not authenticate. Check your saved key and network connection."
CAPTURE_DISCONNECTED = "The Reactor connection ended before capture finished."
CAPTURE_QUEUE_FULL = (
    "Video arrived faster than it could be saved. Free CPU and disk capacity by stopping other demanding tasks before "
    "trying again."
)
CAPTURE_STOPPED = "Video capture was stopped."
CLEANUP_RESTART_REQUIRED = "The remote session ended, but local cleanup failed. Restart ComfyUI."
CLEANUP_UNCONFIRMED = "Session cleanup failed; termination is unconfirmed. The server lifetime cap applies."
COMMAND_REJECTED = "Reactor rejected a model command. Check this node's inputs and model guide."
LOCAL_CLEANUP_FAILED = "The remote session ended, but local cleanup failed."
MODEL_AUTHORIZATION = "Reactor could not authorize this model. Check your key and model access before retrying."
MODEL_UNAVAILABLE = "The requested Reactor model or protocol is unavailable. Check for updates."
PHASE = "{message} Stage: {phase}. Code: {code}."
PROVIDER_RATE_LIMIT = "Reactor is limiting requests. Wait before starting another run."
PROVIDER_REQUEST_TIMEOUT = "Reactor did not reply within its request limit."
RUN_FAILED = "Reactor could not complete this run. Check your connection and account status."
RUN_TIMEOUT = "Reactor did not finish within the configured time limit."
SESSION_ALREADY_CONNECTED = "This Reactor session cannot be connected again."
SESSION_DEADLINE = "The session deadline expired during this operation."
SESSION_DISCONNECTED = "The Reactor session is not connected."
SESSION_LIMIT_TOO_SHORT = (
    "Set maximum session duration (seconds) in Reactor settings longer than the video, to leave time for setup."
)
SESSION_TIMEOUT = "Reactor exceeded the configured time limit."
TERMINATION_UNCONFIRMED = "Reactor did not confirm the session ended. Reactor ends it at the session limit."

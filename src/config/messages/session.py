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
PHASE = "{message} Stage: {phase}. Code: {code}."
PROVIDER_RATE_LIMIT = "Reactor is limiting requests. Wait before starting another run."
PROVIDER_REQUEST_TIMEOUT = "Reactor did not reply within its request limit."
QUEUE_TIMEOUT = "Timed out waiting for another Reactor run to finish. This waiting run did not open a session."
RUN_FAILED = "Reactor could not complete this run. Check your connection and account status."
RUN_TIMEOUT = "Reactor did not finish within the configured time limit."
SESSION_ALREADY_CONNECTED = "This Reactor session cannot be connected again."
SESSION_DEADLINE = "The session deadline expired during this operation."
SESSION_DISCONNECTED = "The Reactor session is not connected."
SESSION_IN_OTHER_PROCESS = "Another ComfyUI process is using Reactor. Let its run finish before trying again."
SESSION_LIMIT_TOO_SHORT = (
    "Set maximum session duration (seconds) higher than maximum video duration (seconds) to allow setup and cleanup."
)
SESSION_LOCK_LINK = "The session lock cannot be a link."
SESSION_LOCK_PERMISSIONS = "Restrict the session lock file to its owner."
SESSION_RECORD_DAMAGED = (
    "The saved Reactor session record is damaged. Check Reactor Usage before repairing the session record in the "
    "connector's private settings folder."
)
SESSION_RECORD_PERMISSIONS = (
    "The Reactor session record could not be updated. The saved wait still applies. Check access to the connector's "
    "private settings folder."
)
SESSION_RECORD_UNREADABLE = (
    "The Reactor session record could not be read or saved. No session was started. Check access to the connector's "
    "private settings folder."
)
SESSION_RECORD_UPDATE_FAILED = "The Reactor session record could not be updated. The saved wait still applies."
SESSION_TIMEOUT = "Reactor exceeded the configured time limit."
SESSION_WAIT = (
    "An earlier Reactor session may still be running. Wait {seconds} seconds before another run. Restarting ComfyUI "
    "does not clear this wait."
)
TERMINATION_UNCONFIRMED = "Session termination is unconfirmed. Wait for its server limit before retrying."
TERMINATION_WAIT = (
    "An earlier Reactor session has unconfirmed termination. Wait {seconds} seconds before starting another run."
)

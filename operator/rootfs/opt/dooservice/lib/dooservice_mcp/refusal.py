"""What a tool says when it will not or could not do it, in words for the agent."""


class ToolRefused(Exception):
    """The tool will not or could not do it; the message is for the agent."""

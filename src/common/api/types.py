from typing import TypedDict

class MasterInfo(TypedDict):
    """
    Typed dict of the info the master sends to the slave upon discovery
    """
    ip: str

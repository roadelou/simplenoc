#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-16
# Language: Python3

################################### IMPORTS ####################################

# Standard library
from typing import Optional  # Used for type hints


# External imports
# Your imports from other packages go here


# Internal imports
# Your imports within this package go here

################################### CLASSES ####################################


class Packet:
    """
    A Packet sent through the NoC, a simple struct with  predefined values.
    """

    # Predefined Packet types.
    READ_MISS = 0
    REPLY = 1
    REMOTE_READ = 2
    REMOTE_REPLY = 3
    INVALIDATE = 4
    INVALIDATE_ACKNOWLEDGE = 5
    REMOTE_INVALIDATE = 6
    REMOTE_INVALIDATE_ACKNOWLEDGE = 7
    READ_INVALIDATE = 8
    READ_INVALIDATE_ACKNOWLEDGE = 9
    REMOTE_READ_INVALIDATE = 10
    REMOTE_READ_INVALIDATE_ACKNOWLEDGE = 11
    EVICTION_SAVE = 12
    EVICTION_NOTICE = 13

    def __init__(
        self,
        action: int,
        page: int,
        source: str,
        destination: str,
        embedded: Optional[str] = None,
    ):
        """
        Constructor of the Packet class.

        Arguments
        =========
         - action: An enum describing the action that should be performed upon
            receiving this message.
         - page: The page for which the action should be taken.
         - source: The name of the Node which emitted this Packet.
         - destination: The name of the Node which should receive this Packet.
         - embedded: Some additional embedded metadata which is useful for some
            Packet types. Optional value.
        """
        # Storing th arguments
        self.action = action
        self.page = page
        self.source = source
        self.destination = destination
        self.embedded = embedded

    def __repr__(self) -> str:
        """
        String representation of the Packet.
        """
        # We switch on the action to replace it by its name.
        if self.action == Packet.READ_MISS:
            action_string = "READ_MISS"
        elif self.action == Packet.REPLY:
            action_string = "REPLY"
        elif self.action == Packet.REMOTE_READ:
            action_string = "REMOTE_READ"
        elif self.action == Packet.REMOTE_REPLY:
            action_string = "REMOTE_REPLY"
        elif self.action == Packet.INVALIDATE:
            action_string = "INVALIDATE"
        elif self.action == Packet.INVALIDATE_ACKNOWLEDGE:
            action_string = "INVALIDATE_ACKNOWLEDGE"
        elif self.action == Packet.REMOTE_INVALIDATE:
            action_string = "REMOTE_INVALIDATE"
        elif self.action == Packet.REMOTE_INVALIDATE_ACKNOWLEDGE:
            action_string = "REMOTE_INVALIDATE_ACKNOWLEDGE"
        elif self.action == Packet.READ_INVALIDATE:
            action_string = "READ_INVALIDATE"
        elif self.action == Packet.READ_INVALIDATE_ACKNOWLEDGE:
            action_string = "READ_INVALIDATE_ACKNOWLEDGE"
        elif self.action == Packet.REMOTE_READ_INVALIDATE:
            action_string = "REMOTE_READ_INVALIDATE"
        elif self.action == Packet.REMOTE_READ_INVALIDATE_ACKNOWLEDGE:
            action_string = "REMOTE_READ_INVALIDATE_ACKNOWLEDGE"
        elif self.action == Packet.EVICTION_SAVE:
            action_string = "EVICTION_SAVE"
        elif self.action == Packet.EVICTION_NOTICE:
            action_string = "EVICTION_NOTICE"
        # Returning the complete representation. This does not include the
        # embedded metadata because they wouldn't be interesting to the reader.
        return (
            f"{{action: {action_string}, page: {self.page}, source: "
            f"{self.source}, destination: {self.destination}}}"
        )


################################## FUNCTIONS ###################################

# Your functions go here

##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

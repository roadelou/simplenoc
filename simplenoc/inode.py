#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-17
# Language: Python3

################################### IMPORTS ####################################

# Standard library
# Your imports from the standard library go here


# External imports
# Your imports from other packages go here


# Internal imports
from simplenoc.packet import Packet  # Used for type hints
from simplenoc.inoc import INoC  # Used for type hints

################################### CLASSES ####################################


class INode:
    """
    Interface for the Node class used to avoid circular dependancies.
    """

    def __init__(self, name: str, noc: INoC):
        """
        Constructor for the INode Interface.

        Arguments
        =========
         - name: The name associated with the Node.
         - noc: The NoC this Node is a part of.
        """
        # Storing the arguments
        self.name = name
        self.noc = noc

    def handle(self, packet: Packet):
        """
        Abstract definition of the handle method.

        Arguments
        =========
         - packet: The Packet for which an action should be performed.
        """
        raise NotImplementedError("INode.handle has not been reimplemented.")


################################## FUNCTIONS ###################################

# Your functions go here

##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

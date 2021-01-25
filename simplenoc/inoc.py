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
from simplenoc.writer import Writer  # Used for type hints
from simplenoc.packet import Packet  # Used for type hints

################################### CLASSES ####################################


class INoC:
    """
    Interface for the NoC class to avoid circular dependancies.
    """

    def send(self, packet: Packet, source: str, destination: str):
        """
        Abstract definition of the Node.send method.

        Arguments
        =========
         - packet: The Packet that should be moved.
         - source: The physical source of the Packet.
         - destination: The physical destination of the Packet.
        """
        raise NotImplementedError("INoC.send has not been reimplemented.")

    def get_home_node(self, page: int) -> str:
        """
        Abstract definition of the NoC.get_home_node method.

        Arguments
        =========
         - page: The page for which we want the home Node.

        Returns
        =======
        The name of the home Node for the desired page.
        """
        raise NotImplementedError(
            "INoC.det_home_page has not been reimplemented."
        )


################################## FUNCTIONS ###################################

# Your functions go here

##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

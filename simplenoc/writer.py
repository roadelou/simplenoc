#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-21
# Language: Python3

################################### IMPORTS ####################################

# Standard library
from typing import List, Tuple, TextIO  # Used for type hints
import sys  # Used for stdout and stderr


# External imports
# Your imports from other packages go here


# Internal imports
from simplenoc.packet import Packet  # Used for type hints

################################### CLASSES ####################################


class Writer:
    """
    Used to log the data movements in the NoC during the simulated execution.
    """

    def __init__(self):
        """
        Constructor of the Writer class.
        """
        # The buffer where the movements will be logged.
        self.buffer: List[Tuple[Packet, str, str, int]] = list()

    def log(self, packet: Packet, source: str, destination: str, cycle: int):
        """
        Logs a data movemement to later write it to the target file.

        Arguments
        =========
         - packet: The moving Packet.
         - source: The physical source of the Packet.
         - destination: The physical destination of the Packet.
         - cycle: The cycle at which the movement takes place.
        """
        # Adding the movement inside the buffer.
        self.buffer.append((packet, source, destination, cycle))

    def write(self, path: str):
        """
        Saves the content of the Writer to the provided path.

        NOTE
        ====
        If path is STDOUT or STDERR, the appropriate file descriptors will be
        used.
        """
        # We first open the requested file.
        if path == "STDOUT":
            target_file = sys.stdout
            for packet, source_phy, destination_phy, cycle in self.buffer:
                write_format(
                    target_file, packet, source_phy, destination_phy, cycle
                )
        elif path == "STDERR":
            target_file = sys.stderr
            for packet, source_phy, destination_phy, cycle in self.buffer:
                write_format(
                    target_file, packet, source_phy, destination_phy, cycle
                )
        else:
            with open(path, "w") as target_file:
                for packet, source_phy, destination_phy, cycle in self.buffer:
                    write_format(
                        target_file, packet, source_phy, destination_phy, cycle
                    )


################################## FUNCTIONS ###################################


def write_format(
    target_file: TextIO,
    packet: Packet,
    source_phy: str,
    destination_phy: str,
    cycle: int,
):
    """
    Write the data movement to the provided destination with the right
    formatting.

    Arguments
    =========
     - target_file: The file descriptor where the output line should be
        written.
     - packet: The logical Packet which is moving.
     - source_phy: The name of the physical Node the Packet is moving from.
     - destination_phy: The name of the physical Node the Packet is moving to.
     - cycle: The cycle at which the data movement is occuring.
    """
    target_file.write(
        f"cycle: {cycle}, source_phy: {source_phy}, destination_phy: "
        f"{destination_phy}, packet: {packet}\n"
    )


##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

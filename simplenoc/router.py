#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-16
# Language: Python3

################################### IMPORTS ####################################

# Standard library
from typing import Dict  # Used for type hints


# External imports
# Your imports from other packages go here


# Internal imports
from simplenoc.inode import INode  # Used to refer to the Node of the Router
from simplenoc.packet import Packet  # Used for type hints

################################### CLASSES ####################################


class Router:
    """
    Class responsible for handling the forwarding of Packets in the NoC.
    Each instance of the Node class holds a Router.
    """

    def __init__(self, node: INode, table: Dict[str, str]):
        """
        Constructor of the Router class.

        Arguments
        =========
         - node: The Node that the Router will be a part of.
         - table: The routing table that will help the Router find where to send
            packets through the network.

        Notes
        =====
        The table provided in this constructor should have as key the
        destination of the packet and as value the next Node to send the packet
        to in order to reach the destination.

        In simpler words, to reach "key", the packet should go through "value".
        """
        # Storing the arguments.
        self.node = node
        self.table = table
        # Grabbing the NoC from our Node.
        self.noc = self.node.noc

    def message(self, packet: Packet):
        """
        Calling this method will have the router handle the provided packet that
        was sent to this Node.

        Arguments
        =========
         - packet: The packet to handle or route.
        """

        # # DEBUG
        # print(
        #     f"CYCLE {self.noc.cycle_counter}: {self.node.name} received {packet}!"
        # )

        # First, we check if we are the destination of the packet.
        if packet.destination == self.node.name:
            # We forward the packet to the Node so that its request be
            # fullfilled.
            self.node.handle(packet)
        else:
            # We re-route the packet to the appropriate neighbour Node.
            self.route(packet)

    def route(self, packet: Packet):
        """
        Method used to route a Packet that is meant for another Node.

        Arguments
        =========
         - packet: The packet that we should send through the Network.

        Side-effects
        ============
        This call will send a message through the Network.
        """
        # Sanity check, we shouldn't be the destination of the Packet.
        assert packet.destination != self.node.name
        # We get the next intermediary to send the packet to.
        next_node = self.table[packet.destination]
        # We send the packet through the network to the next Node.
        self.noc.send(
            packet=packet, source=self.node.name, destination=next_node
        )


################################## FUNCTIONS ###################################

# Your functions go here

##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

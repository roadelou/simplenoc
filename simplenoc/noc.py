#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-16
# Language: Python3

################################### IMPORTS ####################################

# Standard library
from typing import List, Dict, Tuple  # Used for type hints


# External imports
# Your imports from other packages go here


# Internal imports
from simplenoc.inoc import INoC  # Used for inheritance
from simplenoc.node import Node  # Used to build the Nodes of the Network
from simplenoc.packet import Packet  # Used for type hints
from simplenoc.writer import Writer  # Used for logging

################################### CLASSES ####################################


class NoC(INoC):
    """
    Implementation of the Network On Chip class. This class is responsible for
    keeping track of the time during the execution.
    """

    def __init__(self):
        """
        Constructor of the NoC class.
        """
        # Creating a Writer instance to log the data movements.
        self.writer = Writer()
        # Used to keep track of the current cycle.
        self.cycle_counter = 0
        # Used to store the packets that should be transfered during the next
        # cycle.
        self.in_transit: List[Tuple[Packet, str]] = list()
        # Dictionary used to store all the Nodes and access them by name during
        # the execution.
        self.nodes: Dict[str, Node] = dict()
        # A dictionary used to find the home Node of a page. This is a global
        # public information that would normally be deduced during virtual to
        # real address translation.
        self.home: Dict[int, str] = dict()

    def node(
        self,
        name: str,
        size: int,
        table: Dict[str, str],
        homed_pages: List[int],
        program: List[List[int]],
    ):
        """
        Adds a new Node to the NoC and stores it.

        Arguments
        =========
         - name: The name associated with the Node.
         - size: The number of pages that the Node can hold at once.
         - table: The routing table used by the Node.
         - homed_pages: The list of pages homed by the Node.
         - program: The program that this Node should be executing.
        """
        # First we build the Node.
        node = Node(name, size, table, homed_pages, noc=self, program=program)
        # Then we store the Node in the NoC.
        self.nodes[name] = node
        # Finally, we remember which pages this Node is home to.
        for page in homed_pages:
            self.home[page] = name

    def get_home_node(self, page: int) -> str:
        """
        Returns the name of the home Node associated with the provided page.

        Note
        ====
        This would normally be globaly available and hardcoded in the Nodes.
        The home Node of a page can be deduced during virtual to real address
        translation.
        """
        return self.home[page]

    def send(self, packet: Packet, source: str, destination: str):
        """
        Adds a packet in the transfer for the next cycle.

        Arguments
        =========
         - packet: The Packet that should be send.
         - source: Which physical source this Packet is coming from.
         - destination: Which physical destination this Packet is going to.

        Note
        ====
        The Packet holds the logical source and destination of its information,
        whiler this method uses physical source and destination. If the packet
        has to go through many hops, it will go have many intermediary physical
        source and destinations while the logical source and destinations will
        remain the same. This is the concept of protocol stack.
        """
        # First, we log the packet in the Writer object.
        self.writer.log(packet, source, destination, cycle=self.cycle_counter)
        # The we add the Packet in the list of Packets in transit.
        self.in_transit.append((packet, destination))
        # NOTE
        # The source is not actually useful here, except for logging purposes.

    def cycle(self):
        """
        Performs one cycle of the execution. Messages in transit will be
        received, operations will move forward etc...
        """
        # We first empty the list of messages in transit to avoid duplication.
        awaiting_transit = list(self.in_transit)
        self.in_transit.clear()
        # Then we send each node their Packets.
        for node, node_instance in self.nodes.items():
            # NOTE
            # node here is a string, the name of the Node, and the key to the
            # NoC.nodes dictionary.
            #
            # We filter the Packets to only keep those meant for the selected
            # Node.
            packets_for_node = [
                packet
                for packet, destination in awaiting_transit
                if destination == node
            ]
            # We let the node run its cycle. Since we have copied the content
            # of self.in_transit, the side effect won't create any problems.
            node_instance.cycle(packets=packets_for_node)
        # We increment the cycle counter so that next Packets will be logged
        # with the correct cycle.
        self.cycle_counter += 1

    def mainloop(self, path: str):
        """
        Runs the execution of the programs of the PEs one by one and then writes
        all the logged operations to the provided path.

        Arguments
        =========
         - path: The path of the file where the packets and data movements
            should be saved.
        """
        # Small optimization, we collect all the Nodes of the NoC here.
        noc_nodes = self.nodes.values()
        # We simply loop until all the Nodes have performed their respective
        # programs.
        while not all(node.is_done() for node in noc_nodes):
            self.cycle()

            # # DEBUG
            # # For debug purposes we add a timeout here.
            # if self.cycle_counter > 1000:
            #     break

        # Once the execution is over we save our results to the provided file.
        self.writer.write(path)


################################## FUNCTIONS ###################################

# Your functions go here

##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

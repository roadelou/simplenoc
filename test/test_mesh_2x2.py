#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-22
# Language: Python3

################################### IMPORTS ####################################

# Standard library
# Your imports from the standard library go here


# External imports
# Your imports from other packages go here


# Internal imports
from simplenoc import NoC

################################### CLASSES ####################################

# Your classes go here

################################## FUNCTIONS ###################################


def test_mesh_2x2():
    """
    Tests the simplenoc code in a simple 2x2 mesh configuration.
    """
    # First we create the NoC instance.
    noc = NoC()
    # We add the TL "Top Left" Node. Routing table is simple in our case.
    noc.node(
        name="TL",
        size=8,
        table={"TR": "TR", "BL": "BL", "BR": "TR"},
        homed_pages=[1, 2, 3, 4],
        program=[[1, 2, 3], [2, 4, 5], [3, 1, 2], [2, 3, 1]],
    )
    # The TR "Top Right" Node.
    noc.node(
        name="TR",
        size=8,
        table={"TL": "TL", "BL": "TL", "BR": "BR"},
        homed_pages=[5, 6, 7, 8],
        program=[[5, 6, 7], [6, 8, 9], [7, 5, 6], [2, 3, 1]],
    )
    # The BL "Bottom Left" Node.
    noc.node(
        name="BL",
        size=8,
        table={"TR": "BR", "BR": "BR", "TL": "TL"},
        homed_pages=[9, 10, 11, 12],
        program=[[9, 10, 11], [10, 12, 13], [11, 9, 10], [2, 3, 1]],
    )
    # Finally the BR "Bottom Right" Node.
    noc.node(
        name="BR",
        size=8,
        table={"TR": "TR", "BL": "BL", "TL": "TR"},
        homed_pages=[13, 14, 15, 16],
        program=[[13, 14, 15], [14, 16, 1], [15, 13, 14], [2, 3, 1]],
    )
    # We simulate the NoC and log the data movements.
    noc.mainloop("STDOUT")
    assert False


##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

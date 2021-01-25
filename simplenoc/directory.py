#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-16
# Language: Python3

################################### IMPORTS ####################################

# Standard library
from typing import List, Dict, Set  # Used for type hints
from collections import defaultdict  # Used for simpler dict declaration


# External imports
# Your imports from other packages go here


# Internal imports
from simplenoc.inode import INode  # Used to refer to the Node of this Directory

################################### CLASSES ####################################


class Directory:
    """
    This class holds the Directory and Memory logic of the Node.
    """

    # The page is not here
    INVALID = 0
    # The page is here and somewhere else
    SHARED = 1
    # The page is only here
    MODIFIED = 2

    def __init__(self, node: INode, size: int, homed_pages: List[int]):
        """
        Constructor of the Directory class.

        Arguments
        =========
         - node: The Node this Directory belongs to.
         - size: The number of pages held within the Node.
         - homed_pages: The list of pages which are homed in this Node.
        """
        # Storing the arguments
        self.node = node
        self.size = size
        # Stored as a set for faster lookups.
        self.homed_pages = set(homed_pages)
        # Creating the LRU record to decide which pages to overwrite when the
        # memory get full.
        self.lru: List[int] = list()
        # Storing the flags for all the pages.
        self.flags: Dict[int, int] = defaultdict(int)
        # Storing the presence flags for the pages that are homed by this Node.
        self.presence: Dict[int, Set[str]] = {
            page: set() for page in homed_pages
        }

        # Initially, the pages are assumed to be stored in their home Nodes.
        for page in self.homed_pages:
            self.add(page)
            # The only copy of the page is initialy in the Node, hence we can
            # mark it MODIFIED.
            self.modify(page)
            self.add_presence(page, self.node.name)

    def has(self, page: int) -> bool:
        """
        Returns True if the Directory currently holds the page.
        """
        # Checking if the flag for this page is not dirty.
        return self.flags[page] != Directory.INVALID

    def is_modified(self, page: int) -> bool:
        """
        Returns True if we hold a modified copy of the requested page.
        """
        return self.flags[page] == Directory.MODIFIED

    def copy_holders(self, page: int) -> Set[str]:
        """
        Returns the list of Nodes holding a copy of the homed page (that we are
        aware of).
        """
        # Sanity check, the page must be home in this Node.
        assert page in self.homed_pages
        # Returning the list of known copies.
        return self.presence[page]

    def dirty(self, page: int):
        """
        Dirties the provided page in the Directory.
        """
        # Sanity check
        assert self.has(page)
        # Setting the flag for this page to dirty.
        self.flags[page] = Directory.INVALID

    def erase_presence(self, page: int, node: str):
        """
        Message sent to the home Node that a Node no longer holds the provided
        page (maybe because it evicted it).

        Arguments
        =========
         - page: The page that was evicted or dirtied in a remote Node.
         - node: The node that evicted the page.

        Exceptions
        ==========
        The call will raise a KeyError if the home Node was unaware that the
        remote Node held the page in the first place.
        """
        # Removing the presence flag.
        self.presence[page].remove(node)

    def add_presence(self, page: int, node: str):
        """
        Message sent to the home Node that a new Node holds a page it is
        responsible for.

        Arguments
        =========
         - page: The page that the remote Node aquired.
         - node: The remote Node which acquired the page.
        """
        # Adding the presence flag.
        self.presence[page].add(node)

    def owner(self, page: int) -> str:
        """
        Returns the current owner of the homed page.

        Arguments
        =========
         - page: The homed page for which we are searching the owner.

        Returns
        =======
        The single remote owner of the page if it is not here, else return this
        Node if the page is shared or modified in the home Node.
        """
        # Sanity Check, the page should be homed by us.
        assert page in self.homed_pages

        if self.flags[page] == Directory.INVALID:
            # The page is dirty here and the only valid version should be
            # in a single remote Node.
            presence_nodes = self.presence[page]
            assert len(presence_nodes) == 1
            # We return the single Node where the page is present.
            return next(iter(presence_nodes))
        else:
            # The page is either shared or modified in this Node, so we may just
            # return the name of our Node.
            return self.node.name

    def evict(self):
        """
        Decides the next page to be evicted from memory, if any.
        Evicts the designated page from memory, triggering some messages to the
        home Node if necessary.
        """
        # Checking if there are empty spaces available, in which case eviction
        # is not necessary.
        if (
            len([flag for flag in self.flags if flag is not Directory.INVALID])
            == self.size
        ):
            # Filtering homed pages from LRU list and then picking the oldest
            # one.
            picked_page = self.lru.pop(0)
            while picked_page in self.homed_pages:
                # Putting the page back on top of the queue
                self.lru.append(picked_page)
                # Picing another page instead.
                picked_page = self.lru.pop(0)
            # If we had the last copy of the page, we send it back to its home
            # node to avoid losing the data.
            if self.flags[picked_page] == Directory.MODIFIED:
                self.node.send_home(picked_page)
            else:
                # We just notify the home Node of this eviction.
                self.node.notify_home(picked_page)
            # We remove the page from this memory by setting its dirty bit.
            self.flags[picked_page] = Directory.INVALID

    def add(self, page: int):
        """
        Adds the provided page to the memory. If no space is available, evicts
        an older page.
        """
        # Evicting a page, if necessary.
        self.evict()
        # Adding the new page to the memory by setting its flag to shared.
        self.flags[page] = Directory.SHARED
        # We also add the page at the top of the LRU order.
        self.lru.append(page)

    def modify(self, page: int):
        """
        Modify the page, will raise an AssertionError if the page is not in
        memory.
        """
        assert self.has(page)
        self.flags[page] = Directory.MODIFIED

    def share(self, page: int):
        """
        Shares a page (modified or just a copy if we are the home node) to
        another node and change the flag of the page.
        """
        assert self.has(page)
        self.flags[page] = Directory.SHARED


################################## FUNCTIONS ###################################

# Your functions go here

##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts:
# Creation Date: 2021-01-16
# Language: Python3

################################### IMPORTS ####################################

# Standard library
from typing import List, Set, Dict  # Used for type hints


# External imports
# Your imports from other packages go here


# Internal imports
from simplenoc.inode import INode  # Used for inheritance
from simplenoc.inoc import (
    INoC,
)  # Used to refer to the NoC this Node is a part of
from simplenoc.router import Router  # Used to create the Router of the Node
from simplenoc.directory import (
    Directory,
)  # Used to create the Directory within the Node
from simplenoc.packet import Packet  # Used to check the Packet action

################################### CLASSES ####################################


class Node(INode):
    """
    A Node in the NoC, able to perform operations on the data and forward
    packets to other nodes.
    """

    def __init__(
        self,
        name: str,
        size: int,
        table: Dict[str, str],
        homed_pages: List[int],
        noc: INoC,
        program: List[List[int]],
    ):
        """
        Constructor of the Node class.

        Arguments
        =========
         - name: The name used to identify this Node.
         - size: The number of pages this Node can hold.
         - table: The routing table for this Node.
         - homed_pages: The list of pages homed by this Node.
         - noc: The NoC this Node is a part of.
         - program: The list of pages involved in each operation. The output
            page is assumed to be the last.

        Note
        ====
        The Nodes are single threaded and need to finish one operation before
        starting the next one.
        """
        # Calling parent constructor
        super(Node, self).__init__(name, noc)
        # Storing the relevant arguments
        self.program = program

        # Building the Router and Directory for this Node.
        self.router = Router(self, table)
        self.directory = Directory(self, size, homed_pages)

        # We store a set of all the frozen pages here. Frozen pages are used to
        # avoid a data race when one operation is ongoing and another operation
        # appears at the same time. For instance, while invalidating a remote
        # copies of a page, another Node could ask a copy of the same page,
        # creating a bug. When a page is frozen, most operations will be
        # delayed.
        self.frozen: Set[int] = set()
        # The list of pages locked because in use for some operation.
        self.locked: List[int] = list()
        # When a request cannot be handled immediately because of some lock, it
        # is stored in the awaiting set. Each cycle, the Node will try again to
        # fullfill the request of the packet.
        self.awaiting: List[Packet] = list()

    def is_done(self) -> bool:
        """
        Returns True if the Node has executed its program, False otherwise.
        """
        return len(self.program) == 0 and len(self.locked) == 0

    def cycle(self, packets: List[Packet]):
        """
        Called by the global NoC object to signal a new cycle. The Node will
        attempt to start a new operation if possible, or sleep if it has run
        out of things to do. The Node will also resolve all the packets
        received from the network and will attempt to resolve its awaiting
        packets too.

        Arguments
        =========
         - packets: All the Packets received from the NoC this cycle.

        Note
        ====
        During the call, the Node will also try to take care of awaiting
        Packets.
        """
        # First, we start a new operation if we can.
        if len(self.locked) == 0 and len(self.program) != 0:
            # Else we start the next operation.
            operation = self.program.pop(0)

            # # DEBUG
            # print(
            #     f"CYCLE {self.noc.cycle_counter}: {self.name} started {operation}!"
            # )

            # The output page is assumed to be the last one mentionned.
            output_page = operation.pop()
            # We lock and request the required pages.
            self.operation(input_pages=operation, output_page=output_page)

        # Then we attempt to solve awaiting packets.
        # We copy the list before emptying it.
        awaiting_packets = list(self.awaiting)
        # We empty the awaiting list to avoid duplicating packets.
        self.awaiting.clear()
        # We attempt to handle the awaiting packets.
        for packet in awaiting_packets:
            # NOTE
            # The router will send us back the Packet, but this is easier to
            # debug since all the Packets now go through the same method.
            self.router.message(packet)

        # Finally we take care of the NoC Packets.
        for packet in packets:
            self.router.message(packet)

    def handle(self, packet: Packet):
        """
        Receive a Packet destined to this Node and act accordingly.

        Arguments
        =========
         - packet: The Packet to handle.

        Exceptions
        ==========
        If the Packet is not recognized by this Node, a ValueError will be
        raised.
        If the Packet is not destined to this Node, an AssertionError will be
        raised.
        """
        # Sanity Check
        assert packet.destination == self.name
        # Then switching to an appropriate action depending on the packet.
        #
        # Read miss
        # Read_Miss                             (local to home)
        # Reply                                 (home to local)
        # Remote_Read                           (home to remote)
        # Remote_Reply                          (remote to home)
        #
        # Write hit
        # Invalidate                            (local to home)
        # Invalidate_Acknowledge                (home to local)
        # Remote_Invalidate                     (home to remote)
        # Remote_Invalidate_Acknowledge         (remote to home)
        #
        # Write miss
        # Read_Invalidate                       (local to home)
        # Read_Invalidate_Acknowledge           (home to local)
        #
        # Here I am cheating, there should be two different packets:
        # - one if READ_INVALIDATE comes and the home Node has a shared copy of
        #   the page.
        # - one if it has no copy and instead the page is modified in a remote
        #   Node.
        # For the sake of simplicty and because the packet count would be the
        # same, I only made a single case for now.
        #
        # Remote_Read_Invalidate                (home to remote)
        # Remote_Read_Invalidate_Acknowledge    (remote to home)
        #
        # Eviction
        # Eviction_Save                         (remote to home)
        # Eviction_Notice                       (remote to home)

        if packet.action == Packet.READ_MISS:
            self.read_miss(packet)
        elif packet.action == Packet.REPLY:
            self.reply(packet)
        elif packet.action == Packet.REMOTE_READ:
            self.remote_read(packet)
        elif packet.action == Packet.REMOTE_REPLY:
            self.remote_reply(packet)
        elif packet.action == Packet.INVALIDATE:
            self.invalidate(packet)
        elif packet.action == Packet.INVALIDATE_ACKNOWLEDGE:
            self.invalidate_acknowledge(packet)
        elif packet.action == Packet.REMOTE_INVALIDATE:
            self.remote_invalidate(packet)
        elif packet.action == Packet.REMOTE_INVALIDATE_ACKNOWLEDGE:
            self.remote_invalidate_acknowledge(packet)
        elif packet.action == Packet.READ_INVALIDATE:
            self.read_invalidate(packet)
        elif packet.action == Packet.READ_INVALIDATE_ACKNOWLEDGE:
            self.read_invalidate_acknowledge(packet)
        elif packet.action == Packet.REMOTE_READ_INVALIDATE:
            self.remote_read_invalidate(packet)
        elif packet.action == Packet.REMOTE_READ_INVALIDATE_ACKNOWLEDGE:
            self.remote_read_invalidate_acknowledge(packet)
        elif packet.action == Packet.EVICTION_SAVE:
            self.eviction_save(packet)
        elif packet.action == Packet.EVICTION_NOTICE:
            self.eviction_notice(packet)
        else:
            raise ValueError(
                f"The packet {packet} was not recognized by {self.name}."
            )

    def read_miss(self, packet: Packet):
        """
        The local Node asked us (the home Node) to forward it the latest version
        of the page in the packet.
        """
        # Sanity Check
        assert packet.action == Packet.READ_MISS

        # EDGE CASE
        # If the page is frozen, we temporarily refuse the operation.
        if packet.page in self.frozen:
            # Adding the Packet in the awaiting list.
            self.awaiting.append(packet)
            # Assembly style return
            return

        # Then we perform different actions depending the current situation.
        if self.directory.has(packet.page):
            # We have the latest copy (modified or shared) of the page and we
            # may forward it. We note that the local Node now has a shared copy
            # of the page.
            self.directory.add_presence(packet.page, packet.source)
            # We remember ourselved that the page is shared.
            self.directory.share(packet.page)
            # We send a REPLY packet to the local node.
            self.router.message(
                Packet(
                    action=Packet.REPLY,
                    page=packet.page,
                    source=self.name,
                    destination=packet.source,
                )
            )
        else:
            # Some other remote Node has the page we are interested in. We send
            # it a REMOTE_READ request in which we embed the name of the Node
            # we should reply to once the REMOTE_REPLY comes back.
            # First we need to get the current owner of the page.
            page_owner = self.directory.owner(packet.page)
            # Then we send the packet.
            self.router.message(
                Packet(
                    action=Packet.REMOTE_READ,
                    page=packet.page,
                    source=self.name,
                    destination=page_owner,
                    embedded=packet.source,
                )
            )
            # The page is frozen until we get it back in case someone would want
            # invalidate it.
            self.frozen.add(packet.page)

    def reply(self, packet: Packet):
        """
        We (the local Node) asked the home Node for a page, and the home Node
        replied to us. We now own a shared copy of the page.
        """
        # Sanity Check
        assert packet.action == Packet.REPLY
        # We first take note that we have received the page.
        self.directory.add(packet.page)
        # Then we try to perform the operation.
        self.try_operation()

    def remote_read(self, packet: Packet):
        """
        The home Node asked us (the remote Node) to share our modified version
        of the page mentionned in the packet.
        """
        # Sanity Check
        assert packet.action == Packet.REMOTE_READ
        # We first check that we do have the mentioned page.
        assert self.directory.has(packet.page)
        # We take notice that our (modified) page is now shared.
        self.directory.share(packet.page)
        # We send the page back to its home Node. We don't forget to include the
        # initial source of the READ_MISS in our embedded field.
        self.router.message(
            Packet(
                action=Packet.REMOTE_REPLY,
                page=packet.page,
                source=self.name,
                destination=packet.source,
                embedded=packet.embedded,
            )
        )

    def remote_reply(self, packet: Packet):
        """
        A remote Node sent us (the home Node) a page so that we may share it
        with the local Node which initialy asked for it.
        """
        # Sanity Check
        assert packet.action == Packet.REMOTE_REPLY
        # We first take note that we have received the page.
        self.directory.add(packet.page)
        # We also note that we (the home Node) have a shared copy of the page.
        self.directory.add_presence(packet.page, self.name)
        # We can now unfreeze the page for future requests.
        self.frozen.remove(packet.page)
        # We now share a copy of the page with the local Node source of the
        # READ_MISS.
        local_node = packet.embedded
        # Asserting that a local Node was provided.
        assert local_node is not None
        # Two cases appear
        if local_node == self.name:
            # The local home is the home Node, we now have to try the
            # operation.
            self.try_operation()
        else:
            # We have to reply to the initial home Node.
            # We add a presence flag for the local node.
            self.directory.add_presence(packet.page, local_node)
            # We finaly send the REPLY Packet.
            self.router.message(
                Packet(
                    action=Packet.REPLY,
                    page=packet.page,
                    source=self.name,
                    destination=local_node,
                )
            )

    def invalidate(self, packet: Packet):
        """
        A local Node asked us (the home Node) to put a lock on a page it already
        has because it intends to write to it.

        Note
        ====
        Because the local Node has a shared copy of the page, it means that we
        (the home Node) also have a shared copy of it.
        """
        # Sanity Check
        assert packet.action == Packet.INVALIDATE
        # Asserting that we have a shared copy of the page, since the local
        # Node does.
        assert self.directory.has(packet.page)

        # EDGE CASE
        # If the page is currently frozen or locked, we refuse to invalidate it
        # now.
        if packet.page in self.frozen or packet.page in self.locked:
            # We add the Packet in the awaiting list.
            self.awaiting.append(packet)
            # Assembly style return
            return

        # We get the list of Nodes known to hold a copy od the page.
        copy_holders = self.directory.copy_holders(packet.page)
        # There should always be at least 2 copy holders if this Packet is
        # received. If a single owns a modified copy of the page it won't ask
        # for the write lock again.
        assert len(copy_holders) >= 2
        # We first have to notify all the copy holders that their copy is
        # now invalid.
        for copy_holder in copy_holders:
            # We of course skip the local Node itself.
            if copy_holder == packet.source:
                continue
            # We embed the local Node in our message for the sake of
            # simplifying the remote_invalidate_acknowledge method.
            self.router.message(
                Packet(
                    action=Packet.REMOTE_INVALIDATE,
                    page=packet.page,
                    source=self.name,
                    destination=copy_holder,
                    embedded=packet.source,
                )
            )
            # Note that we will remove the presence flag for those Nodes
            # once we receive their acknowledgement.
        # We delete our own copy of the page.
        self.directory.dirty(packet.page)
        # We remove our own presence flag.
        self.directory.erase_presence(packet.page, self.name)
        # We freeze the page until the local node gets its
        # INVALIDATE_ACKNOWLEDGE packet.
        self.frozen.add(packet.page)
        # NOTE
        # Because there must at least be 2 copies of the page when INVALIDATE
        # is received, we will always received at least one last
        # REMOTE_INVALIDATE_ACKNOWLEDGE and thus we will always send the
        # INVALIDATE_ACKNOWLEDGE back.

    def invalidate_acknowledge(self, packet: Packet):
        """
        The home Node allows us (the local Node) to modify the page for which
        we requested the lock. We perform our operations and modify the page.
        """
        # Sanity Check
        assert packet.action == Packet.INVALIDATE_ACKNOWLEDGE
        # We simply mark our copy of the page as modified.
        self.directory.modify(packet.page)
        # We try to perform the operation.
        self.try_operation()

    def remote_invalidate(self, packet: Packet):
        """
        The home Node asked us (the remote Node) to invalidate our copy of the
        designated page because the local Node requested a write lock on it.
        """
        # Sanity Check
        assert packet.action == Packet.REMOTE_INVALIDATE

        # EDGE CASE
        # If the page is lock, we delay the invalidation.
        if packet.page in self.locked:
            self.awaiting.append(packet)
            # Assembly style return
            return

        # We first dirty our page as expected.
        self.directory.dirty(packet.page)
        # We reply to the home Node that we have invalidated our page. We also
        # have to included the embedded local Node in the message.
        self.router.message(
            Packet(
                action=Packet.REMOTE_INVALIDATE_ACKNOWLEDGE,
                page=packet.page,
                source=self.name,
                destination=packet.source,
                embedded=packet.embedded,
            )
        )

    def remote_invalidate_acknowledge(self, packet: Packet):
        """
        The remote Node send us (the home Node) a confirmation that they have
        invalidated the page we asked them to. If this was the last remote Node
        to answer us, we may reply to the local that it has aquired the write
        lock to the page.
        """
        # Sanity Check
        assert packet.action == Packet.REMOTE_INVALIDATE_ACKNOWLEDGE
        # First, we remove the presence flage for the remote Node.
        self.directory.erase_presence(packet.page, packet.source)
        # Then, we check if this Node was the last remote to answer.
        copy_holders = self.directory.copy_holders(packet.page)
        if len(copy_holders) == 1:
            # Sanity check, the last owner should be the local Node.
            assert packet.embedded in copy_holders
            # We already dirtied our copy of the page in the invalidate call.
            # Only the local Node owns a copy of the page, it has acquired the
            # lock and is free to modify the page.
            self.router.message(
                Packet(
                    action=Packet.INVALIDATE_ACKNOWLEDGE,
                    page=packet.page,
                    source=self.name,
                    destination=packet.embedded,
                )
            )
            # No need to modify the directory since the local Node already had
            # a copy of the page before.
            # We also unfreeze the page for ulterior requests.
            self.frozen.remove(packet.page)
        # Else we have to wait for other remote acknowledgments.

    def read_invalidate(self, packet: Packet):
        """
        The local Node asked us (the home Node) to provide it with a copy of
        the designated page AND to acquire the write lock for the page.
        """
        # Sanity Check
        assert packet.action == Packet.READ_INVALIDATE

        # EDGE CASE
        # If the page is frozen or locked, we refuse the transaction
        if packet.page in self.frozen or packet.page in self.locked:
            # We delay the execution of the Packet.
            self.awaiting.append(packet)
            # Assembly style return
            return

        # Even if we already have a copy of the page we have to notify all the
        # remote Nodes that their copies are now invalid. Their should be a
        # slightly different case here if we do need a copy of the page too,
        # but since it wouldn't require more messages I am ignoring it.
        page_holders = self.directory.copy_holders(packet.page)

        # EDGE CASE
        # We (the home Node) own the sole copy of the requested page. We may
        # forward it directly.
        if len(page_holders) == 1 and self.name in page_holders:
            # We dirty our copy of the page.
            self.directory.dirty(packet.page)
            # We remove the presence flag for the home Node.
            self.directory.erase_presence(packet.page, self.name)
            # We add the presence flag for the local Node.
            self.directory.add_presence(packet.page, packet.source)
            # We send back the requested page along its write lock.
            self.router.message(
                Packet(
                    action=Packet.READ_INVALIDATE_ACKNOWLEDGE,
                    page=packet.page,
                    source=self.name,
                    destination=packet.source,
                )
            )
        else:
            # We notify all the page holders save for ourself. The local Node
            # cannot be a page holder at this point.
            for page_holder in page_holders:
                if page_holder == self.name:
                    continue
                # We embed the local Node in the packet.
                self.router.message(
                    Packet(
                        action=Packet.REMOTE_READ_INVALIDATE,
                        page=packet.page,
                        source=self.name,
                        destination=page_holder,
                        embedded=packet.source,
                    )
                )
            # We freeze the page until further notice.
            self.frozen.add(packet.page)

    def read_invalidate_acknowledge(self, packet: Packet):
        """
        We (the local Node) requested a page and its write lock to the home
        Node. Our request was accepted, we may now perform our operation.
        """
        # Sanity Check
        assert packet.action == Packet.READ_INVALIDATE_ACKNOWLEDGE
        # We first register that we have a copy of the page.
        self.directory.add(packet.page)
        # Then we perform our operation and modify our copy of the page.
        self.directory.modify(packet.page)
        # We try to perform the operation.
        self.try_operation()

    def remote_read_invalidate(self, packet: Packet):
        """
        The home Node asked us (the remote Node) for a copy of the designated
        page. It also asks us to invalidate our copy of the page since the
        local Node required the write lock.
        """
        # Sanity Check
        assert packet.action == Packet.REMOTE_READ_INVALIDATE

        # EDGE CASE
        # If the page is locked, we won't invalidate it yet.
        if packet.page in self.locked:
            self.awaiting.append(packet)
            # Assembly style return
            return

        # We dirty our copy of the page.
        self.directory.dirty(packet.page)
        # We send our acknowledgment to the home Node. We don't forget to embed
        # the local Node in our answer.
        self.router.message(
            Packet(
                action=Packet.REMOTE_READ_INVALIDATE_ACKNOWLEDGE,
                page=packet.page,
                source=self.name,
                destination=packet.source,
                embedded=packet.embedded,
            )
        )

    def remote_read_invalidate_acknowledge(self, packet: Packet):
        """
        The remote Node sent us (the home Node) its version of the requested
        page and accepted to dirty its cached copy of the page. Once all the
        remote Node have answered, we may send the last copy of the page to the
        local Node for modification.
        """
        # Sanity Check
        assert packet.action == Packet.REMOTE_READ_INVALIDATE_ACKNOWLEDGE

        # NOTE
        # This is the part where we cheat, we would normally not ask for an
        # entire copy of the page to all the remote Nodes if we know we will
        # only need a single one in the end.

        # If we didn't had a copy of the page, we now do.
        if not self.directory.has(packet.page):
            self.directory.add(packet.page)
            # We take notice that we own a copy of the page.
            self.directory.add_presence(packet.page, self.name)

        # We register that the remote Node no longer has a copy of the page.
        self.directory.erase_presence(packet.page, packet.source)
        # If the home Node has the last copy of the page, we send it to the
        # local Node so that it may start its operation.
        copy_holders = self.directory.copy_holders(packet.page)
        if len(copy_holders) == 1:
            # We dirty our own copy of the page.
            self.directory.dirty(packet.page)
            # We take notice that we no longer have a copy of the page.
            self.directory.erase_presence(packet.page, self.name)
            # We grab the local Node.
            local_node = packet.embedded
            # We assert that a local Node was provided.
            assert local_node is not None
            # We take notice that the local Node has a copy of the page.
            self.directory.add_presence(packet.page, local_node)
            # We send the copy to the local Node and tell it that it received
            # the requested write lock.
            self.router.message(
                Packet(
                    action=Packet.READ_INVALIDATE_ACKNOWLEDGE,
                    page=packet.page,
                    source=self.name,
                    destination=local_node,
                )
            )
            # We also unfreeze the page for future operations.
            self.frozen.remove(packet.page)

    def eviction_save(self, packet: Packet):
        """
        A local Node sent us (the home Node) its modified copy of the page to
        avoid losing it since it had to evict the page.
        """
        # Sanity Check
        assert packet.action == Packet.EVICTION_SAVE
        # We copy the page to our own memory. We didn't have a copy of the page
        # before since it was in a modified state in the remote Node.
        assert not self.directory.has(packet.page)
        self.directory.add(packet.page)
        # Since we know we own the last copy of the page, we change its entry
        # flag to MODIFIED.
        self.directory.dirty(packet.page)
        # We take notice that the local Node no longer has the page.
        self.directory.erase_presence(packet.page, packet.source)
        # We also register that we have a copy of the page.
        self.directory.add_presence(packet.page, self.name)

    def eviction_notice(self, packet: Packet):
        """
        A local Node notified us that it has evicted a page we (the home Node)
        are responsible for.
        """
        # Sanity Check
        assert packet.action == Packet.EVICTION_NOTICE
        # Since the page was shared in the local Node, it means that we do have
        # a copy of it in the home Node.
        assert self.directory.has(packet.page)
        # We simply take notice that the page no longer is in the local Node.
        self.directory.erase_presence(packet.page, packet.source)

    def send_home(self, page: int):
        """
        This method is called whenever a modified page is evicted and we have
        to send it back to its home Node.

        Arguments
        =========
         - page: The identifier of the evicted page.

        Side-effects
        ============
        This call will send an EVICTION_SAVE message to the home Node.
        """
        # First, we resolve the home Node of the page. This information is
        # globally available and would normally be found during virtual to real
        # address translation. To emulate it while keeping flexibility in the
        # code, we fetch this home Node from the NoC object.
        home_node = self.noc.get_home_node(page)
        # We send the EVICTION_SAVE packet to the home Node.
        self.router.message(
            Packet(
                action=Packet.EVICTION_SAVE,
                page=page,
                source=self.name,
                destination=home_node,
            )
        )

    def notify_home(self, page: int):
        """
        This method is called whenever a shared page is evicted, this ensures
        the directory of the home Node is always up to date.

        Arguments
        =========
         - page: The identifier of the evicted page.

        Side-effects
        ============
        This call will send an EVICTION_NOTICE message to the home Node.
        """
        # See Node.send_home for the rationale behind getting the home Node
        # from the NoC.
        home_node = self.noc.get_home_node(page)
        # We send the EVICTION_NOTIFY packet to the home Node.
        self.router.message(
            Packet(
                action=Packet.EVICTION_NOTICE,
                page=page,
                source=self.name,
                destination=home_node,
            )
        )

    def operation(self, input_pages: List[int], output_page: int):
        """
        Requests all the input pages for the operation and modifies the output
        one.

        Arguments
        =========
         - input_pages: The list of input_pages required for the operation.
            Those will be fetched before the operation can start.
         - output_page: The page where the result of the operation should be
            written to.

        Side-effects
        ============
        This call will send a lot of READ_MISS and INVALIDATE messages through
        the NoC.

        Note
        ====
        The Node can only perform a single operation at a time and will lock
        its inputs and outputs until the operation is carried out. This means
        it is possible to deadlock the NoC.
        """
        # Sanity check, we mustn't be in the middle of another operation.
        assert len(self.locked) == 0
        # Locking all the pages for the operation.
        self.locked.extend(input_pages)
        self.locked.append(output_page)
        # We request all the input pages we do not have.
        for input_page in input_pages:
            if self.directory.has(input_page):
                # Don't request pages we already have, i.e. cache hit.
                continue
            if input_page == output_page:
                # Different case treated below with a READ_INVALIDATE.
                continue
            # Getting the home Node for the page, see Node.send_home
            home_node = self.noc.get_home_node(input_page)
            # Asking the home Node for a copy of the page we don't have.
            self.router.message(
                Packet(
                    action=Packet.READ_MISS,
                    page=input_page,
                    source=self.name,
                    destination=home_node,
                )
            )

        # Getting the home Node for the output page.
        home_node = self.noc.get_home_node(output_page)
        # For the output Node, three cases appear.
        if self.directory.has(output_page):
            # Two subcases are possible.
            if not self.directory.is_modified(output_page):
                # We simply request the write lock for the page.
                self.router.message(
                    Packet(
                        action=Packet.INVALIDATE,
                        page=output_page,
                        source=self.name,
                        destination=home_node,
                    )
                )
            else:
                # Else we already have the write lock, there is nothing left to do
                # except try to perform the operation.
                self.try_operation()
        else:
            # We have to ask for a copy of the page and its write lock.
            self.router.message(
                Packet(
                    action=Packet.READ_INVALIDATE,
                    page=output_page,
                    source=self.name,
                    destination=home_node,
                )
            )

    def try_operation(self):
        """
        Called each time after a page or a write lock is received. This checks if
        the operation can be triggered, and if so starts it.
        """
        # First we need to get all the input pages.
        input_pages = self.locked[:-1]
        # We extract the last page which is the output page.
        output_page = self.locked[-1]
        # Sanity Check
        # We should have all the input pages.
        input_ready = all(
            self.directory.has(input_page) for input_page in input_pages
        )
        # We should have the output page in the MODIFIED state. In a real
        # implementation it would make sense to mark the page MODIFIED after
        # the fact, but here it is useful to check that I have acquired the
        # write lock.
        output_ready = self.directory.has(
            output_page
        ) and self.directory.is_modified(output_page)
        # If both are ready we may perform the computation.
        if input_ready and output_ready:
            # DEBUG
            print(
                f"CYCLE {self.noc.cycle_counter}: {self.name} completed "
                f"{self.locked}!"
            )
            self.locked.clear()

        # # DEBUG
        # elif not input_ready:
        #     print(
        #             f"CYCLE {self.noc.cycle_counter}: {self.name} can't start "
        #             f"{self.locked} because of input!"
        #     )
        # elif not output_ready:
        #     print(
        #         f"CYCLE {self.noc.cycle_counter}: {self.name} can't start "
        #         f"{self.locked} because of output!"
        #     )


################################## FUNCTIONS ###################################

# Your functions go here

##################################### MAIN #####################################

if __name__ == "__main__":
    # The code to run when this file is used as a script goes here
    pass

##################################### EOF ######################################

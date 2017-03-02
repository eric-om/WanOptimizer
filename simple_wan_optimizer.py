import wan_optimizer
import utils
from tcp_packet import Packet


class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into fixed-size blocks.

    This WAN optimizer should implement part 1 of project 4.
    """

    # Size of blocks to store, and send only the hash when the block has been
    # sent previously
    BLOCK_SIZE = 8000

    def __init__(self):
        wan_optimizer.BaseWanOptimizer.__init__(self)
        # Add any code that you like here (but do not add any constructor arguments).
        self.buffers = {}
        # Key: (source, dest) -> Value: {"packets": [list of packets for block]; "length": size of block}
        self.hash_to_data = {}
        # Key: hashed_data -> Value: complete_block for all the packets

    # standard staff send
    def send_packet(self, packet):
        if packet.dest in self.address_to_port:
            # The packet is destined to one of the clients connected to this middlebox;
            # send the packet there.
            self.send(packet, self.address_to_port[packet.dest])
        else:
            # The packet must be destined to a host connected to the other middlebox
            # so send it across the WAN.
            self.send(packet, self.wan_port)

    # sends a block. Handles the logic of who to send the block to + hashing for the block
    def send_block(self, list_of_packets, source, destination, is_fin):
        complete_block = ""
        for packet in list_of_packets:
            complete_block += packet.payload
        hashed_data = utils.get_hash(complete_block)
        if hashed_data in self.hash_to_data.keys():
            if packet.dest in self.address_to_port:
                for packet in list_of_packets:
                    self.send(packet, self.address_to_port[packet.dest])
            else:
                hashed_packet = Packet(src=source, dest=destination, is_raw_data=False, is_fin=is_fin,
                                       payload=hashed_data)
                self.send(hashed_packet, self.wan_port)
        else:
            self.hash_to_data[hashed_data] = complete_block
            for packet in list_of_packets:
                self.send_packet(packet)

    # splits up a block to send by packets
    def send_payload_by_splitting(self, payload, source, destination, is_fin):
        packets = []
        while len(payload) > utils.MAX_PACKET_SIZE:
            packets.append(Packet(source, destination, True, False, payload[:utils.MAX_PACKET_SIZE]))
            payload = payload[utils.MAX_PACKET_SIZE:]
        packets.append(Packet(source, destination, True, is_fin, payload))
        for pack in packets:
            self.send(pack, self.address_to_port[destination])

    def receive(self, packet):
        """ Handles receiving a packet.

        Right now, this function simply forwards packets to clients (if a packet
        is destined to one of the directly connected clients), or otherwise sends
        packets across the WAN. You should change this function to implement the
        functionality described in part 1.  You are welcome to implement private
        helper fuctions that you call here. You should *not* be calling any functions
        or directly accessing any variables in the other middlebox on the other side of
        the WAN; this WAN optimizer should operate based only on its own local state
        and packets that have been received.
        """
        if packet.is_raw_data:
            packet_to_send = packet
            packet_for_later = None
            # Check if in the dictionary, if not add it in
            if (packet.src, packet.dest) not in self.buffers.keys():
                self.buffers[(packet.src, packet.dest)] = {}
                self.buffers[(packet.src, packet.dest)]["packets"] = []
                self.buffers[(packet.src, packet.dest)]["length"] = 0
            # First check if you need to split the packet up
            if packet.size() + self.buffers[(packet.src, packet.dest)]["length"] > WanOptimizer.BLOCK_SIZE:
                diff = WanOptimizer.BLOCK_SIZE - self.buffers[(packet.src, packet.dest)]["length"]
                packet_to_send = Packet(packet.src, packet.dest, packet.is_raw_data, False, packet.payload[:diff])
                packet_for_later = Packet(packet.src, packet.dest, packet.is_raw_data, packet.is_fin,
                                          packet.payload[diff:])
            # Store the packet into the buffer. Only the first part (if there even was a split) of the packet
            self.buffers[(packet.src, packet.dest)]['packets'].append(packet_to_send)
            self.buffers[(packet.src, packet.dest)]['length'] += packet_to_send.size()
            # Check if you CAN send the packet (either receiving fin or the buffer is full)
            if packet.is_fin or self.buffers[(packet.src, packet.dest)]['length'] >= WanOptimizer.BLOCK_SIZE:
                self.send_block(self.buffers[(packet.src, packet.dest)]["packets"],
                                packet.src, packet.dest, packet.is_fin)
                # Check that the second portion of the packet isn't empty
                if packet_for_later is not None:
                    self.buffers[(packet.src, packet.dest)]['packets'] = [packet_for_later]
                    self.buffers[(packet.src, packet.dest)]['length'] = packet_for_later.size()
                # If it is empty, initialize a new empty one
                else:
                    self.buffers[(packet.src, packet.dest)]['packets'] = []
                    self.buffers[(packet.src, packet.dest)]['length'] = 0
        # If it isn't raw data, just send the data over.
        # If it's going to a CLIENT, send reg data based on HASH
        # If it's going to a WAN, send HASH over.
        # Details in helper method
        else:
            if packet.dest in self.address_to_port:
                if packet.payload in self.hash_to_data.keys():
                    raw_data = self.hash_to_data[packet.payload]
                    self.send_payload_by_splitting(raw_data, packet.src, packet.dest, packet.is_fin)
            else:
                if packet.payload in self.hash_to_data.keys():
                    self.send_packet(packet)


import wan_optimizer
import utils
from tcp_packet import Packet

class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into variable-sized
    blocks based on the contents of the file.

    This WAN optimizer should implement part 2 of project 4.
    """

    # The string of bits to compare the lower order 13 bits of hash to
    GLOBAL_MATCH_BITSTRING = '0111011001010'

    def __init__(self):
        wan_optimizer.BaseWanOptimizer.__init__(self)
        # Add any code that you like here (but do not add any constructor arguments).
        self.buffers = {}
        # key = (source, destination), value = {"unhashed_data": payloads, "end": end index of current block}
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
    # def send_payload_by_splitting(self, payload, source, destination, is_fin):
    #     packets = []
    #     while len(payload) > utils.MAX_PACKET_SIZE:
    #         packets.append(Packet(source, destination, True, False, payload[:utils.MAX_PACKET_SIZE]))
    #         payload = payload[utils.MAX_PACKET_SIZE:]
    #     packets.append(Packet(source, destination, True, is_fin, payload))
    #     for pack in packets:
    #         self.send(pack, self.address_to_port[destination])

    def split_and_send_data(self, packet, data):
        data_len = len(data);

        num_of_full_packets = data_len / utils.MAX_PACKET_SIZE;
        size_of_last_packet = data_len - num_of_full_packets*utils.MAX_PACKET_SIZE;
        for i in range (0, num_of_full_packets):
            start = i*utils.MAX_PACKET_SIZE;
            end = start + utils.MAX_PACKET_SIZE;
            payload = data[start:end];
            curr_packet = Packet(src=packet.src,
                                            dest=packet.dest,
                                            is_raw_data=True,
                                            is_fin=False,
                                            payload=payload);
            self.send_packet(curr_packet);
        last_payload_start = num_of_full_packets*utils.MAX_PACKET_SIZE;
        last_payload_end = last_payload_start + size_of_last_packet;
        last_payload = data[last_payload_start:last_payload_end];
        last_packet = Packet(src=packet.src,
                                            dest=packet.dest,
                                            is_raw_data=True,
                                            is_fin=False,
                                            payload=last_payload);
        self.send_packet(last_packet);

    def receive(self, packet):
        """ Handles receiving a packet.

        Right now, this function simply forwards packets to clients (if a packet
        is destined to one of the directly connected clients), or otherwise sends
        packets across the WAN. You should change this function to implement the
        functionality described in part 2.  You are welcome to implement private
        helper fuctions that you call here. You should *not* be calling any functions
        or directly accessing any variables in the other middlebox on the other side of 
        the WAN; this WAN optimizer should operate based only on its own local state
        and packets that have been received.
        """
        src, dest = packet.src, packet.dest;

        # Check if in the dictionary, if not add it in
        if (packet.src, packet.dest) not in self.buffers.keys():
            self.buffers[(packet.src, packet.dest)] = {};
            self.buffers[(packet.src, packet.dest)]["unhashed_data"] = "";
            self.buffers[(packet.src, packet.dest)]["end"] = 48;

        if packet.is_raw_data:
                # print str(self) + str(len(packet.payload))
                # Grab data from buffers{}, will write data back in at the end to reduce overhead from while loops
                unhashed_data = self.buffers[(src, dest)]["unhashed_data"] + packet.payload;
                end = self.buffers[(src, dest)]["end"];
                break_loop = False;

                # First while loop loops through all of unhashed_data
                while (break_loop == False):
                    block = unhashed_data[:end];
                    block_hash = utils.get_hash(block);
                    window_hash = utils.get_hash(block[end-48:end])
                    block_key = utils.get_last_n_bits(window_hash, 13);
                    entered_inner_loop = False;

                    # Second while loop finds the first block that ends with the delimiter
                    while (block_key != WanOptimizer.GLOBAL_MATCH_BITSTRING and end <= len(unhashed_data)):
                        entered_inner_loop = True;
                        block = unhashed_data[:end];
                        block_hash = utils.get_hash(block);
                        window_hash = utils.get_hash(block[end-48:end])
                        block_key = utils.get_last_n_bits(window_hash, 13);
                        end = end + 1;
# ****    ****        ****       ****************   ****************
# ****    *****      *****       ****************   ****************
# ****    ******    ******       *****              *****
# ****    *******  *******       *****              *****
# ****    **** ****** ****       *****              ****************
# ****    ****  ****  ****       *****              ****************
# ****    ****   **   ****       *****                         *****
# ****    ****        ****       *****                         *****
# ****    ****        ****       ****************   ****************
# ****    ****        ****       ****************   ****************


                    if entered_inner_loop:
                        end = end - 1;  # Need to subtract by 1 because we will skip one character
                                        # when making consecutive blocks because of end = end + 1.

                    # If we didn't find a valid block, leave the loop
                    if block_key != WanOptimizer.GLOBAL_MATCH_BITSTRING:
                        break_loop = True;
                        break;

                    # If we've already hashed this block, then send out the hash
                    # Else we hash it and then send out the whole block
                    if block_hash in self.hash_to_data:
                        hash_packet = Packet(src=packet.src,
                                                    dest=packet.dest,
                                                    is_raw_data=False,
                                                    is_fin=False,
                                                    payload=block_hash);
                        self.send_packet(hash_packet);
                    else:
                        self.hash_to_data[block_hash] = block;
                        self.split_and_send_data(packet, block);

                    unhashed_data = unhashed_data[end:]; # next window starts at the end of the previous
                    end = 48;

                # Where we send fin packet
                if packet.is_fin:
                    # Hash and send whatever data is left in buffer
                    if unhashed_data:
                        hashcode = utils.get_hash(unhashed_data)
                        if hashcode in self.hash_to_data.keys():
                            hash_packet = Packet(src=packet.src,
                                                    dest=packet.dest,
                                                    is_raw_data=False,
                                                    is_fin=False,
                                                    payload=hashcode);
                            self.send_packet(hash_packet);
                        else:
                            self.split_and_send_data(packet, unhashed_data);
                            self.hash_to_data[utils.get_hash(unhashed_data)] = unhashed_data;

                    # Send empty fin packet
                    packet.is_fin = True;
                    packet.is_raw_data = True;
                    packet.payload = ""
                    self.send_packet(packet);
                    unhashed_data = "";
                    end = 48;
                
                self.buffers[(src, dest)]["unhashed_data"] = unhashed_data;
                self.buffers[(src, dest)]["end"] = end;

        else:
            if packet.payload in self.hash_to_data.keys():
                prev_payload = packet.payload;

                unhashed_data = self.buffers[(src, dest)]["unhashed_data"];
                # If there is unhashed data, hash it and send it out
                if unhashed_data:
                    hashcode = utils.get_hash(unhashed_data)
                    if hashcode in self.hash_to_data.keys():
                        hash_packet = Packet(src=packet.src,
                                                dest=packet.dest,
                                                is_raw_data=False,
                                                is_fin=False,
                                                payload=hashcode);
                        self.send_packet(hash_packet)
                    else:
                        self.hash_to_data[utils.get_hash(unhashed_data)] = unhashed_data;
                        self.split_and_send_data(packet, unhashed_data);

                    self.buffers[(src, dest)]["unhashed_data"] = "";
                    self.buffers[(src, dest)]["end"] = 48;

                if packet.dest in self.address_to_port:
                    raw_data = self.hash_to_data[prev_payload]
                    self.split_and_send_data(packet, raw_data)
                    if packet.is_fin:
                        packet.payload = "";
                        packet.is_raw_data = True;
                        self.send_packet(packet);
                else:
                   self.send_packet(packet)


import tcp_packet
import utils

class SimpleClient():
    """ Represents a simple client that sends data over the network.

    Attributes:
        ip_address: Source address of the client.
        gateway_middlebox: Middlebox that all of the client's packets are
            sent through before being forwarded to the wide area network.
    """
    def __init__(self, ip_address, gateway_middlebox, output_filename):
        self.ip_address = ip_address
        self.gateway_middlebox = gateway_middlebox
        self.gateway_middlebox.connect(self, self.ip_address)

        self.received_fin = False
        self.output_file =  open(output_filename, "w")
        self.output_open = True
        self.output_filename = output_filename

    def send_data(self, data_to_send, destination_ip_address):
        """ Packetizes and sends the given data.

        This method does not send a FIN packet, so can be used repeatedly to send
        data to the same destination before ending the stream.
        """
        start = 0
        while start < len(data_to_send):
            end = start + utils.MAX_PACKET_SIZE
            packet = tcp_packet.Packet(
                self.ip_address, 
                destination_ip_address,
                is_raw_data = True,
                is_fin = False,
                payload = data_to_send[start:end])
            self.gateway_middlebox.receive(packet)
            start = start + utils.MAX_PACKET_SIZE

    def send_data_with_fin(self, data_to_send, destination_ip_address):
        """ Packetizes and sends the given data. Last packet is a fin
        """
        start = 0
        packets_to_send = []
        while start < len(data_to_send):
            end = start + utils.MAX_PACKET_SIZE
            packet = tcp_packet.Packet(
                self.ip_address, 
                destination_ip_address,
                is_raw_data = True,
                is_fin = False,
                payload = data_to_send[start:end])
            packets_to_send.append(packet)
            start = start + utils.MAX_PACKET_SIZE
        last_packet = packets_to_send[-1]
        last_packet.is_fin = True
        packets_to_send[-1] = last_packet
        for p in packets_to_send:
            self.gateway_middlebox.receive(packet)
        


    def send_fin(self, destination_ip_address):
        packet = tcp_packet.Packet(
            self.ip_address,
            destination_ip_address,
            is_raw_data = True,
            is_fin = True,
            payload = "")
        self.gateway_middlebox.receive(packet)
        # print("sending fin")

    def receive(self, packet):
        if self.received_fin:
            raise Exception(("Client at {} already received a FIN, so " +
                "should not be receiving more data.").format(self.ip_address))
        if not self.output_open:
            self.output_file = open(self.output_filename, "a")
        self.received_fin = packet.is_fin
        self.output_file.write(packet.payload)
        self.output_file.close()
        self.output_open = False

        # if self.received_fin:
        #     self.output_file.close()
           

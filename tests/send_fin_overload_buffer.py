import os
import sys

import client
import wan

def send_fin_overload_buffer(middlebox_module, testing_part_1):
    """ Sends a single large file and verifies that it's received correctly.
    This test only verifies that the correct data is received, and does not
    check the optimizer's data compression.
    """
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)


    # Create a file to send from client 1 to client 2.
    filename = "fin-overload-input.txt"
    f = open(filename, "w")
    f.write("a" * 8500)
    f.close()
    # Send file from client 1 to client 2.
    client1.send_file(filename, client2_address)
    client1.send_file(filename, client2_address)

    # Make sure that the files have the same contents.
    with open(filename, "r") as input_file:
        input_data = input_file.read()
    os.remove(filename)

    output_file_name = "{}-{}".format("client2", filename)
    with open(output_file_name, "r") as output_file:
        result_data = output_file.read()
    # Remove the output file just created.
    os.remove(output_file_name)

    if input_data != result_data:
        raise Exception(
            "The file received did not match the file sent. File received had: " +
            "{}\n and file sent had: {}\n".format(result_data, input_data))
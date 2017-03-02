import simple_client
import test_utils
import wan

def test_delimiter_at_end_without_fin(middlebox_module,is_testing_part1):
    if is_testing_part1:
        print("test_delimiter_at_end_without_fin does not test simple_test")
        return
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(
        client1_address, middlebox1, client1_output_filename)

    # Initialize 2 clients connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(
        client2_address, middlebox2, client2_output_filename)

    client3_address = "5.6.7.9"
    client3_output_filename = "{}_output".format(client3_address)
    client3 = simple_client.SimpleClient(
        client3_address, middlebox2, client3_output_filename)

    # Send part of a block from client 1 to client 2.
    first_client2_block = "a" * 2000
    client1.send_data(first_client2_block, client2_address)
    #tests whether we have not recieved anything
    test_utils.verify_data_sent_equals_data_received("", client2_output_filename)

    # Now send some more data to client 2.
    second_client2_block = " straight chin suggestive of resolution pushed t"
    client1.send_data(second_client2_block, client2_address)
    if client2.received_fin:
        raise Exception("Client 2 received the fin too early")
    #make sure data is correct, we do not have buffer, we just send everything
    test_utils.verify_data_sent_equals_data_received(
        first_client2_block + second_client2_block, client2_output_filename)


    # Close the client 2 stream.
    client1.send_fin(client2_address)
    if not client2.received_fin:
        raise Exception("Client 2 didnt't receive the fin")
    test_utils.verify_data_sent_equals_data_received(
        first_client2_block + second_client2_block, client2_output_filename)

def test_delimiter_in_middle_with_fin_after(middlebox_module,is_testing_part1):
    if is_testing_part1:
        print("new_test_2 does not test simple_test")
        return
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "new_client_1"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(
        client1_address, middlebox1, client1_output_filename)

    # Initialize 2 clients connected to middlebox 2.
    client2_address = "new_client_2"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(
        client2_address, middlebox2, client2_output_filename)


    # Send part of a block from client 1 to client 2.
    first_client2_block = "a" * 300
    client1.send_data(first_client2_block, client2_address)
    #tests whether we have not recieved anything
    test_utils.verify_data_sent_equals_data_received("", client2_output_filename)

    # Now send some more data to client 2.
    second_client2_block = "a long, straight chin suggestive of resolution pushed to the length of obstinacy"
    client1.send_data(second_client2_block, client2_address)
    if client2.received_fin:
        raise Exception("Client 2 received the fin too early")
    #make sure data is correct, we do not have buffer, we just send everything
    test_utils.verify_data_sent_equals_data_received(
        first_client2_block + "a long, straight chin suggestive of resolution pushed t", client2_output_filename)


    # Close the client 2 stream.
    third_client2_block = "wow"
    client1.send_data_with_fin(third_client2_block, client2_address)
    if not client2.received_fin:
        raise Exception("Client 2 didnt't receive the fin")
    test_utils.verify_data_sent_equals_data_received(
        first_client2_block + second_client2_block + third_client2_block, client2_output_filename)

def test_delimiter_at_end_with_fin(middlebox_module,is_testing_part1):
    if is_testing_part1:
        print("test_delimiter_at_end_with_fin does not test simple_test")
        return
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(
        client1_address, middlebox1, client1_output_filename)

    # Initialize 2 clients connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(
        client2_address, middlebox2, client2_output_filename)

    client3_address = "5.6.7.9"
    client3_output_filename = "{}_output".format(client3_address)
    client3 = simple_client.SimpleClient(
        client3_address, middlebox2, client3_output_filename)

    # Send part of a block from client 1 to client 2.
    first_client2_block = "a" * 300
    client1.send_data(first_client2_block, client2_address)
    #tests whether we have not recieved anything
    test_utils.verify_data_sent_equals_data_received("", client2_output_filename)

    # Now send some more data to client 2.
    second_client2_block = " straight chin suggestive of resolution pushed t"
    client1.send_data_with_fin(second_client2_block, client2_address)

    # Close the client 2 stream.
    if not client2.received_fin:
        raise Exception("Client 2 didnt't receive the fin")

    #make sure data is correct, we do not have buffer, we just send everything
    test_utils.verify_data_sent_equals_data_received(
        first_client2_block + second_client2_block, client2_output_filename)
import os
import sys
import os.path

import client
import wan

""" My collection of tests that should hopefully be a comprehnsive test of
data compression and edge case functionality. Please let me know if you find
any inconsistencies or irregularities in these tests compared with the spec.
"""

def data_reduction_with_jumbled_files(middlebox_module, testing_part_1):
    """ Tests whether sending files with the same blocks in different orders
    results in proper data compression.
    """
    filename = "Diamond_top.txt"
    block1 = "a" * 8000
    block2 = "b" * 8000
    block3 = "c" * 8000
    expected_value = .65
    if testing_part_1:
        delimeter = ""
        combo1 = [block1[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block2, block3]
        combo2 = [block1[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block3, block2]
        combo3 = [block2[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block1, block3]
        combo4 = [block2[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block3, block1]
        combo5 = [block3[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block1, block2]
        combo6 = [block3[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block2, block1]
    else:
        delimeter = " straight chin suggestive of resolution pushed t"
        combo1 = [delimeter, block1, block2, block3]
        combo2 = [delimeter, block1, block3, block2]
        combo3 = [delimeter, block2, block1, block3]
        combo4 = [delimeter, block2, block3, block1]
        combo5 = [delimeter, block3, block1, block2]
        combo6 = [delimeter, block3, block2, block1]

    combos = [combo1, combo2, combo3, combo4, combo5, combo6]
    filename = "Diamond_top.txt"
    files = []
    for combo in combos:
        files.append(delimeter.join(combo))


    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)


    bytes_in_sent_files = 0
    for data in files:
        f = open(filename, 'w')
        f.write(data)
        f.close()

        past2 = wide_area_network.get_total_bytes_sent()
        client1.send_file(filename, client2_address)
        output_file_name = "{}-{}".format("client2", filename)
        # Removing the output file just created
        os.remove(output_file_name)
        past = bytes_in_sent_files
        bytes_in_sent_files += len(data) + len(filename) + len(client.FILENAME_DELIMITER)

    bytes_sent = wide_area_network.get_total_bytes_sent()

    reduction = (float(bytes_in_sent_files - bytes_sent)
                 / float(bytes_in_sent_files))
    if (reduction < expected_value):
        raise Exception("data_reduction_random_edit_file failed," +
                        " because reduciton ratio should be greater than " +
                        " {}, was {}.".format(expected_value, reduction))


def cross_sending(middlebox_module, testing_part_1):
    """ Tests that a large file without a delimeter will be sent correctly
    Only works for a  a
    """
    filename = "Diamond_top.txt"
    block1 = "a" * 8000
    block2 = "b" * 8000
    block3 = "c" * 8000
    expected_value = .88
    if testing_part_1:
        delimeter = ""
        combo1 = [block1[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block2, block3]
        combo2 = [block1[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block3, block2]
        combo3 = [block2[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block1, block3]
        combo4 = [block2[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block3, block1]
        combo5 = [block3[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block1, block2]
        combo6 = [block3[:8000 - len(filename) - len(client.FILENAME_DELIMITER)], block2, block1]
    else:
        delimeter = " straight chin suggestive of resolution pushed t"
        combo1 = [delimeter, block1, block2, block3]
        combo2 = [delimeter, block1, block3, block2]
        combo3 = [delimeter, block2, block1, block3]
        combo4 = [delimeter, block2, block3, block1]
        combo5 = [delimeter, block3, block1, block2]
        combo6 = [delimeter, block3, block2, block1]

    combos = [combo1, combo2, combo3, combo4, combo5, combo6]
    filename = "Diamond_top.txt"
    files = []
    for combo in combos:
        files.append(delimeter.join(combo))


    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize clients connected to middlebox 1.
    client1_address = "1.2.3.4"
    client2_address = "1.3.4.2"
    client3_address = "1.4.2.3"
    client1 = client.EndHost("client1", client1_address, middlebox1)
    client2 = client.EndHost("client2", client2_address, middlebox1)
    client3 = client.EndHost("client3", client3_address, middlebox1)

    # Initialize clients connected to middlebox 2.
    client4_address = "5.6.7.8"
    client5_address = "5.8.7.6"
    client6_address = "5.7.6.8"
    client4 = client.EndHost("client4", client4_address, middlebox2)
    client5 = client.EndHost("client5", client5_address, middlebox2)
    client6 = client.EndHost("client6", client6_address, middlebox2)

    bytes_in_sent_files = 0
    for data in files:
        f = open(filename, 'w')
        f.write(data)
        f.close()

        past2 = wide_area_network.get_total_bytes_sent()
        client1.send_file(filename, client4_address)
        client5.send_file(filename, client2_address)
        client3.send_file(filename, client6_address)
        output_file_name = "{}-{}".format("client2", filename)
        # Removing the output file just created
        os.remove(output_file_name)
        output_file_name = "{}-{}".format("client4", filename)
        # Removing the output file just created
        os.remove(output_file_name)
        output_file_name = "{}-{}".format("client6", filename)
        # Removing the output file just created
        os.remove(output_file_name)
        past = bytes_in_sent_files
        bytes_in_sent_files += (len(data) + len(filename) + len(client.FILENAME_DELIMITER)) * 3

    bytes_sent = wide_area_network.get_total_bytes_sent()

    reduction = (float(bytes_in_sent_files - bytes_sent)
                 / float(bytes_in_sent_files))
    if (reduction < expected_value):
        raise Exception("data_reduction_random_edit_file failed," +
                        " because reduciton ratio should be greater than " +
                        " {}, was {}.".format(expected_value, reduction))

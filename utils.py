def eth_topic_to_address(topic, length):
    address = int(topic, base=16)
    address = "{0:#0{1}x}".format(address, length)
    return address

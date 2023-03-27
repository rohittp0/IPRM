from myhdl import block, always_comb, Signal, always, intbv


@block
def manchester_decoder(clk, encoded, decoded, trigger_out):
    # Register to hold the last Manchester-encoded bit
    last_bit = Signal(bool(0))

    i = Signal(intbv(0))

    # Manchester decoding logic
    @always(clk.posedge)
    def manchester_decode():
        if trigger_out:
            return

        if i.val % 2:
            if last_bit and not encoded:
                decoded.next[i.val // 2] = 0
            elif not last_bit and encoded:
                decoded.next[i.val // 2] = 1
            elif not last_bit and not encoded:
                trigger_out.next = 1
            elif last_bit and encoded:
                raise ValueError('Invalid Manchester code 11')
        else:
            last_bit.next = encoded

        i.next = i + 1

    return manchester_decode


@block
def ip_parser(decoded, source_port, dest_port, data, trigger_in):
    # Constants for the UDP header fields
    SRC_PORT_OFFSET = 0
    DST_PORT_OFFSET = 2
    LENGTH_OFFSET = 4
    CHECKSUM_OFFSET = 6
    DATA_OFFSET = 8

    # Constants for the IP header fields
    SRC_IP_OFFSET = 12
    DST_IP_OFFSET = 16
    PROTOCOL_OFFSET = 20

    # Constants for the Ethernet header fields
    SRC_MAC_OFFSET = 6
    DST_MAC_OFFSET = 0
    ETHERTYPE_OFFSET = 12

    # Constants for the UDP protocol
    UDP_PROTOCOL = 17

    # Constants for the Ethernet II frame type
    ETHERTYPE_IPV4 = 0x0800

    # Define input and output signals
    @always_comb
    def logic():
        if not trigger_in:
            return

        # Extract Ethernet header fields
        # src_mac = decoded[SRC_MAC_OFFSET + 6:SRC_MAC_OFFSET]
        # dst_mac = decoded[DST_MAC_OFFSET + 6:DST_MAC_OFFSET]
        ethertype = int.from_bytes(decoded[ETHERTYPE_OFFSET + 2:ETHERTYPE_OFFSET], byteorder='big')

        # Only parse IPv4 UDP packets
        if ethertype == ETHERTYPE_IPV4 and decoded[PROTOCOL_OFFSET] == UDP_PROTOCOL:
            # src_ip = decoded[SRC_IP_OFFSET + 4:SRC_IP_OFFSET]
            # dst_ip = decoded[DST_IP_OFFSET + 4:DST_IP_OFFSET]
            udp_header = decoded[DATA_OFFSET + 8:DATA_OFFSET]
            udp_data = decoded[DATA_OFFSET + 8:]

            # Extract UDP header fields
            source_port.next = int.from_bytes(udp_header[SRC_PORT_OFFSET + 2:SRC_PORT_OFFSET], byteorder='big')
            dest_port.next = int.from_bytes(udp_header[DST_PORT_OFFSET + 2:DST_PORT_OFFSET], byteorder='big')

            # Copy UDP data
            data.next = udp_data

    # Return the logic process
    return logic


# @block
# def manchester_encoder(clk, data, encoded):
#     @always_seq(clk.posedge, reset=None)
#     def encode_process():
#         for i in range(int(len(data) / 2)):
#             if data[i * 2] and data[i * 2 + 1]:
#                 encoded[i] = 1
#             elif not data[i * 2] and data[i * 2 + 1]:
#                 encoded[i] = 0
#             else:
#                 # Invalid Manchester code
#                 pass
#
#     return encode_process


@block
def top(clk, encoded, decoded, source_port, dest_port, data):
    # Instantiate decoder, parser, and encoder blocks
    trigger = Signal(bool(0))

    decode_inst = manchester_decoder(clk, encoded, decoded, trigger)
    parse_inst = ip_parser(decoded, source_port, dest_port, data, trigger)
    # encode_inst = manchester_encoder(clk, data, encoded)

    return decode_inst, parse_inst  # , encode_inst

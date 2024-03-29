def generate_frame_checksum(frame: bytes) -> bytes:
    """
    Generate frame checksum
    :param frame: ethernet frame
    :return: frame checksum
    """
    # Define the polynomial and initial CRC value for the CRC32 BZIP2 algorithm
    poly = 0x04c11db7
    init_crc = 0xffffffff

    # Initialize the CRC to the initial value
    crc = init_crc

    # Calculate the CRC over the frame
    for byte in frame:
        crc ^= byte << 24
        for i in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ poly
            else:
                crc = crc << 1
        crc &= 0xffffffff  # mask to keep crc within 32-bit range

    # Complement the CRC and return it as a bytearray in big-endian order
    crc = crc ^ 0xffffffff
    fcs_bytes = crc.to_bytes(4, byteorder='big')

    return fcs_bytes


def generate_ip_checksum(header: bytes) -> bytes:
    """
    Calculate IP header checksum
    :param header: IP header as bytearray
    :return: checksum as 2-byte value
    """
    checksum = 0
    for i in range(0, len(header), 2):
        word = (header[i] << 8) + header[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    checksum = ~checksum & 0xffff

    return checksum.to_bytes(2, byteorder='big')


def pack_udp(src_port: int, dst_port: int, data: bytes) -> bytes:
    """
    Pack UDP packet
    :param src_port: source port
    :param dst_port: destination port
    :param data: UDP payload
    :return: UDP packet as bytes
    """
    # UDP header
    udp_header = bytearray()
    udp_header.extend(src_port.to_bytes(2, byteorder='big'))
    udp_header.extend(dst_port.to_bytes(2, byteorder='big'))
    udp_header.extend((8 + len(data)).to_bytes(2, byteorder='big'))
    udp_header.extend((0).to_bytes(2, byteorder='big'))
    udp_header.extend(data)

    return bytes(udp_header)


def pack_ip(src_ip: bytes, dst_ip: bytes, protocol: int, data: bytes) -> bytes:
    """
    Pack IP packet
    :param src_ip: source IP address
    :param dst_ip: destination IP address
    :param protocol: IP protocol
    :param data: IP payload
    :return: IP packet as bytes
    """
    # IP header
    ip_header = bytearray()
    ip_header.extend((0x45).to_bytes(1, byteorder='big'))
    ip_header.extend((0x00).to_bytes(1, byteorder='big'))
    ip_header.extend((20 + len(data)).to_bytes(2, byteorder='big'))
    ip_header.extend((0).to_bytes(2, byteorder='big'))
    ip_header.extend((0x40).to_bytes(1, byteorder='big'))
    ip_header.extend((0x00).to_bytes(1, byteorder='big'))
    ip_header.extend((0x40).to_bytes(1, byteorder='big'))
    ip_header.extend(protocol.to_bytes(1, byteorder='big'))
    ip_header.extend((0).to_bytes(2, byteorder='big'))  # placeholder for checksum
    ip_header.extend(src_ip)
    ip_header.extend(dst_ip)

    # calculate and update checksum
    ip_header[10:12] = generate_ip_checksum(ip_header)
    ip_header.extend(data)

    return bytes(ip_header)


def pack_ethernet(src_mac: bytes, dst_mac: bytes, data: bytes) -> bytes:
    """
    Pack Ethernet packet
    :param src_mac: source MAC address
    :param dst_mac: destination MAC address
    :param data: Ethernet payload
    :return: Ethernet packet as bytes
    """
    # Ethernet header
    ethernet_header = bytearray()
    ethernet_header.extend(dst_mac)
    ethernet_header.extend(src_mac)
    ethernet_header.extend((0x0800).to_bytes(2, byteorder='big'))
    ethernet_header.extend(data)
    ethernet_header.extend(generate_frame_checksum(ethernet_header))

    return bytes(ethernet_header)


def manchester_encode(data: bytes, reverse: bool = True) -> list:
    """
    Encode a byte array using Manchester encoding
    :param reverse: Reverses the data bit vice before encoding
    :param data: Data to be encoded
    :return: encoded data as list of 1s and 0s
    """
    encoded = []

    ONE = [1, 0] if reverse else [0, 1]
    ZERO = [0, 1] if reverse else [1, 0]

    for byte in data:
        for i in range(7, -1, -1):
            if byte & (1 << i):
                encoded.append(ONE)
            else:
                encoded.append(ZERO)

    enc = []

    for e in encoded:
        enc.extend(e)

    return enc


def pack(src_mac: str, dst_mac: str, src_ip: str, dst_ip: str, src_port: int, dst_port: int, data: bytes) -> bytes:
    """
    Pack Ethernet packet
    :param src_mac: source MAC address
    :param dst_mac: destination MAC address
    :param src_ip: source IP address
    :param dst_ip: destination IP address
    :param src_port: source port
    :param dst_port: destination port
    :param data: Ethernet payload
    :return: Ethernet packet as bytes
    """

    src_mac = bytes.fromhex(src_mac.replace(':', ''))
    dst_mac = bytes.fromhex(dst_mac.replace(':', ''))
    src_ip = bytes([int(x) for x in src_ip.split('.')])
    dst_ip = bytes([int(x) for x in dst_ip.split('.')])

    udp = pack_udp(src_port, dst_port, data)
    ip = pack_ip(src_ip, dst_ip, 0x11, udp)
    ethernet = pack_ethernet(src_mac, dst_mac, ip)

    return ethernet

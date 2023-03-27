from typing import Tuple, Dict

from scripts.pack import generate_frame_checksum


def verify_frame_checksum(frame: bytes) -> None:
    """
    Verify frame checksum
    :param frame: Ethernet frame as bytes
    :raises AssertionError: if checksum is invalid
    :return: None
    """
    received_checksum = frame[:-4]
    received_frame = frame[:-4]

    calculated_checksum = generate_frame_checksum(received_frame)

    assert received_checksum == calculated_checksum, \
        'Invalid checksum, expected {}, got {}'.format(received_frame, calculated_checksum)


def unpack_ethernet(packet: bytes) -> Tuple[bytes, bytes, bytes]:
    """
    Unpack Ethernet packet
    :param packet: Ethernet packet as bytes
    :return: source MAC address, destination MAC address, Ethernet payload
    """
    verify_frame_checksum(packet)

    src_mac = packet[0:6]
    dst_mac = packet[6:12]
    data = packet[14:]

    return src_mac, dst_mac, data


def unpack_ip(packet: bytes) -> Tuple[bytes, bytes, int, bytes]:
    """
    Unpack IP packet
    :param packet: IP packet as bytes
    :return: source IP address, destination IP address, IP protocol, IP payload
    """
    src_ip = packet[12:16]
    dst_ip = packet[16:20]
    protocol = packet[9]
    data = packet[20:]

    return src_ip, dst_ip, protocol, data


def unpack_udp(packet: bytes) -> Tuple[int, int, bytes]:
    """
    Unpack UDP packet
    :param packet: UDP packet as bytes
    :return: source port, destination port, UDP payload
    """
    src_port = int.from_bytes(packet[0:2], byteorder='big')
    dst_port = int.from_bytes(packet[2:4], byteorder='big')
    data = packet[8:]

    return src_port, dst_port, data


def parse_mac(mac: bytes) -> str:
    """
    Parse MAC address
    :param mac: MAC address as bytes
    :return: MAC address as string
    """
    return ':'.join(['{:02x}'.format(b) for b in mac])


def parse_ip(ip: bytes) -> str:
    """
    Parse IP address
    :param ip: IP address as bytes
    :return: IP address as string
    """
    return '.'.join([str(b) for b in ip])


def unpack(packet: bytes) -> Dict[str, bytes]:
    """
    Unpack Ethernet, IP and UDP packet
    :param packet: Ethernet, IP and UDP packet as bytes
    :return: source MAC address, destination MAC address, source IP address, destination IP address, source port, destination port, UDP payload
    """
    src_mac, dst_mac, data = unpack_ethernet(packet)
    src_ip, dst_ip, protocol, data = unpack_ip(data)
    src_port, dst_port, data = unpack_udp(data)

    src_mac, dst_mac = parse_mac(src_mac), parse_mac(dst_mac)
    src_ip, dst_ip = parse_ip(src_ip), parse_ip(dst_ip)

    return {'src_mac': src_mac, 'dst_mac': dst_mac, 'src_ip': src_ip, 'dst_ip': dst_ip, 'src_port': src_port,
            'dst_port': dst_port, 'data': data}

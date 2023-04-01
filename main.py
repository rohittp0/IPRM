from pprint import pprint

from tabulate import tabulate

from scripts.pack import pack
from scripts.unpack import unpack


def bhex(bytes_: bytes):
    return bytes_.hex(sep=".")


def int_to_bits(b: str) -> str:
    bits = [b[i:i + 8] for i in range(0, len(b), 8)]
    headers = ['Byte Index', *range(len(bits))]
    bits = ['Bits'] + bits
    hexs = ['Hex'] + [int(x, 2).to_bytes(1, "little") for x in bits[1:]]
    return tabulate([bits, hexs], headers=headers, tablefmt='grid')


def bytes_to_string(bytes_: bytes) -> str:
    ret = ""
    for byte in bytes_:
        for i in range(7, -1, -1):
            if byte & (1 << i):
                ret += "1"
            else:
                ret += "0"

    return ret


def print_packet(packet: bytes):
    """
    Prints the packet in hex formatted into table correctly according to the Ethernet standard
    and IP standard.

    :param packet:
    :return: None
    """

    print("Ethernet Header")
    print("{} {}".format(bhex(packet[:6]), bhex(packet[6: 12])))
    print("{} {}".format(bhex(packet[12: 14]), bhex(packet[-4:])))
    print("\nIP Header")
    print("{} {} {} {}".format(bhex(packet[14: 18]), bhex(packet[18: 22]),
                               bhex(packet[22: 25]), bhex(packet[25: 30]), bhex(packet[30: 46])))
    print("{} {} {} {}".format(bhex(packet[46: 48]), bhex(packet[48: 50]),
                               bhex(packet[50: 52]), bhex(packet[52: 54])))


def main():
    packet = pack(
        src_mac="00:00:00:00:00:01",
        dst_mac="00:00:00:00:00:02",
        src_ip="192.168.1.2",
        dst_ip="192.168.1.3",
        src_port=8000,
        dst_port=8001,
        data=b"Hello World!"
    )

    print_packet(packet)

    unpacked = unpack(packet)

    print("\nUnpacked packet:")
    pprint(unpacked, sort_dicts=False)


if __name__ == "__main__":
    main()

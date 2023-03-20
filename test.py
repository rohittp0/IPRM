import random
from myhdl import block, instance, Signal, delay, intbv

from switch import top


def get_packet():
    # Generate a random packet
    src_ip = bytes([random.randint(0, 255) for _ in range(4)])
    dst_ip = bytes([random.randint(0, 255) for _ in range(4)])
    src_port = 8000
    dst_port = 8080
    payload_len = 256  # Hard-coded because I am lazy
    payload = bytes([random.randint(0, 255) for _ in range(payload_len)])

    # Construct the packet
    ethernet_header = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00])
    udp_header = int.to_bytes(src_port, 2, byteorder='big') + int.to_bytes(dst_port, 2, byteorder='big') + \
                 int.to_bytes(payload_len + 8, 2, byteorder='big') + bytes([0, 0]) + payload
    ip_header = bytes([0x45, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x40, 0x11, 0x00, 0x00]) + \
                src_ip + dst_ip + udp_header

    # Encode the packet
    # encoded_packet = bytearray()
    # for byte in ethernet_header + ip_header:
    #     encoded_packet.extend([byte])
    # encoded_int = int.from_bytes(encoded_packet, byteorder='big')

    return ethernet_header + ip_header


def manual_manchester(data: bytes):
    """
    Encode a byte array using Manchester encoding
    :param data:
    :return: encoded data as string of 1s and 0s
    """
    for byte in data:
        for i in range(8):
            if byte & (1 << i):
                yield 0
                yield 1
            else:
                yield 1
                yield 0


@block
def test_bench():
    clk = Signal(bool(0))
    encoded = Signal(bool(0))
    decoded = Signal(intbv(0)[2384:])
    source_port = Signal(intbv(0)[16:])
    dest_port = Signal(intbv(0)[16:])
    data = Signal(intbv(0)[640:])

    # Instantiate the design under test
    dut = top(clk, encoded, decoded, source_port, dest_port, data)

    packet = get_packet()
    manchester = manual_manchester(packet)
    print('Packet: {}'.format(packet))
    print('Packet Length: {}'.format(len(packet)))

    # Clock generator
    @instance
    def clock_gen():
        while True:
            clk.next = not clk
            yield delay(10)

    @instance
    def driver():
        for bit in manchester:
            encoded.next = bit
            yield clk.posedge

        print("Done sending packet")

        while True:
            encoded.next = 0
            yield clk.posedge

    # Monitor the output
    @instance
    def monitor():
        yield clk.posedge
        while True:
            yield delay(10000)

            # print('Source port: {}'.format(source_port))
            # print('Destination port: {}'.format(dest_port))
            # print('Encoded: {}'.format(encoded))
            # print('Data: {}'.format(data))
            # print('-' * 80)
            # if data != payload:
            #     raise ValueError('Data mismatch')
            # if source_port != src_port:
            #     raise ValueError('Source port mismatch')
            # if dest_port != dst_port:
            #     raise ValueError('Destination port mismatch')
            # print('Packet received successfully')

    return dut, clock_gen, monitor, driver


if __name__ == '__main__':
    # Simulate the test bench
    tb = test_bench()
    # tb.config_sim(trace=True)
    tb.run_sim()

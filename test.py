from myhdl import block, instance, Signal, delay, intbv

from main import int_to_bits
from scripts.pack import pack, manchester_encode
from switch import top


@block
def test_bench():
    clk = Signal(bool(0))
    encoded = Signal(bool(0))
    decoded = Signal(intbv(0)[464:])
    source_port = Signal(intbv(0)[16:])
    dest_port = Signal(intbv(0)[16:])
    data = Signal(intbv(0)[32:])

    # Instantiate the design under test
    dut = top(clk, encoded, decoded, source_port, dest_port, data)

    packet = pack(
        src_mac="00:00:00:00:00:01",
        dst_mac="00:00:00:00:00:02",
        src_ip="192.168.1.2",
        dst_ip="192.168.1.3",
        src_port=8000,
        dst_port=8001,
        data=b"Hello World!"
    )

    manchester = manchester_encode(packet)
    print('Packet: \n{}'.format(int_to_bits(int.from_bytes(packet, byteorder='big'))))
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

            print('Source port: {}'.format(source_port))
            print('Destination port: {}'.format(dest_port))
            print('Encoded: {}'.format(encoded))
            print('Data: {}'.format(data))
            print('-' * 80)
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


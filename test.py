from myhdl import block, instance, Signal, delay, intbv

from main import int_to_bits, bytes_to_string
from scripts.pack import pack, manchester_encode
from switch import top


@block
def test_bench():
    clk = Signal(bool(0))
    encoded = Signal(bool(0))
    decoded = Signal(intbv(0)[464:])
    source_port = Signal(intbv(0)[16:])
    dest_port = Signal(intbv(0)[16:])
    data = Signal(intbv(0)[96:])

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
    print('Packet: \n{}'.format(int_to_bits(bytes_to_string(packet))))
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

            txt = [int(data[i + 8: i]).to_bytes(1, "little") for i in range(0, len(data), 8)]

            print('Source port: {}'.format(int(source_port)))
            print('Destination port: {}'.format(int(dest_port)))
            print('Data: {}'.format(txt[::-1]))
            print('Encoded: {}'.format(encoded))
            print('-' * 80)

    return dut, clock_gen, monitor, driver


if __name__ == '__main__':
    # Simulate the test bench
    tb = test_bench()
    # tb.config_sim(trace=True)
    tb.run_sim()


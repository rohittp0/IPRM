from myhdl import block, delay, always, now, Signal, instance, instances, Simulation, intbv, concat, always_comb


@block
def clock_gen(clk, period=20):

    lowTime = int(period / 2)
    highTime = period - lowTime

    @instance
    def drive_clk():
        while True:
            yield delay(lowTime)
            clk.next = 1
            yield delay(highTime)
            clk.next = 0

    return drive_clk


@block
def manchester_rx(clk, data_in, port_in):
    # Create a clock domain for Manchester decoding
    manchester_clk = Signal(bool(0))

    # Register to hold the last Manchester-encoded bit
    last_bit = Signal(bool(0))

    # Register to hold the current decoded bit
    decoded_bit = Signal(bool(0))

    # Manchester decoding logic
    @always(clk.posedge)
    def manchester_decode():
        # Shift the last bit into the MSB of the current data word
        data_word = concat(last_bit, data_in)

        # If the data word is a valid Manchester code, decode it
        if data_word == intbv('01'):
            decoded_bit.next = 0
        elif data_word == intbv('10'):
            decoded_bit.next = 1
        else:
            decoded_bit.next = decoded_bit

        # Shift the current bit into the last bit register
        last_bit.next = decoded_bit

    # Destination port lookup table
    port_table = {1: 2, 2: 1, 3: 4, 4: 3}

    # Register to hold the current destination port
    dest_port = Signal(intbv(0)[3:])

    # Register to hold the current Manchester-encoded bit
    encoded_bit = Signal(bool(0))

    # Manchester encoding logic
    @always_comb
    def manchester_encode():
        # Get the current destination port based on the incoming port and switch table
        dest_port.next = port_table[int(port_in)]

        # If the destination port is different from the incoming port, encode and transmit the packet
        if dest_port != port_in:
            if encoded_bit:
                # Transmit a 10 Manchester code
                data_out.next = intbv('10')
                encoded_bit.next = 0
            else:
                # Transmit a 01 Manchester code
                data_out.next = intbv('01')
                encoded_bit.next = 1
        else:
            # Don't transmit the packet if it's destined for the same port
            data_out.next = 0
            encoded_bit.next = 0

    # Register to hold the current Manchester-encoded data word
    data_out = Signal(intbv(0)[2:])

    return manchester_decode, manchester_encode, data_out

@block
def top(clk, rx, tx):
    rx_ip = Signal(bool(0))
    rx_udp = Signal(intbv(0)[16:])

    ethernet = parse_ethernet(clk, rx=rx, out=rx_ip)
    ip = parse_ip(rx=rx_ip, out=rx_udp)
    udp = parse_udp(clk=rx_ip, rx=rx_udp, tx=tx)

    return instances()


@block
def test_bench(clk, rx, tx, in_packets):
    @always(clk.posedge)
    def tb():
        rx.next = in_packets.pop()
        print(int(tx), end='')

    return tb


def main():
    data = [bool(int(x)) for x in "0000010101010101011"]
    period = 20

    signal_in = Signal(bool(1))
    signal_out = Signal(bool(0))
    clk = Signal(bool(0))

    clk_gen = clock_gen(clk, period=period)
    inst = top(clk, signal_in, signal_out)

    tester = test_bench(clk, signal_in, signal_out, data)

    Simulation(clk_gen, inst, tester).run(period * len(data))

    inst.convert(hdl='Verilog', initial_values=True, directory='verilog', name='pass_through')


if __name__ == '__main__':
    main()

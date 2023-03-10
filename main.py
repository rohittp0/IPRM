from myhdl import block, delay, always, now, Signal, instance, instances, Simulation, intbv


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
def parse_ethernet(clk: Signal, rx: Signal, out: Signal):
    last = Signal(bool(0))

    @always(clk.posedge)
    def parse():
        if rx != last:
            out.next = rx
        last.next = rx

    return parse


@block
def parse_ip(rx: Signal, out: Signal):
    n = Signal(intbv(0, min=0, max=len(out)))

    @always(rx.posedge, rx.negedge)
    def parse():
        out.next[n.val] = rx
        n.next = n + 1
        if n.val == len(out):
            n.next = 0

    return parse


@block
def parse_udp(clk, rx, tx):
    n = Signal(intbv(0, min=0, max=len(rx)))

    @always(clk.posedge)
    def parse():
        tx.next = rx[n.val]
        n.next = n + 1
        if n == 16:
            n.next = 0

    return parse


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

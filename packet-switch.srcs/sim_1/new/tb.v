module tb_pass_through;

reg clk;
reg encoded;
wire [463:0] decoded;
wire [15:0] source_port;
wire [15:0] dest_port;
wire [95:0] data;

initial begin
    $from_myhdl(
        clk,
        encoded
    );
    $to_myhdl(
        decoded,
        source_port,
        dest_port,
        data
    );
end

initial begin
    forever
    begin
        #5 clk = ~clk;
    end
end

pass_through dut(
    clk,
    encoded,
    decoded,
    source_port,
    dest_port,
    data
);



endmodule

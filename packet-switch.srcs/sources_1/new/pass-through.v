`timescale 1ns/10ps

module pass_through (
    clk,
    rx,
    tx
);


input clk;
input rx;
output tx;
reg tx;

reg rx_ip = 0;
reg [15:0] rx_udp = 0;
reg parse_ethernet0_last = 0;
reg [3:0] parse_ip0_n = 0;
reg [3:0] parse_udp0_n = 0;



always @(posedge clk) begin: PASS_THROUGH_PARSE_ETHERNET0_PARSE
    if ((rx != parse_ethernet0_last)) begin
        rx_ip <= rx;
    end
    parse_ethernet0_last <= rx;
end


always @(posedge clk) begin: PASS_THROUGH_PARSE_IP0_PARSE
    rx_udp[parse_ip0_n] <= rx_ip;
    parse_ip0_n <= (parse_ip0_n + 1);
    if ((parse_ip0_n == 16)) begin
        parse_ip0_n <= 0;
    end
end


always @(posedge rx_ip) begin: PASS_THROUGH_PARSE_UDP0_PARSE
    tx <= rx_udp[parse_udp0_n];
    parse_udp0_n <= (parse_udp0_n + 1);
    if ((parse_udp0_n == 16)) begin
        parse_udp0_n <= 0;
    end
end

endmodule

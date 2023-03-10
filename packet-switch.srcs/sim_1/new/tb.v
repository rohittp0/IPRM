`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 10.03.2023 21:32:15
// Design Name:
// Module Name: tb
// Project Name:
// Target Devices:
// Tool Versions:
// Description:
//
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////


module tb();

reg clk;
reg rx;
wire tx;

pass_through uut (
    .clk(clk),
    .rx(rx),
    .tx(tx)
);


initial begin
    clk = 0;
    rx = 0;
end

initial begin
    forever #5 clk = ~clk;
end

initial begin
    forever #10 rx = ~rx;
end

endmodule

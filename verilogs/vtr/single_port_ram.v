module single_port_ram(clk, data, we, addr, out);

    parameter ADDR_WIDTH = 8;
    parameter DATA_WIDTH = 8;

    input 				clk;
    input	[DATA_WIDTH-1:0] 	data;
    input 				we;
    input	[ADDR_WIDTH-1:0] 	addr;

    
    output	[DATA_WIDTH-1:0] 	out;
    reg		[DATA_WIDTH-1:0] 	out;
     
    reg 	[DATA_WIDTH-1:0] 	RAM[255:0];
     
    always @ (posedge clk) begin
        if (we) begin
            RAM[addr] <= data;
        end
    end

    always @ (posedge clk) begin
        if (!we) begin
            out <= RAM[addr];
        end
    end

endmodule
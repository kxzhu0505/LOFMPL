module dual_port_ram(
    clk,
    we1,
    we2,
    data1,
    data2,
    out1,
    out2,
    addr1,
    addr2
);

    parameter ADDR_WIDTH = 7;
    parameter DATA_WIDTH = 1024;

    input  clk;

    input  we1;
    input  [ADDR_WIDTH-1:0] addr1;
    input  [DATA_WIDTH-1:0] data1;
    output [DATA_WIDTH-1:0] out1;
    reg    [DATA_WIDTH-1:0] out1;

    input  we2;
    input  [ADDR_WIDTH-1:0] addr2;
    input  [DATA_WIDTH-1:0] data2;
    output [DATA_WIDTH-1:0] out2;
    reg    [DATA_WIDTH-1:0] out2;

    reg    [DATA_WIDTH-1:0] 	RAM[255:0];

    // Memory Write Block
    always @ (posedge clk) begin
        if ( we1 ) begin
            RAM[addr1] <= data1;
        end
    end
    always @ (posedge clk) begin
        if ( we2 ) begin
            RAM[addr2] <= data2;
        end
    end

    // Memory Read Block
    always @ (posedge clk) begin
        if ( !we1 ) begin
            out1 <= RAM[addr1]; 
        end
    end
    always @ (posedge clk) begin
        if ( !we2 ) begin
            out2 <= RAM[addr2]; 
        end
    end


endmodule
## Variable to define the type of MVMU
# One of "Analog", "Digital" (To be added), "PNM" (To be added)
MVMU_ver = "Analog"

## Operand precision (fixed point allowed only): num_bits = int_bits + frac_bits
num_bits = 16

## IMA configurable parameters (permissible values for each parameter provided here)
## Instruction generation - affected by xbar_bits, num_xbar, xbar_size.
# xbar_bits: 2, 4, 6
# num_xbar: positive integer
# xbar_size: 32, 64, 128, 256
# dac_res: positive integer <= num_bits
# adc_res: positive integer <= num_bits
# num_adc: positive integer <= num_xbar (doesn't allow more than one ADC per xbar)
# num_ALU: positive integer
# dataMem_size: (in Bytes) - 256, 512, 1024, 2048 (affects instrn width, hence capped)
# instrnMem_size: (in Bytes) - 512, 1024, 2048

# Fixed parameters
addr_width = 32 # Added to address larger address space for conv layers (#TODO: Compiler needs to fix shared memory reuse)
data_width = num_bits # (in bits)
xbdata_width = data_width # (in bits)
instrn_width = 48 # (in bits)


# Input and Weight parameters
input_prec = 16
weight_width = 16
# Change here - Specify the IMA parameters here
xbar_bits = 2

#FIXME make num_matrix equal to N_CONSTANT_MVMUS_PER_CORE 
num_matrix = 4 # each matrix is 1-fw logical xbar for inference and 1-fw, 1-bw, and 1 delta logical xbar for training. Each logical xbar for inference is 8-fw physical xbar and for training  8-fw, 8-bw and 16-delta physical xbars.
xbar_size = 128
dac_res = 1
# ADC configuration
adc_res = 8 # around 4 to 8. this value should be
num_adc_per_matrix = 2
num_adc = num_adc_per_matrix * num_matrix

# The idea is to have different ADC resolution value for each ADC.
# The number of ADC if defined by num_adc property. Currently it is 2 * num_matrix(2) = 4
# NOTE: Only taking in account indexes 0 and 2, 1 and 3 are ignored, because ADCs 1 and 3 are assumed t be equal to 0 and 2. 

num_ALU = num_matrix*2
#dataMem_size = num_matrix*(6*xbar_size) # 4 for 4 input spaces within matrix (1 for f/b each, 2 for d)
dataMem_size = 2048 # 2048 is larger than num_matrix*(6*xbar_size)
instrnMem_size = 512 #in entries

## Tile configurable parameters (permissible values for each parameter provided here)
## Instruction generation - affected by num_ima
# num_ima: positive integer
# edram buswidth: positive integer <= 16 (actual buswidth - this integer*data_width)
# edram_size: (in KiloBytes) - 64, 128, 256, 512
# receive_buffer_depth: 4, 8, 12, 16, 32 (number of edram buffer entries (each entry maps to a virtual tile)) \
#        puts a cap on the maximum num ber of tiles that can send data to a tile in next layer
# receive_buffer_width: edram_buswidth/data_width (Fixed - in terms of number of neurons)
# tile_instrnMem_size: 256, 512, 1024 (in Bytes)

# Fixed parameters
instrn_width = 48 # bits (op-2, vtile_id-6, send/receive_width-8, target_addr/counter-16, vw-8, mem_addr-16)
edram_buswidth = 256 # in bits
#receive_buffer_depth = 16
receive_buffer_depth = 150 #set equal to num_tile_max
receive_buffer_width =  edram_buswidth / num_bits # size of receive buffeer entry (in terms of number of neurons)

# Change here - Specify the Tile parameters here
num_ima = 8
edram_size = 64 # in Kilobytes (64 KB - same as issac)
tile_instrnMem_size = 2048 # in entries

## Node configurable parameters (permissible values for each parameter provided here)
## Instruction generation - affected by num_tile
# num_tile_compute =  positive integer
# inj_rate < 0.2 (depends on the mapping)
# num_port: 4, 8

# Fixed parameters
# NOC topology: cmesh (n=2, k=4, c=4) - can fit k*n*c tiles
cmesh_c = 4
num_bits_tileId =32
flit_width = 32
packet_width = edram_buswidth/data_width #in multiples of flits (data considered only - booksim consider address itself)
# (b bit of address = logN, N is the number of nodes)


## Node parameters - Our way of simulation just assumes all tile in one actual node
# Change here - Specify the Node parameters here (FIXME to be supported)
num_node = 1
num_tile_max = 138.0 # maximum number of tiles per node

# Define the instruction prototypes which will be used by the generate_instrn.py file
import sys

import numpy as np
import config as cfg

# List of supported opcodes for tile
op_list_tile = ['send', 'receive', 'compute', 'halt']

# Instruction format for Tile
dummy_instrn_tile = {'opcode' : op_list_tile[0],
                     'mem_addr': 0,     # send/receive - edram_addr
                     'r1': 0,     # send-send_width, receive-receive_width
                     'r2': 0,     # send-target_addr, receive-counter
                     'vtile_id': 0, # send/receive-neuron_id
                     'ima_nma': '',      # compute - a bit for each ima
                     'vec': 0} # vector width

# Define instruction prototypes
# generate receive prototype
def i_receive (mem_addr, vtile_id, receive_width, counter, vec = 1):
    i_temp = dummy_instrn_tile.copy()
    i_temp['opcode'] = 'receive'
    i_temp['mem_addr'] = mem_addr
    i_temp['vtile_id'] =  vtile_id
    i_temp['r1'] = receive_width
    i_temp['r2'] = counter
    i_temp['vec'] = vec
    return i_temp

# generate send prototype
def i_send (mem_addr, vtile_id, send_width, target_addr, vec = 1):
    i_temp = dummy_instrn_tile.copy()
    i_temp['opcode'] = 'send'
    i_temp['mem_addr'] = mem_addr
    i_temp['vtile_id'] = vtile_id
    i_temp['r1'] = send_width
    i_temp['r2'] = target_addr
    i_temp['vec'] = vec
    return i_temp

# generate halt prototype
def i_halt ():
    i_temp = dummy_instrn_tile.copy()
    i_temp['opcode'] = 'halt'
    return i_temp




# Define the instruction prototypes which will be used by the generate_instrn.py file
import sys

import numpy as np
from data_convert import *
import config as cfg

from data_convert import *

# List of supported opcodes/aluops for IMA - cp will copy data (from data memory of ima to xbarInmem)
op_list = ['ld', 'cp', 'st', 'set', 'nop', 'alu', 'alui', 'mvm', 'vvo', 'hlt', 'jmp', 'beq', 'alu_int', 'crs']
aluop_list = ['add', 'sub', 'sna', 'mul', 'sigmoid'] # sna is also used by mvm isntruction

# Instruction format for IMA
dummy_instrn = {'opcode' : op_list[0],      # instrn op
               'aluop'  : aluop_list[0],   # alu function
               'd1'     : 0,               # destination
               'r1'     : 0,               # operand1 (stride for mvm)
               'r2'     : 0,               # operand2
               'r3'     : 0,               # operand3 (shift)
               'vec'    : 0,               # vector width
               'imm'    : 0,               # immediate (scalar) data
               'xb_nma' : 0 }              # xbar negative-mask, a xbar evaluates if neg-mask = 1


def i_load (d1, r1, load_width = 1, vec = 1):
    assert (load_width <= (cfg.edram_buswidth/cfg.data_width)), 'Load width must be smaller than \
    edram_buswidth/data_width'
    i_temp = dummy_instrn.copy ()
    i_temp['opcode'] = 'ld'
    i_temp['d1'] = d1 # rf addr
    i_temp['r1'] = r1 # mem addr
    i_temp['imm'] = load_width
    i_temp['vec'] = vec
    return i_temp

# generate store protoyype - store data from (datamem/sboutmem) to edram
def i_store (d1, r1, counter = 1, store_width = 1, vec = 1):
    assert (store_width <= (cfg.edram_buswidth/cfg.data_width)), 'Load width must be smaller than \
    edram_buswidth/data_width'
    i_temp = dummy_instrn.copy ()
    i_temp['opcode'] = 'st'
    i_temp['d1'] = d1 # mem addr
    i_temp['r1'] = r1 # rf addr
    i_temp['r2'] = counter
    i_temp['imm'] = store_width
    i_temp['vec'] = vec
    return i_temp

# generate cp prototype:
# src_type = 0: copy data from (datamem/xbInmem) to (datmem/xbInmem)
# src_type = 1: copy data from (datamem/xbOutmem) to (datmem/xbInmem)
def i_copy (d1, r1, vec = 1, src_type = 0):
    i_temp = dummy_instrn.copy ()
    i_temp['opcode'] = 'cp'
    i_temp['d1'] = d1
    i_temp['r1'] = r1
    i_temp['vec'] = vec
    return i_temp

# generate set prototype - set a particular reg value (datamem/xbInmem) to a scalar
def i_set (d1, imm, vec = 1):
    i_temp = dummy_instrn.copy ()
    i_temp['opcode'] = 'set'
    i_temp['d1'] = d1
    i_temp['imm'] = imm if (type(imm) == str) else int2bin(imm, cfg.addr_width)
    i_temp['vec'] = vec
    return i_temp

# generate alu prototype - arithmrtic, logical, non-linear opearrions
def i_alu (aluop, d1, r1, r2=0, imm=0, vec = 1):
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'alu'
    i_temp['aluop'] = aluop
    i_temp['d1'] = d1
    i_temp['r1'] = r1
    i_temp['r2'] = r2
    i_temp['imm'] = imm # will be used in lsh
    i_temp['vec'] = vec
    return i_temp

# generate alui prototype - arithmrtic, logical, non-linear opearrions with scalars
def i_alui (aluop, d1, r1, imm, vec = 1):
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'alui'
    i_temp['aluop'] = aluop
    i_temp['d1'] = d1
    i_temp['r1'] = r1
    i_temp['imm'] = float2fixed (imm, cfg.int_bits, cfg.frac_bits)
    i_temp['vec'] = vec
    return i_temp

# generate mvm prototype - xbar isntrn
def i_mvm (xb_nma = cfg.num_matrix*'0', r1=0, r2=0): # r1 is displacement, r2 is length of a continuum of data
    xb_nma_str = xb_nma[0]
    #xb_nma_str = xb_nma
    xb_nma_list = [xb_nma_str[i]+'00' for i in range(len(xb_nma_str))] # split into list of 3-bit masks
    assert (len(xb_nma_list) == cfg.num_matrix) # each matrix in a core has a 3-bit mask
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'mvm'
    i_temp['r1'] = r1
    i_temp['r2'] = r2
    i_temp['xb_nma'] = xb_nma_list
    return i_temp
    
## Added for COMPILER - i_train, mask as integer
def i_train (xb_nma = cfg.num_matrix*['000'], r1=0, r2=0): # r1 is displacement, r2 is length of a continuum of data
    xb_nma_str = xb_nma[0]
    xb_nma_list = [xb_nma_str[i*3:(i+1)*3] for i in range(len(xb_nma_str)/3)] # split into list of 3-bit masks
    assert (len(xb_nma_list) == cfg.num_matrix) # each matrix in a core has a 3-bit mask
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'mvm'
    i_temp['r1'] = r1
    i_temp['r2'] = r2
    i_temp['xb_nma'] = xb_nma_list
    return i_temp

# generate crs instruction
# for each matrix, one bit to specify whether to do crs or not
def i_crs (xb_nma = cfg.num_matrix*['0']):
    assert (len(xb_nma) == cfg.num_matrix) # each matrix in a core has a 1-bit mask
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'crs'
    i_temp['xb_nma'] = xb_nma
    return i_temp

# generate halt prototype
def i_hlt ():
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'hlt'
    return i_temp

# generate jmp prototype
def i_jmp (imm): # imm is the jump target
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'jmp'
    i_temp['imm'] = imm
    return i_temp

# generate beq prototype
def i_beq (r1, r2, imm): # imm is the jump target
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'beq'
    i_temp['r1'] = r1
    i_temp['r2'] = r2
    i_temp['imm'] = imm
    return i_temp

# generate alu_int prototype
def i_alu_int (aluop, d1, r1, r2):
    i_temp = dummy_instrn.copy()
    i_temp['opcode'] = 'alu_int'
    i_temp['aluop'] = aluop
    i_temp['d1'] = d1
    i_temp['r1'] = r1
    i_temp['r2'] = r2
    return i_temp


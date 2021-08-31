import GlobalVars as gv
import numpy as np
import Operations
from data_convert import *
import Profile as pf
import sys

class Core:
    def __init__(self, num, tile):
        self.num = num
        self.tile = tile
        self.inst_list = self.load_inst()
        self.cyc = 0
        self.pc = 0
        self.work_cyc = 0 # core is busy for next work_cyc
        self.is_halted = False
        self.reg = {}
        
    def load_inst(self):
        filename = "%s/tile%d/core_imem%d.npy" \
            % (gv.params["foldername"], self.tile.num, self.num)
        inst_list = np.load(filename, allow_pickle=True)

        return inst_list

    def debug(self, inst):
        if gv.debug_enabled == False: return
        #if self.cyc > gv.last_debug_cyc: print ("")
        gv.last_debug_cyc = self.cyc
        #print ("[%4d] Tile %d ; Core %2d ; pc %2d: %s    //" 
        #    % (self.cyc, self.tile.num, self.num, self.pc, inst['opcode']), inst)
        sys.stdout.flush();


    def advance(self):
        self.cyc += 1

        if self.is_halted == True:
            return

        if self.work_cyc > 0:
            self.work_cyc -= 1

            if self.work_cyc == 0:
                self.pc += 1
            else: return

        inst = self.inst_list[self.pc]

        if inst['opcode'] == 'st':
            if self.tile.mem_wait == 0:
                mem_addr = self.reg[inst['d1']]
                counter = inst['r2']
                width = inst['imm']
                vec = inst['vec']
                dat = inst['r1']

                #assert (not mem_addr in self.tile.shared_mem)\
                #    or self.tile.shared_mem[mem_addr] == 0

                #self.tile.shared_mem[mem_addr] = counter
                data = 0
                if dat in self.reg: data = self.reg[dat]

                self.tile.memory.allocate(mem_addr, counter, data)

                #self.tile.mem_wait = vec # assuming 1cyc/vec-write
                #self.work_cyc = vec
                self.tile.mem_wait = 1 # assuming 1cyc/vec-write
                self.work_cyc = 1

                self.debug(inst)
                pf.call_stack["Store"] += 1
                    
            else: pass # store block

        elif inst['opcode'] == 'ld':
            if self.tile.mem_wait == 0:
                mem_addr = self.reg[inst['r1']]
                vec = inst['vec']

                #if mem_addr in self.tile.shared_mem\
                #    and self.tile.shared_mem[mem_addr] > 0:
                accessed, data = self.tile.memory.access(mem_addr)
                if accessed:
                    self.reg[inst['d1']] = data

                    #self.tile.mem_wait = vec # assuming 1cyc/vec-read
                    #self.work_cyc = vec
                    self.tile.mem_wait = 1 # assuming 1cyc/vec-read
                    self.work_cyc = 1
                    #self.tile.shared_mem[mem_addr] -= 1
                    #
                    #if self.tile.shared_mem[mem_addr] == 0:
                    #    del self.tile.shared_mem[mem_addr] # free the space

                    self.debug(inst)
                    pf.call_stack["Load"] += 1

            else: pass # load block

        elif inst['opcode'] == 'hlt':
            self.is_halted = True
            self.tile.halted_core_num += 1

            self.debug(inst)

        elif inst['opcode'] == 'alu' or inst['opcode'] == 'alui':
            vec = inst['vec']
            #self.work_cyc = Operations.latency[inst['opcode']] * vec # possible pipelining of multiple vectors / possible parallelization using multiple alu unit
            self.work_cyc = Operations.latency[inst['opcode']] * 1 # possible pipelining of multiple vectors / possible parallelization using multiple alu unit

            self.debug(inst)
            if inst['opcode'] == 'alu': pf.call_stack["ALU"] += 1
            else: pf.call_stack["ALUI"] += 1

        elif inst['opcode'] == 'mvm':
            self.work_cyc += Operations.latency[inst['opcode']]

            self.debug(inst)
            pf.call_stack["MVM"] += 1

        elif inst['opcode'] == 'cp':
            self.work_cyc += Operations.latency[inst['opcode']]

            self.debug(inst)
            pf.call_stack["Copy"] += 1

        elif inst['opcode'] == 'set':
            self.work_cyc += Operations.latency[inst['opcode']]

            reg_addr = inst['d1']
            imm = inst['imm']
            vec = inst['vec']
            #assert vec == 1

            self.reg[reg_addr] = bin2int(imm, 22) # 22: default compiler config - address bit #
            self.debug(inst)
            pf.call_stack["Set"] += 1

        else:
            self.debug(inst)
            raise NotImplementedError


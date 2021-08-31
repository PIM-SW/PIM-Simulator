import numpy as np
import GlobalVars as gv
import Profile as pf
import NoC
import Core
import Memory
import sys

class Tile:
    def __init__(self, num, noc):
        self.num = num
        self.noc = noc
        #self.x, self.y = gv.ind_to_coord(num)
        self.inst_list = self.load_inst()
        self.cyc = 0
        self.pc = 0
        self.send_wait_cyc = 0
        self.is_halted = False
        self.halted_core_num = 0

        self.fifo = [0 for _ in range(gv.fifo_num)] # (# of packets) in the fifo

        self.mem_wait = 0 # how many cycles left to finish serving current request

        self.memory = Memory.Memory(self)
        self.cores = [Core.Core(i, self) for i in range(gv.params["core_num"])]

        self.total_inst = len(self.inst_list)
        for core in self.cores: self.total_inst += len(core.inst_list)


    def load_inst(self):
        filename = "%s/tile%d/tile_imem.npy" % (gv.params["foldername"], self.num)
        inst_list = np.load(filename, allow_pickle=True)
        return inst_list

    def debug(self, inst):
        if gv.debug_enabled == False: return
        #if self.cyc > gv.last_debug_cyc: print ("")
        gv.last_debug_cyc = self.cyc
        #print ("[%4d] Tile %d ;         ; pc %2d: %s    //" % (self.cyc, self.num, self.pc, inst['opcode']), inst)
        sys.stdout.flush();

    def advance(self):

        self.cyc += 1
        if self.is_halted == True:
            return

        if self.mem_wait > 0:
            self.mem_wait -= 1

        if self.send_wait_cyc > 0:
            self.send_wait_cyc -= 1
            
        inst = self.inst_list[self.pc]
        
        if inst['opcode'] == 'send':
            if self.mem_wait == 0:
                mem_addr = inst['mem_addr']
                #if self.num == 0 or \
                #    (mem_addr in self.shared_mem and self.shared_mem[mem_addr] != 0):
                accessed = True
                if self.num != 0: accessed, data = self.memory.access(mem_addr)
                if accessed:

                    vtile_id = inst['vtile_id']
                    send_width = inst['r1']
                    target_tile_num = inst['r2']
                    vec = inst['vec']

                    # send_width: scalar #, 16: bit-precision, 32: packet size
                    packet_num = ((send_width*16+31) / 32) * vec
                    self.noc.send_packets(self.num, target_tile_num, vtile_id, packet_num, self.send_wait_cyc)
                    
                    # shared mem ==> packet geneartion
                    #self.mem_wait = vec # assuming 1cyc/vec-read, decoupled packet gen
                    self.mem_wait = 1 # assuming 1cyc/vec-read, decoupled packet gen

                    # decoupled packet gen, assuming 1cyc/packet 
                    #self.send_wait_cyc += packet_num
                    self.send_wait_cyc += 1

                    self.debug(inst)
                    self.pc += 1
                    pf.call_stack["Send"] += 1

            else: pass #send block - shared memory contention

        elif inst['opcode'] == 'receive':
            if self.mem_wait == 0:
                mem_addr = inst['mem_addr']
                vtile_id = inst['vtile_id']
                receive_width = inst['r1']
                counter = inst['r2']
                vec = inst['vec']


                if self.fifo[vtile_id] > 0:
                    #assert (not mem_addr in self.shared_mem)\
                    #    or self.shared_mem[mem_addr] == 0

                    packet_num = ((receive_width*16+31) / 32) * vec
                    assert packet_num <= self.fifo[vtile_id]

                    self.fifo[vtile_id] -= packet_num
                    self.memory.allocate(mem_addr, counter)

                    # fifo ==> shared mem
                    #self.mem_wait = vec # assuming 1cyc/vec-write
                    self.mem_wait = 1 # assuming 1cyc/vec-write

                    self.debug(inst)
                    self.pc += 1
                    pf.call_stack["Receive"] += 1

            else: 
                pass #receive block

        elif inst['opcode'] == 'halt':
            if self.halted_core_num == gv.params["core_num"]:
                self.is_halted = True
                gv.halted_tile_num += 1

                self.debug(inst)
            
        else:
            raise NotImplementedError

        for core in self.cores:
            core.advance()

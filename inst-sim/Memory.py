import numpy as np
import GlobalVars as gv
import Profile as pf
import config as cfg
import Tile
import sys

class Memory:
    def __init__(self, tile):
        self.tile = tile

        # map virtual address to the physical address
        # convert the virtual address 
        # to the physical address
        self.virtual_to_physical = {}
        
        # physical memory (counter (0), virtual addr (1), data(2))
        self.physical_mem = {}
        self.max_physical_size = 0

        self.virtual_mem = {}

    def allocate(self, virtual_addr, counter, data = 0):
        # check alignment
        assert(virtual_addr % cfg.xbar_size == 0)

        self.virtual_mem[virtual_addr] = 0

        # first check if the virtual address & count
        assert ((not virtual_addr in self.virtual_to_physical)\
            or (self.physical_mem[self.virtual_to_physical[virtual_addr]][0] == 0))

        # search for the empty space & allocate to the physical memory
        target_addr = 0
        while(True):
            # if the physical address has not been allocated
            # or the counter is zero
            if(not target_addr in self.physical_mem):
                # then add a new entry to the dictionary
                self.virtual_to_physical[virtual_addr] = target_addr
                # allocate the new entry to the physical mem
                self.physical_mem[target_addr] = [counter, virtual_addr, data]
                break
            target_addr += cfg.xbar_size
        
        # renew the maximum size
        if(target_addr > self.max_physical_size): self.max_physical_size = target_addr

    def access(self, virtual_addr):
        # if the virtual address exist & the physical memory's counter is not zero

        if ((virtual_addr in self.virtual_to_physical)\
            and (self.physical_mem[self.virtual_to_physical[virtual_addr]][0] != 0)):
            
            physical_addr = self.virtual_to_physical[virtual_addr]
            self.physical_mem[physical_addr][0] -= 1
            data = self.physical_mem[physical_addr][2]

            if(self.physical_mem[physical_addr][0] == 0):
                self.virtual_to_physical.pop(self.physical_mem[physical_addr][1])
                assert(not self.physical_mem[physical_addr][1] in self.virtual_to_physical)
                self.physical_mem.pop(physical_addr)
                assert(not physical_addr in self.physical_mem)
                #del self.virtual_to_physical[self.physical_mem[physical_addr][1]]
            return True, data

        return False, -1
        

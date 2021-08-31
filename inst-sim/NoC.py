import GlobalVars as gv
from queue import PriorityQueue
import Tile
import Profile as pf

class NoC:

    def __init__(self):
        self.tiles = [Tile.Tile(i, self) for i in range(gv.params["tile_num"])]
        self.cyc = 0
        self.packet_queue = PriorityQueue()

        self.total_inst = 0
        for tile in self.tiles: 
            self.total_inst += tile.total_inst

        self.pc = 0
        self.pc_prev = 0

    def send_packets(self, src_tile_num, dst_tile_num, vtile_id, packet_num, wait_cyc):
        packets = (self.cyc + wait_cyc + self.getRoutingLatency(src_tile_num, dst_tile_num),
                dst_tile_num, vtile_id, packet_num)
        self.packet_queue.put(packets)

    def advance(self):
        self.cyc += 1
        while True:
            if self.packet_queue.empty() == True: break
            (arrival_cyc, dst_tile_num, vtile_id, packet_num) = self.packet_queue.queue[0]
            if arrival_cyc > self.cyc: break
            self.packet_queue.get()
            self.tiles[dst_tile_num].fifo[vtile_id] += packet_num
            

        self.pc = 0
        for tile in self.tiles:
            self.pc += tile.pc
            tile.advance()
            for core in tile.cores:
                self.pc += core.pc

        self.pc_prev = self.pc

        pf.progress(self.pc, self.total_inst)

    # FIXME: add BW support
    def getRoutingLatency(self, src_tile_num, dst_tile_num):
        src_x, src_y = gv.ind_to_coord(src_tile_num)
        dst_x, dst_y = gv.ind_to_coord(dst_tile_num)

        return abs(src_x - dst_x) + abs(src_y - dst_y)


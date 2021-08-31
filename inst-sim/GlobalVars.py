debug_enabled = True
last_debug_cyc = 0

params = {}
NoC = None
halted_tile_num = 0
fifo_num = 0
total_inst = 0

def ind_to_coord(ind):
    return ind % params["tile_x"], ind // params["tile_x"]

import sys
import os
import math
import config as cfg
import numpy as np
import GlobalVars as gv
import Profile as pf
import NoC
import Tile
from collections import deque
from collections import defaultdict
from queue import PriorityQueue
from cProfile import Profile
from pstats import Stats 

def init():
    # workload name
    gv.params["workload"] = sys.argv[1]
    gv.params["foldername"] = "workload/%s" % (sys.argv[1])
    gv.params["result_foldername"] = "result/%s" % (sys.argv[1])
    if not os.path.isdir(gv.params["foldername"]):
        raise("No workload folder exists")
    if not os.path.isdir(gv.params["result_foldername"]):
        os.mkdir(gv.params["result_foldername"])

    os.listdir()
    total_cores = 0
    total_tiles = 0

    ##
    for _, dirnames, filenames in os.walk(gv.params["foldername"]):
        for file in filenames:
            if "-core" in file and not ".swp" in file:
                total_cores += 1
        total_tiles += len(dirnames)

    gv.params["tile_x"] = int(math.sqrt(total_tiles))
    gv.fifo_num = total_tiles

    assert(total_cores % total_tiles == 0)

    ##
    gv.params["tile_num"] = int(total_tiles)
    gv.params["core_num"] = int(total_cores / total_tiles)

    gv.NoC = NoC.NoC()

def simulate():
    pf.cyc = 0
    while gv.halted_tile_num < gv.params["tile_num"]:
        pf.cyc += 1
        gv.NoC.advance()
        

def stat():
    result_path = os.path.join(gv.params["result_foldername"], "result.txt")
    result_file = open(result_path, "w")

    result_file.write("\n====CPI STACK====\n")
    result_file.write("total cyc: {}\n".format(pf.cyc))
    #print ("\n====CPI STACK====")
    #print ("total cyc: {}".format(pf.cyc))
    sum_v = 0
    for _, v in pf.call_stack.items():
        sum_v += v
    for k, v in pf.call_stack.items():
        result_file.write("{} : {} / {}\n".format(k, v, sum_v))
        #print ("{} : {} / {}".format(k, v, sum_v))

    result_file.write("\n====LINK====\n")
    #print ("\n====LINK====")
    result_file.write("busiest link: {}KB\n".format(float(pf.busiest_link_data) / (8*1024)))
    #print ("busiest link: {}KB".format(float(pf.busiest_link_data) / (8*1024)))

    result_file.write("\n====MAX MEMORY SIZE====\n")
    #print("\n====MAX MEMORY SIZE====")
    for tile in gv.NoC.tiles:
        result_file.write("tile id: {}\t\t\tphysical size: {}\t\t\tvirtual size: {}\n".format(
            tile.num, tile.memory.max_physical_size, len(tile.memory.virtual_mem) * cfg.xbar_size))
        #print(tile.num, tile.memory.max_physical_size, 
        #    len(tile.memory.virtual_mem) * gv.MVMU_DIM)

def testrun():
    init()
    simulate()
    stat()

profiler = Profile()
profiler.runcall(testrun)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('tottime')
stats.print_stats()

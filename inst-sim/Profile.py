import sys


def progress(count, total):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('progress: [%s] %s%s\r' % (bar, percents, '%'))
    sys.stdout.flush()

passed_data = None # key:((src_x, src_y), (dst_x, dst_y)), value:data_bits
busiest_link = None
busiest_link_data = -1
cyc = None
cpi_stack = {"Copy": 0,
           "Load": 0,
           "Store": 0,
           "Send": 0,
           "Receive": 0,
           "MVM": 0,
           "ALU": 0,
           "ALUI": 0,
           "Set": 0,
           "WriteInput": 0,
           "ReadOutput": 0}

call_stack = {"Copy": 0,
           "Load": 0,
           "Store": 0,
           "Send": 0,
           "Receive": 0,
           "MVM": 0,
           "ALU": 0,
           "ALUI": 0,
           "Set": 0,
           "WriteInput": 0,
           "ReadOutput": 0}

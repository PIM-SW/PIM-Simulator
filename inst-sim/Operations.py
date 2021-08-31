op_list = ['ld', 'cp', 'st', 'set', 'nop', 'alu', 'alui', 'mvm', 'vvo', 'hlt', 'jmp', 'beq', 'alu_int', 'crs']
aluop_list = ['add', 'sub', 'sna', 'mul', 'sigmoid'] # sna is also used by mvm isntruction
op_list_tile = ['send', 'receive', 'halt']

latency = {"ld": None,
           "cp": 1,
           "st": None,
           "set": 1,
           "nop": 1,
           "alu": 1,
           "alui": 1,
           "mvm": 1000,
           "vvo": 1,
           "hlt": 1,
           "jmp": 1,
           "beq": 1,
           "alu_int": 1,
           "crs": 1,
           "send": None,
           "receive": None,
           "halt": 1
          }


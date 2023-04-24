import re
import numpy as np
import os

from path import ASB_PATH

TOTAL_EPOCH = 200

pattern = "([ \d]{6,}): ([ \.\d]{7,}) s > ([ \d,]{7,}) ops, [ \.\d]{7,} us/op, [ ,\d]{5,} empty reads > Read amp ([ ,\.\d]{6,}), Write amp ([ ,\.\d]{6,}) > .*"
stat_pattern = ".*> Cnt\ *(\d+), Avg\ *((\d+)|none|(\d+[km]))\. (.*)"

def to_float(input):
    return float(input.replace(",","").replace(" ",""))

def parse(file):
    rn, rs, wn, ws = (None,) * 4
    for line in file:
        res = re.match(pattern,line)
        if res:
            epoch, time, tps, ra, wa = (to_float(x) for x in res.groups())
            yield epoch, time, tps,ra,wa,rn,rs,wn,ws
            rn, rs, wn, ws = (None,) * 4
        elif re.match(".*10:.*20:.*95:",line):  
            res = re.match(stat_pattern,line).groups()
            cnt = res[0]
            avg = res[1]
            msg = res[4]
            if msg == "Non-empty read size":
                rn = int(cnt)
                rs = int(avg)
            elif msg == "Write size":
                wn = int(cnt)
                ws = int(avg)
            else:
                pass
        else:
            pass


def path(authdb, keys, folder="osdi23", stat=False, low_mem=False, high_mem=0):
    if stat:
        return f"paper_experiment/{folder}/stat_{authdb}_{keys}.log"
    else:
        if low_mem:
            return f"paper_experiment/{folder}/time_{authdb}_{keys}_lowmem.log"
        elif high_mem > 0:
            return f"paper_experiment/{folder}/time_{authdb}_{keys}_highmem{high_mem}.log"
        else:
            return f"paper_experiment/{folder}/time_{authdb}_{keys}.log"
        

def load(authdb, keys, folder="osdi23", low_mem=False):
    with open(os.path.join(ASB_PATH, path(authdb, keys, folder, low_mem=low_mem))) as f:
        data_time = np.array(list(parse(f)))  
        
    with open(os.path.join(ASB_PATH, path(authdb, keys, folder, stat=True, low_mem=low_mem))) as f:
        data_stat = np.array(list(parse(f))) 
        return Data(data_time,data_stat,skip_start=(keys!="real"))

    
    
class Data:
    def __init__(self,time,stat=None,skip_start=True):
        data = time.T
        if skip_start:
            mask = (data[0] < TOTAL_EPOCH) & (data[0] >= TOTAL_EPOCH/2)
            data = data[:,mask]
        self.epoch = data[0]
        self.timer = data[1]
        
        self.tps = data[2]
        self.ra = data[3]
        self.wa = data[4]
        
        T = self.timer
        T = np.concatenate([[0],T])
        self.latency = T[1:]-T[:-1]
        
        
        data = stat.T
        if skip_start:
            mask = (data[0] < TOTAL_EPOCH) & (data[0] >= TOTAL_EPOCH/2)
            data = data[:,mask]
        
        self.rn = data[5]
        self.rs = data[6]
        self.wn = data[7]
        self.ws = data[8]
    
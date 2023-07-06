import re
import numpy as np
import os

from path import ASB_PATH

pattern = "([ \d]{6,}): ([ \.\d]{7,}) s > ([ \d,]{7,}) ops, [ \.\d]{7,} us/op, ([ ,\d]{5,}) empty reads > Read amp ([ ,\.\d]{6,}), Write amp ([ ,\.\d]{6,}) > .*"
stat_pattern = ".*> Cnt\ *(\d+), Avg\ *((\d+)|none|(\d+[km]))\. (.*)"
percentiles = [10,20,30,40,50,60,70,80,90,95,98,99]
pecentile_pattern = "\ *".join([f"{n}:\ *((\d+)|none|(\d+[km]))" for n in percentiles])

def parse_number(item):
    if item[-1] in "kmg":
        number = float(item[:-1])
        number *= {"k": 1e3,"m": 1e6, "g": 1e9}[item[-1]]
        return number
    elif item == "none":
        return np.nan
    else:
        return float(item)

def parse_pecentile(msg):
    res = re.search(pecentile_pattern,msg).groups()
    ans = np.array([parse_number(res[i]) for i in range(0,36,3)])
    return ans
    

def to_float(input):
    return float(input.replace(",","").replace(" ",""))

def parse(file):
    rn, rs, wn, ws, rempty = (None,) * 5
    rc = np.full((12,), np.nan)
    wc = np.full((12,), np.nan)
    for line in file:
        res = re.match(pattern,line)
        if res:
            epoch, time, tps, rempty, ra, wa = (to_float(x) for x in res.groups())
            yield np.concatenate((np.array([epoch, time, tps, rempty, ra,wa,rn,rs,wn,ws]),rc,wc))
            rn, rs, wn, ws, rempty = (None,) * 5
            rc = np.full((12,), np.nan)
            wc = np.full((12,), np.nan)
        elif re.match(".*10:.*20:.*95:",line):  
            res = re.match(stat_pattern,line).groups()
            cnt = res[0]
            avg = res[1]
            msg = res[4]
            if msg == "Non-empty read size":
                rn = int(cnt)
                rs = int(avg)
                rc = parse_pecentile(line)
            elif msg == "Write size":
                wn = int(cnt)
                ws = int(avg)
                wc = parse_pecentile(line)
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
        

def load(authdb, keys, folder="osdi23", low_mem=False, only_time=False):
    with open(os.path.join(ASB_PATH, path(authdb, keys, folder, low_mem=low_mem))) as f:
        data_time = np.array(list(parse(f)))  
        if only_time:
            return Data(data_time,skip_start=(keys!="real"))
        
    with open(os.path.join(ASB_PATH, path(authdb, keys, folder, stat=True, low_mem=low_mem))) as f:
        data_stat = np.array(list(parse(f))) 
        return Data(data_time,data_stat,skip_start=(keys!="real"))

    
    
class Data:
    def __init__(self, time, stat=None, skip_start=True):
        data = time.T
        if skip_start:
            max_epoch = np.max(data[0])
            mask = data[0] >= max_epoch/2
            data = data[:,mask]
        else:
            data = data[:,10:]
        self.epoch = data[0]
        self.timer = data[1]
        
        self.tps = data[2]
        self.rempty = data[3]
        self.ra = data[4]
        self.wa = data[5]
        
        T = self.timer
        T = np.concatenate([[0],T])
        self.latency = T[1:]-T[:-1]
        
        if stat is None:
            return
        
        
        data = stat.T
        if skip_start:
            mask = data[0] >= max_epoch/2
            data = data[:,mask]
        else:
            data = data[:,10:]
        
        self.rn = data[6]
        self.rs = data[7]
        self.wn = data[8]
        self.ws = data[9]
        self.rc = data[10:10+12]
        self.wc = data[10+12:10+24]
    
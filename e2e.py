import re
import numpy as np
from path import ASB_E2E_PATH

import os


def metrics_loader(path):
    timestamp = None
    lines = []
    with open(path) as f:
        for line in f.readlines():
            res = re.match("(\d*),.*", line)
            if res is None:
                break
            line_timestamp = int(res.groups()[0])
            if timestamp is None:
                timestamp = line_timestamp
            if timestamp == line_timestamp:
                lines.append(line)
            else:
                yield (timestamp, "\n".join(lines))
                lines = [line]
                timestamp = line_timestamp

    yield (timestamp, "".join(lines))


class Pattern:
    def __init__(self, group, name, meter="count"):
        self.pattern = f"(^|(?<=\n))\d*, {group}, Group, \x7b.*{name}\.{meter}: (\d+),"

    def extract(self, record):
        res = re.search(self.pattern, record)
        if res is None:
            return float(0)
        else:
            return float(res.groups()[1])


patterns = [
    Pattern("system_metrics", "good_tps"),  # 1
    Pattern("timer", "storage::get"),  # 2
    Pattern("timer", "storage::set"),  # 3
    Pattern("timer", "storage::commit"),  # 4
    Pattern("timer", "backend::get"),  # 5
    Pattern("timer", "backend::set"),  # 6
    Pattern("timer", "backend::commit"),  # 7
    Pattern("timer", "consensus::handle_epoch_execution"),  # 8
    Pattern("debug", "debug"),  # 9
]


def load(ty, size, erc20=False, folder="osdi23"):
    if erc20:
        task = "erc20"
    else:
        task = "native"

    path = "experiment_data/metrics/{folder}/less-sender-{task}-{ty}-{size}.log".format(
        ty=ty, size=size, folder=folder, task=task)
    records = list(metrics_loader(os.path.join(ASB_E2E_PATH, path)))
    return Data(np.array([[timestamp, *[p.extract(record) for p in patterns]] for (timestamp, record) in records]))


class Data:
    def __init__(self, data):
        data = data.T
        if len(data[0]) == 0:
            return

        # Truncate the prefix of warmup
        DT = data[1, 1:] - data[1][:-1]
        zeros = np.where(DT < 1)[0]
        start_index = 0
        if len(zeros) > 0:
            start_index = zeros[-1] + 1

        mark_index = np.where(data[-1] >= 1)[0][0]
        # skip first 10 seconds
        start_index = np.where(data[0] > data[0, mark_index] + 10000)[0][0]
        end_index = np.where(data[0] < data[0, -1] - 10000)[0][-1]

        data = data.T
        data = data[start_index:]
        data -= data[0]
        data = data.T

        data[0] /= 1e3

        self.data = data

    @property
    def timestamp(self):
        return self.data[0]

    def data(self, col):
        return self.data[col]

    def mean(self, col):
        return self.data[col, -1] / self.data[0, -1]

    def rate(self, col):
        A = self.data[col]
        T = self.data[0]
        return np.divide(A[1:]-A[:-1], T[1:]-T[:-1])

    @property
    def tps(self):
        return self.rate(1)

    @property
    def mean_tps(self):
        return self.mean(1)

    @property
    def goodput(self):
        return self.data(1)

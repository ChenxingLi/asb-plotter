import numpy as np
from matplotlib import pyplot as plt
from data_parse import load as load_asb
from data_parse import parse_number
from e2e import load as load_e2e
from plot import BarPlot
from pathlib import Path
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

e2e_authdbs = ["raw", "lvmt", "lvmt64", "lvmt16", "rain", "lmpts", "mpt"]
e2e_breakdown = ["raw", "lvmt", "lvmt64", "lvmt16", "rain", "mpt"]
authdbs = ["lvmt", "lvmt64", "lvmt16", "rain", "mpt", "lvmt1"]
authdbs_detail = authdbs[:-1]
tasks = ["real", "fresh", "1m", "10m", "100m"]

def maybe(func):
    try:
        ans = func()
        if ans == np.nan:
            return None
        return ans
    except:
        return None

def labelize(authdbs):
    def f(authdb):
        if authdb == "lmpts":
            return "LMPTs"
        elif authdb == "lvmt":
            return "LVMT-r"
        else:
            return authdb.upper()
    if type(authdbs) is str:
        return f(authdbs)
    else:
        return [f(db) for db in authdbs]


def plot_native_transfer():
    """ Figure 2(a) """

    fig = plt.figure(figsize=(8, 4), dpi=200)
    ax = fig.add_subplot(111)

    bp = BarPlot()
    for size in ["1m", "3m", "5m"]:
        data = [load_e2e(authdb, size, erc20=False).mean_tps/1000 for authdb in e2e_authdbs]
        bp.add(size, *data)
    bp.draw(ax, space=0.3, labels=labelize(e2e_authdbs))
    bp.number(ax, align="c"*(len(e2e_authdbs)), hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=3)
    ax.set_title("Throughput for Simple Transactions")
    ax.set_ylabel("Transactions per Second (x1000)")
    ax.set_xlabel("Number of Initialized Keys")

    # plt.show()
    plt.savefig("figures/native_transfer.pdf", bbox_inches='tight')


def plot_erc20_transfer():
    """ Figure 2(b) """

    fig = plt.figure(figsize=(8, 4), dpi=200)
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for size in ["1m", "3m", "5m"]:
        data = [load_e2e(authdb, size, erc20=True).mean_tps/1000 for authdb in e2e_authdbs]
        bp.add(size, *data)
    bp.draw(ax, space=0.3, labels=labelize(e2e_authdbs))
    bp.number(ax, align="c"*(len(e2e_authdbs)), hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=3)
    ax.set_title("Throughput for ERC20 Transfers")
    ax.set_ylabel("Transactions per Second (x1000)")
    ax.set_xlabel("Number of Initialized Keys")

    # plt.show()
    plt.savefig("figures/erc20_transfer.pdf", bbox_inches='tight')


def plot_native_breakdown():
    """ Figure 3(a) """

    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for algo in e2e_breakdown:
        data = load_e2e(algo, "5m", erc20=False)
        all = data.mean(8)/1e3/data.mean_tps
        auth = data.mean([2, 3, 4]).sum()/1e3/data.mean_tps
        backend = data.mean([5, 6, 7]).sum()/1e3/data.mean_tps

        vm = all - auth
        vc = max(auth - backend, 0)
        bp.add(labelize(algo), vm, vc, backend)

    bp.draw(ax, labels=["Execution Engine",
            "Authenticated Structure", "Backend "])
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.0f}")
    ax.set_ylabel("Time (us)")
    ax.set_xlabel("Authenticated Storage Systems")
    ax.set_title(f"Time Usage Breakdown for Simple Transactions")
    ax.legend(loc=2)
    plt.savefig("figures/native_breakdown.pdf", bbox_inches='tight')


def plot_erc20_breakdown():
    """ Figure 3(b) """

    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for algo in e2e_breakdown:
        data = load_e2e(algo, "5m", erc20=True)
        all = data.mean(8)/1e3/data.mean_tps
        auth = data.mean([2, 3, 4]).sum()/1e3/data.mean_tps
        backend = data.mean([5, 6, 7]).sum()/1e3/data.mean_tps

        vm = all - auth
        vc = max(auth - backend, 0)
        bp.add(labelize(algo), vm, vc, backend)

    bp.draw(ax, labels=["Execution Engine",
            "Authenticated Structure", "Backend "])
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.0f}")
    ax.set_yticks(np.arange(0,81,10))
    ax.set_ylim(0,80)
    ax.set_ylabel("Time (us)")
    ax.set_xlabel("Authenticated Storage Systems")
    ax.set_title(f"Time Usage Breakdown for ERC20 Transfers")
    ax.legend(loc=2)
    plt.savefig("figures/erc20_breakdown.pdf", bbox_inches='tight')


def plot_asb_tps():
    """ Figure 4(a) """
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for size in ["real", "fresh", "1m", "10m", "100m"]:
        data = [maybe(lambda: np.mean(load_asb(authdb, size, only_time=True).tps)/1000) for authdb in authdbs]
        bp.add(size, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs))
    bp.number(ax, align="cllllll", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=1)
    ax.set_title("Throughput of Authenticated Storage Systems")
    ax.set_ylabel("Operations per second (1000x)")
    ax.set_xlabel("Workloads")
    plt.savefig("figures/asb_tps.pdf", bbox_inches='tight')
    
def plot_asb_tps_on_size():
    """ Figure 4(b) """
    fig = plt.figure(figsize=(7, 3.5), dpi=200)
    ax = fig.add_subplot(111)

    all_size = ["1m", "1600k", "2500k", "4m", "6300k", "10m", "16m", "25m", "40m", "63m", "100m"]
    x = np.array([parse_number(x) for x in all_size])

    marker = "o^vsDphx"
    for (idx, algo) in enumerate(authdbs+["raw"]):
        def get_tps(size):
            try:
                return np.mean(load_asb(algo, size, only_time=True).tps)
            except:
                return 0
        y = np.array([get_tps(size) for size in all_size])
        ax.loglog(x[y>0], y[y>0], label=labelize(algo), marker=marker[idx])

    ax.minorticks_off()
    ax.set_xticks(x)
    ax.set_xticklabels(["1","1.6","2.5","4","6.3","10","16","25","40","63","100"])
    ax.set_yticks([1e3, 2e3, 5e3, 1e4,2e4,5e4,1e5,2e5,5e5])
    ax.set_yticklabels(["1","2","5","10","20","50","100","200","500"])

    ax.grid(linestyle = "--", alpha=0.5)
    ax.legend(loc="upper left",bbox_to_anchor=[1, 1])
    ax.set_xlabel("Keys in Ledger (in millions)")
    ax.set_ylabel("Operations per Second (x1000)")
    ax.set_title("Throughput of Authenticated Storage Systems on Various Ledger Sizes")
    ax.set_ylim(1e3,5e5)
    plt.savefig("figures/asb_tps_on_size.pdf", bbox_inches='tight')

def plot_ra():
    """ Figure 5(a) """

    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for task in tasks:
        data = [maybe(lambda: np.mean(load_asb(authdb, task, only_time=True).ra)) for authdb in authdbs_detail]
        bp.add(task, *data)

    bp.draw(ax, space=0.12, labels=labelize(authdbs_detail))
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.1f}")
    legend = ax.legend(loc="upper center", bbox_to_anchor=[0.465, 1])
    ax.set_title("Read Amplification of Authenticated Storage Systems")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Reads per Operation")
    plt.savefig("figures/asb_ra.pdf", bbox_inches='tight')


def plot_wa():
    """ Figure 5(b) """

    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for task in tasks:
        data = [maybe(lambda: np.mean(load_asb(authdb, task, only_time=True).wa)) for authdb in authdbs_detail]
        bp.add(task, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs_detail))
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.1f}")
    ax.legend(loc="upper center", bbox_to_anchor=[0.465, 1])
    ax.set_title("Write Amplification of Authenticated Storage Systems")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Writes per Operation")
    plt.savefig("figures/asb_wa.pdf", bbox_inches='tight')


def plot_rs():
    """ Figure 7(a) """

    fig = plt.figure(figsize=(9, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    def read_size(x): 
        length = min(len(x.rs), len(x.rempty))
        return x.rs[:length] * (1 - x.rempty[:length]/(x.rn[:length] + x.rempty[:length]))

    for task in tasks:
        data = [np.mean(read_size(load_asb(authdb, task)))
                for authdb in authdbs_detail]
        bp.add(task, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs_detail))
    bp.number(ax, align="cccccc", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc="upper center", bbox_to_anchor=[0.862, 1])
    ax.set_title("Data Size per Read Operation on Backend")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Data Size (bytes)")
    plt.savefig("figures/asb_rs.pdf", bbox_inches='tight')


def plot_ws():
    """ Figure 7(b) """

    fig = plt.figure(figsize=(9, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    def write_size(x): return x.ws

    for task in tasks:
        data = [np.mean(write_size(load_asb(authdb, task)))
                for authdb in authdbs_detail]
        bp.add(task, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs_detail))
    bp.number(ax, align="cccccc", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc="upper center", bbox_to_anchor=[0.862, 1])
    ax.set_title("Data Size per Write Operation on Backend")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Data Size (bytes)")
    plt.savefig("figures/asb_ws.pdf", bbox_inches='tight')
    
def plot_rc():
    """ Figure 7(c) """

    fig = plt.figure(figsize=(8,3), dpi=200)
    ax = fig.add_subplot(111)

    x = np.arange(10,100,10)
    marker = "o^vsDphx"
    for (idx, algo) in enumerate(authdbs_detail):
        y = load_asb(algo, "100m").rc.mean(axis=1)[:9]
        ax.semilogy(x[y>0], y[y>0], label=labelize(algo), marker=marker[idx])

    ax.minorticks_off()
    yticks = [30,50,70,100,200,300,500,700]
    ax.set_yticks(yticks)
    ax.set_yticklabels([0] + yticks[1:])

    ax.grid(linestyle = "--", alpha=0.5)
    ax.legend()
    ax.set_xlabel("Percentiles")
    ax.set_ylabel("Data Size (Bytes)")
    ax.set_title("Backend Read Operations: Data Size Distribution")
    ax.set_ylim(30,700)
    plt.savefig("figures/asb_rc.pdf", bbox_inches='tight')

    
def plot_wc():
    """ Figure 7(d) """

    fig = plt.figure(figsize=(8,3), dpi=200)
    ax = fig.add_subplot(111)

    x = np.arange(10,100,10)
    marker = "o^vsDphx"
    for (idx, algo) in enumerate(authdbs_detail):
        y = load_asb(algo, "100m").wc.mean(axis=1)[:9]
        y[y==0] = np.full((9,),30)[y==0]
        ax.semilogy(x, y, label=labelize(algo), marker=marker[idx])

    ax.minorticks_off()
    yticks = [30,50,70,100,200,300,500,700]
    ax.set_yticks(yticks)
    ax.set_yticklabels([0] + yticks[1:])

    ax.grid(linestyle = "--", alpha=0.5)
    ax.legend()
    ax.set_xlabel("Percentiles")
    ax.set_ylabel("Data Size (Bytes)")
    ax.set_title("Backend Write Operations: Data Size Distribution")
    ax.set_ylim(30,700)
    plt.savefig("figures/asb_wc.pdf", bbox_inches='tight')



if __name__ == "__main__":
    Path("figures").mkdir(exist_ok=True)

    plot_native_transfer()
    plot_erc20_transfer()
    plot_native_breakdown()
    plot_erc20_breakdown()
    plot_asb_tps()
    plot_asb_tps_on_size()
    plot_ra()
    plot_wa()
    plot_rs()
    plot_ws()
    plot_rc()
    plot_wc()

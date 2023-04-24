import numpy as np
from matplotlib import pyplot as plt
from data_parse import load as load_asb
from e2e import load as load_e2e
from plot import BarPlot
from pathlib import Path

e2e_authdbs = ["raw", "lvmt", "lvmt64", "lvmt16", "lmpts", "mpt"]
e2e_breakdown = ["raw", "lvmt", "lvmt64", "lvmt16", "mpt"]
authdbs = ["lvmt", "lvmt64", "lvmt16", "mpt"]
tasks = ["real", "fresh", "1m", "10m", "100m"]


def labelize(authdbs):
    def f(authdb):
        if authdb == "lmpts":
            return "LMPTs"
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
        data = [load_e2e(authdb, size, erc20=False).mean_tps for authdb in e2e_authdbs]
        bp.add(size, *data)
    bp.draw(ax, space=0.3, labels=labelize(e2e_authdbs))
    bp.number(ax, align="clllll", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=3)
    ax.set_title("Throughput for random native transfers")
    ax.set_ylabel("Transactions per second")
    ax.set_xlabel("Number of initialized keys")

    # plt.show()
    plt.savefig("figures/native_transfer.pdf", bbox_inches='tight')


def plot_erc20_transfer():
    """ Figure 2(b) """

    fig = plt.figure(figsize=(8, 4), dpi=200)
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for size in ["1m", "3m", "5m"]:
        data = [load_e2e(authdb, size, erc20=True).mean_tps for authdb in e2e_authdbs]
        bp.add(size, *data)
    bp.draw(ax, space=0.3, labels=labelize(e2e_authdbs))
    bp.number(ax, align="clllll", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=3)
    ax.set_title("Throughput for random erc20 transfers")
    ax.set_ylabel("Transactions per second")
    ax.set_xlabel("Number of initialized keys")

    # plt.show()
    plt.savefig("figures/native_transfer.pdf", bbox_inches='tight')


def plot_native_breakdown():
    """ Figure 3(a) """

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for algo in e2e_breakdown:
        data = load_e2e(algo, "5m", erc20=False)
        all = data.mean(8)/1e3/data.mean_tps
        auth = data.mean([2, 3, 4]).sum()/1e3/data.mean_tps
        backend = data.mean([5, 6, 7]).sum()/1e3/data.mean_tps

        vm = all - auth
        vc = max(auth - backend, 0)
        bp.add(algo, vm, vc, backend)

    bp.draw(ax, labels=["Execution Engine",
            "Authenticated Structure", "Backend "])
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.0f}")
    ax.set_ylabel("Time (us)")
    ax.set_xlabel("Authenticated Storages")
    ax.set_title(f"Time usage breakdown for transaction execution")
    ax.legend(loc=2)
    plt.savefig("figures/native_breakdown.pdf", bbox_inches='tight')


def plot_erc20_breakdown():
    """ Figure 3(b) """

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for algo in e2e_breakdown:
        data = load_e2e(algo, "5m", erc20=True)
        all = data.mean(8)/1e3/data.mean_tps
        auth = data.mean([2, 3, 4]).sum()/1e3/data.mean_tps
        backend = data.mean([5, 6, 7]).sum()/1e3/data.mean_tps

        vm = all - auth
        vc = max(auth - backend, 0)
        bp.add(algo, vm, vc, backend)

    bp.draw(ax, labels=["Execution Engine",
            "Authenticated Structure", "Backend "])
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.0f}")
    ax.set_ylabel("Time (us)")
    ax.set_xlabel("Authenticated Storages")
    ax.set_title(f"Time usage breakdown for executing ERC20 transfers")
    ax.legend(loc=2)
    plt.savefig("figures/erc20_breakdown.pdf", bbox_inches='tight')


def plot_asb_tps():
    """ Figure 4 """
    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for size in ["real", "fresh", "1m", "10m", "100m"]:
        data = [np.mean(load_asb(authdb, size).tps)/1000 for authdb in authdbs]
        bp.add(size, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs))
    bp.number(ax, align="cccccc", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=1)
    ax.set_title("Throughput of authenticated storage")
    ax.set_ylabel("Operations per second (1000x)")
    ax.set_xlabel("Workloads")
    plt.savefig("figures/asb_tps.pdf", bbox_inches='tight')


def plot_low_mem():
    """ Figure 5 """

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for task in tasks:
        data = [np.mean(load_asb("lvmt16", task, low_mem=lowmem).tps) /
                1000 for lowmem in [False, True]]
        bp.add(task, *data)

    bp.draw(ax, space=0.4, labels=["1500 MB", "800 MB"])
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.0f}")
    ax.legend()
    ax.set_title(f"Throughput of LVMT16 with different memory sizes")
    ax.set_ylabel("Operations per second (x1000)")
    ax.set_xlabel("Number of initialized keys")

    plt.savefig("figures/asb_mem_tps.pdf", bbox_inches='tight')


def plot_ra():
    """ Figure 6(a) """

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for task in tasks:
        data = [np.mean(load_asb(authdb, task).ra) for authdb in authdbs]
        bp.add(task, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs))
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.1f}")
    ax.legend(loc=2)
    ax.set_title("Read amplication of authenticated storage")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Reads per operation")
    plt.savefig("figures/asb_ra.pdf", bbox_inches='tight')


def plot_wa():
    """ Figure 6(b) """

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    for task in tasks:
        data = [np.mean(load_asb(authdb, task).wa) for authdb in authdbs]
        bp.add(task, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs))
    bp.number(ax, hspace=0.35, format=lambda x: f"{x:0.1f}")
    ax.legend(loc=2)
    ax.set_title("Write amplication of authenticated storage")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Writes per operation")
    plt.savefig("figures/asb_wa.pdf", bbox_inches='tight')


def plot_rs():
    """ Figure 7(a) """

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    def read_size(x): return x.rs * x.rn / 50000

    for task in tasks:
        data = [np.mean(read_size(load_asb(authdb, task)))
                for authdb in authdbs]
        bp.add(task, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs))
    bp.number(ax, align="cccccc", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=2)
    ax.set_title("Data reads per operation")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Data size (bytes)")
    # plt.show()
    plt.savefig("figures/asb_rs.pdf", bbox_inches='tight')

# Figure 7(b)


def plot_ws():
    """ Figure 7(b) """

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    bp = BarPlot()

    def write_size(x): return x.ws * x.wn / 50000

    for task in tasks:
        data = [np.mean(write_size(load_asb(authdb, task)))
                for authdb in authdbs]
        bp.add(task, *data)

    bp.draw(ax, space=0.2, labels=labelize(authdbs))
    bp.number(ax, align="cccccc", hspace=0.5, format=lambda x: f"{x:0.0f}")
    ax.legend(loc=2)
    ax.set_title("Data writes per operation")
    ax.set_xlabel("Workloads")
    ax.set_ylabel("Data size (bytes)")
    # plt.show()
    plt.savefig("figures/asb_ws.pdf", bbox_inches='tight')


if __name__ == "__main__":
    Path("figures").mkdir(exist_ok=True)

    plot_native_transfer()
    plot_erc20_transfer()
    plot_native_breakdown()
    plot_erc20_breakdown()
    plot_asb_tps()
    plot_low_mem()
    plot_ra()
    plot_wa()
    plot_rs()
    plot_ws()

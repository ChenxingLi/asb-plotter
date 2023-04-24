# Authenticated Storage Benchmarks Plotter

This tool is designed for parsing the experiment traces of authenticated storages and plotting figures in the paper "LVMT: An Efficient Authenticated Storage for Blockchain". To reproduce the results of the paper using this tool, follow the steps below. These steps have been verified on Ubuntu 22.04, but they should also work on other Ubuntu versions with similar commands.

1. Update the package list:
    
    ```bash
    sudo apt update
    ```
    
2. Install Python3 and Pip3:
    
    ```
    sudo apt install python3 python3-pip
    ```
    
3. Install the required modules:
    
    ```
    pip3 install numpy matplotlib
    ```
    
4. Build and run the preconfigured evaluations in the [Authenticated Storage Benchmarks](https://github.com/ChenxingLi/authenticated-storage-benchmarks) by following the instructions provided in that repository.
5. Build and run the preconfigured [end-to-end evaluations](https://github.com/Conflux-Chain/conflux-rust/tree/asb-e2e) for the authenticated storage based on Conflux-rust by following the instructions provided in that repository.
6. Clone the repository and navigate to the project directory:
    
    ```bash
    git clone https://github.com/ChenxingLi/asb-plotter.git
    cd asb-plotter
    ```
    
7. Specify the relative path of Authenticated Storage Benchmarks and Conflux-rust in the `path.py` file of this repository. For example, if your directory structure is:
    
    ```
    your-directory
    ├─ authenticated-storage-benchmarks
    ├─ conflux-rust
    └─ asb-plotter
    ```
    
    Open the `path.py` file in the `asb-plotter` directory and modify the values of `ASB_PATH` and `ASB_E2E_PATH` as follows:
    
    ```bash
    ASB_PATH = "../authenticated-storage-benchmarks"
    ASB_E2E_PATH = "../conflux-rust"
    ```
    
    These paths should be relative to the location of the `[path.py](http://path.py)` file. 
    
8. Parse the experiment results and plot figures by running the following command:
    
    ```
    python3 main.py
    ```
    
    This command will parse the experiment results and plot the figures in the paper. The figures will be saved in the `figures` directory.
import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument()
    parser.add_argument("--crawler", type=str, help="Input seed file for crawling")
    parser.add_argument("--input", type=str, help="graph specification")
    parser.add_argument("--loglogplot", action="store_true", help="Generates log-log plot of the degree distribution of the graph")
    parser.add_argument("--crawler_graph", type=str, help="Saves the processed graph to out_graph.gml")
    parser.add_argument("--pagerank_values", type=str, help="adds the pagerank values")
    return parser.parse_args()

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            max_nodes = int(lines[0])
            domain = lines[1]
            seeds = lines[2:]
            return max_nodes, domain, seeds
    except Exception as e:
        print(f"Error reading crawler file: {e}")
        return None, None, None
    
def plot_loglog_degree(graph):
    degrees = [graph.degree(n) for n in graph.nodes()]
    values, counts = np.unique(degrees, return_counts=True)
    plt.figure()
    plt.loglog(values, counts, marker="o", linestyle="None")
    plt.title("Log-log plot of degree distribution")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

def plot_graph(graph):
    pass

def main():
    args = argument_parser()
    graph = None
    if args.input:
        try:
            graph = nx.read_file(args.input)
            print(f"Loaded {args.input}")
        except FileNotFoundError:
            print(f"Error: file {args.input} not found.")

    pass

if __name__ == "__main__":
    main()
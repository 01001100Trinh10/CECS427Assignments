import numpy as np
import argparse
import networkx as nx
import matplotlib as plt

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", type=str, help="Path to the .gml file")
    parser.add_argument("n", type=int, help="Number of vehicles")
    parser.add_argument("initial", type=int, help="Start node")
    parser.add_argument("final", type=int, help="End node")
    parser.add_argument("--plot", action="store_true", help="Plot the graph")
    return  parser.parse_args()

def cost_function(x, a, b):
    return a * x + b

def compute_nash_equilibrium(graph, n, start, end):
    flow_distribution = {edge: n / len(graph.edges) for edge in graph.edges}
    return flow_distribution

def plot_graph(graph):
    pos = nx.spring_layout(graph)
    edge_labels = {(u, v): f"{graph[u][v]['a']}x+{graph[u][v]['b']}" for u, v in graph.edges}
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    plt.show()

def main():
    args = parse_arguments()
    graph = nx.read_gml(args.graph_file)

if __name__ == "__main__":
    main()
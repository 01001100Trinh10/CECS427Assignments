import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import argparse

# Creates random graph and save it as a gml
def create_random_graph(n, c, gml):
    # Given equation for the probability of generation of nodes ((c)ln(n))/(n) where n is the number of nodes
    p = c * np.log(n)
    p = p / n
    graph = nx.erdos_renyi_graph(n, p)
    if graph:
        nx.write_gml(graph, gml)
    print(f"Graph with {n} nodes created and saved to {gml}.")


# Read gml then use BFS to form a tree
def bfs(gml, start):
    # Error handling if the starting node is not in the graph
    if start not in graph:
        raise ValueError(f"Node {start} is not in the graph!")

    # Reads gml file
    graph = nx.read_gml(gml)

    # Performs bfs on the graph
    bfsTree = nx.bfs_tree(graph, start)
    
    plt.figure(figsize=(10, 8))
    plt.title('BFS Tree')

def main():
    parser = argparse.ArgumentParser(description="Erdős-Rényi Random Graph Generator and Analyzer")
    parser.add_argument("--input", help="Load GML for BFS")
    parser.add_argument("--create_random_graph", help="Create random gml graph")
    parser.add_argument("--nodes", help="Number of nodes for the graph")
    parser.add_argument("--constant", help="Constant for edge probability")
    parser.add_argument("--BFS", help="BFS based on start node")
    parser.add_argument("--plot", help="Visualizes graph")
    parser.add_argument("--output", help="Defines gml file where the graph will be saved")

    args =  parser.parse_args()
    

if __name__ == "__main__":
    main()
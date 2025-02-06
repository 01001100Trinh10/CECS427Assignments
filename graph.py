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
    graph = nx.relabel_nodes(graph, {i: str(i) for i in graph.nodes()})
    if graph:
        nx.write_gml(graph, gml)
    print(f"Graph with {n} nodes created and saved to {gml}.")


# Read gml then use BFS to form a tree
def bfs_shortest_path(graph, start):
    if start not in graph:
        raise ValueError(f"Node {start} is not in the graph.")
    shortestPath = nx.single_source_shortest_path(graph, start)
    return shortestPath

def parser_arguments():
    parser = argparse.ArgumentParser(description="Erdős-Rényi Random Graph Generator and Analyzer")
    parser.add_argument("--input", help="Load GML for BFS")
    parser.add_argument("--create_random_graph", nargs=2, type=float, metavar=("n", "c"), help="Create random gml graph")
    parser.add_argument("--nodes", help="Number of nodes for the graph")
    parser.add_argument("--constant", help="Constant for edge probability")
    parser.add_argument("--BFS", help="BFS based on start node")
    parser.add_argument("--plot", action="store_true", help="Visualizes graph")
    parser.add_argument("--output",help="Defines gml file where the graph will be saved")

    return  parser.parse_args()
    
def main():
    args = parser_arguments()
    graph = None

    if args.input:
        try:
            graph = nx.read_gml(args.input)
            print(f"Loaded graph from {args.input}.")
        except FileNotFoundError:
            print(f"Error: File {args.input} not found.")

    if args.create_random_graph:
        n, c = args.create_random_graph
        n = int(n)
        c = float(c)
        create_random_graph(n, c, args.output)

    if args.BFS:
        if graph is None:
            print("Error: No graph available for BFS")
            return
        if args.BFS not in graph.nodes():
            print(f"Error: Node {args.BFS} not found in the graph")      
            return
        
        shortest_paths = bfs_shortest_path(graph, args.BFS)
        for node, path in shortest_paths.items():
            print(f"Shortest path to {node}: {path}")
        
    if args.plot and graph:
        plt.figure(figsize=(8, 6))
        nx.draw(graph, with_labels=True, node_color="lightblue", edge_color="gray", node_size=500)
        plt.show()

    if args.output and graph:
        nx.write_gml(graph, args.output)
        print(f"Graph saved to {args.output}")

if __name__ == "__main__":
    main()
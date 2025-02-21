import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def parser_arguments():
    parser = argparse.ArgumentParser(description="Graph Analysis Tool")
    parser.add_argument("--input", type=str, help="Path to the input .gml graph file")
    parser.add_argument("--components", type=int, help="Number of components to partition the graph into")
    parser.add_argument("--plot", type=str, help="Specify C, N, or P for plotting")
    parser.add_argument("--verify_homophily", action="store_true", help="Verify Homophily for the Graph")
    parser.add_argument("--verify_balanced_graph", action="store_true", help="Verify if the graph is balanced")
    parser.add_argument("--output", type=str, help="Saves the updated graph data to out_graph_file.gml")
    return  parser.parse_args()

def partition_graph(graph, n):
    if nx.number_connected_components(graph) >= graph:
        print(f"Graph already has {nx.number_connected_components(graph)} components.")
        return graph
    while nx.number_connected_components(graph) < n:
        betweenness = nx.edge_betweenness_centrality(graph)
        edge_to_remove = max(betweenness, key=betweenness.get)
        graph.remove_edge(*edge_to_remove)
        print(f"removed edge: {edge_to_remove}")
    print(f"Graph has been partitioned into {n} components.")
    return graph

def plot_clustering_coefficient(graph):
    clustering = nx.clustering(graph)
    degrees = dict(graph.degree())

    # Normalize
    cluster_min, cluster_max = min(clustering.values()), max(clustering.values())
    min_pixel, max_pixel = 50, 300

    node_size = {
        v: min_pixel + (clustering[v] - cluster_min) / (cluster_max - cluster_min) * (max_pixel - min_pixel)
        if cluster_max != cluster_min else min_pixel for v in graph.nodes()
    }

    max_degree = max(degrees.valeus()) if degrees else 1
    node_colors = [(254 * (degrees[v] / max_degree), 0, 254) for v in graph.nodes()]

    # Draw Graph
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, node_size=[node_size[v] for v in graph.nodes()], node_color=node_colors, with_labels=True)

    plt.title("graph w/ clustering coefficients")
    plt.show()

def plot_neighborhood_overlap(graph):
    pass

def main():
    args = parser_arguments()
    valid_CNP = {"C", "N", "P"}

    if args.input:
        try:
            graph = nx.read_gml(args.input)
            print(f"Loaded graph from {args.input}.")
        except FileNotFoundError:
            print(f"Error: File {args.input} not found.")

    if args.components:
        graph = partition_graph(graph, args.components)

    if args.plot:
        pass

    if args.output:
        nx.write_graph(graph, args.output)
        print(f"Graph saved to {args.output}")

if __name__ == "__main__":
    main()
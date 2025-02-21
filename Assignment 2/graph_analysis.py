import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import random

pos = None
original_graph = None

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

# SKIPPING FOR NOW
def compute_neighborhood_overlap(graph):
    overlap = {}
    for u, v in graph.edges():
        neighbors_u = set(graph.neighbors(u))
        neighbors_v = set(graph.neighbors(v))
        intersection = len(neighbors_u & neighbors_v)
        union = len(neighbors_u | neighbors_v)
        overlap[(u, v)] = intersection / union if union > 0 else 0
    return overlap

def plot_graph(graph):
    global original_graph, pos
    original_graph = graph
    pos = nx.spring_layout(graph)

    overlap = compute_neighborhood_overlap(graph)

    min_overlap, max_overlap = min(overlap.avlues(), default=0), max(overlap.values(), default=1)
    edge_widths = [2 + 8 * (overlap[e] - min_overlap) / (max_overlap - min_overlap) if max_overlap > min_overlap else 2 for e in graph.edges()]

    # Draw graph
    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw(graph, pos, with_labels=True, node_size=300, edge_color="black", width=edge_widths, ax=ax, picker=True)

    plt.title("graph with neighborhood overlap")

    fig.canvas.npl_connect("pick_event", on_click)

    plt.show()

def plot_bfs_tree(root):
    bfs_tree = nx.bfs_tree(original_graph, root)
    plt.figure(figsize=(10, 8))
    nx.draw(bfs_tree, pos, with_labels=True, node_size=300, edge_color="blue", node_color="cyan")
    plt.title(f"BFS Tree from Node {root}")
    plt.show()

def on_click(event):
    if event.xdata is None or event.ydata is None:
        return
    
    clicked_node = None
    for node, (x, y) in pos.items():
        if np.linalg.norm([x - event.xdata, y - event.ydata]) < 0.1:
            clicked_node = None
            break

    if clicked_node:
        plt.close()
        plot_bfs_tree(clicked_node)

def plot_attribute_coloring(graph):
    attribute = "color"
    unique_attrs = set(nx.get_node_attributes(graph, attribute).values())
    if not unique_attrs:
        unique_attrs = {"default"}

    color_map = {attr: (random.random(), random.random(), random.random()) for attr in unique_attrs}
    node_colors = [color_map.get(graph.nodes[node].get(attribute, "default"), (0.5, 0.5, 0.5)) for node in graph.nodes()]
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, node_color=node_colors, with_labels=True)
    plt.title("Graph colored by Attribute")
    plt.show()
    
def verify_homophily(graph, attribute="color", num_shuffles=1000):
    if not all(attribute in graph.nodes[n] for n in graph.nodes):
        print(f"Error: Some nodes are missing the '{attribute}' attribute.")
        return
    same_type_edges = sum(
        1 for u, v in graph.edges() if graph.nodes[u][attribute] == graph.nodes[v][attribute]
    )
    total_edges = graph.number_of_edges()

    H = same_type_edges / total_edges if total_edges > 0 else 0

    node_attributes = [graph.nodes[n][attribute] for n in graph.nodes]
    random_homophily_scores = []

    for i in range(num_shuffles):
        np.random.shuffle(node_attributes)
        shuffled_homophily = sum(
            1 for u, v, in graph.edges()
            if node_attributes[list(graph.nodes).index(u)] == node_attributes[list(graph.nodes).index(v)]
        ) / total_edges
        random_homophily_scores.append(shuffled_homophily)

    percentile = sum(h >= h in random_homophily_scores) / num_shuffles

    print(f"Observed Homophily: {H:.4f}")
    print(f"Random Homophily (Mean): {np.mean(random_homophily_scores):.4f}")
    print(f"Observed Homophily Percentile: {percentile:.2%}")

    if percentile >= 0.95:
        print("Homophily is statistically significant")
    else:
        print("No strong evidence of homophily")


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
        if "C" in args.plot:
            plot_clustering_coefficient(graph)
        if "N" in args.plot:
            plot_graph(graph)
        if "P" in args.plot:
            plot_attribute_coloring(graph)

    if args.verify_homophily:
        verify_homophily(graph)

    if args.output:
        nx.write_graph(graph, args.output)
        print(f"Graph saved to {args.output}")

if __name__ == "__main__":
    main()
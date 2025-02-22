import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import ttest_1samp
import random

pos = None
original_graph = None

# Combines arguments together to take any input in any order
def parser_arguments():
    parser = argparse.ArgumentParser(description="Graph Analysis Tool")
    parser.add_argument("graph_file", type=str, help="Path to the input .gml graph file")
    parser.add_argument("--components", type=int, help="Number of components to partition the graph into")
    parser.add_argument("--plot", type=str, help="Specify C, N, or P for plotting")
    parser.add_argument("--verify_homophily", action="store_true", help="Verify Homophily for the Graph")
    parser.add_argument("--verify_balanced_graph", action="store_true", help="Verify if the graph is balanced")
    parser.add_argument("--output", type=str, help="Saves the updated graph data to out_graph_file.gml")
    return  parser.parse_args()

def partition_graph(graph, n):
    if nx.number_connected_components(graph) >= n:
        print(f"Graph already has {nx.number_connected_components(graph)} components.")
        return graph
    while nx.number_connected_components(graph) < n:
        betweenness = nx.edge_betweenness_centrality(graph)
        edge_to_remove = max(betweenness, key=betweenness.get)
        graph.remove_edge(*edge_to_remove)
        print(f"removed edge: {edge_to_remove}")
    print(f"Graph has been partitioned into {n} components.")
    return graph

# Plots the graph highlighting clustering coefficients
def plot_clustering_coefficient(graph):
    # Compute node positions
    pos = nx.spring_layout(graph)
    
    # Compute clustering coefficients
    clustering_coeffs = nx.clustering(graph)
    cluster_min = min(clustering_coeffs.values())
    cluster_max = max(clustering_coeffs.values())

    # Compute node sizes based on clustering coefficient
    # Define min and max sizes
    min_pixel, max_pixel = 100, 1000 
    node_size = {
        v: min_pixel + ((clustering_coeffs[v] - cluster_min) / (cluster_max - cluster_min) * (max_pixel - min_pixel))
        if cluster_max > cluster_min else min_pixel  # Avoid division by zero
        for v in graph.nodes()
    }

    # Compute node colors based on degree
    degrees = dict(graph.degree())
    max_degree = max(degrees.values())

    # Normalize to [0, 1]
    normalized_degrees = {v: degrees[v] / max_degree for v in graph.nodes()}
    
    # Assign the colors so that Blue low degree and Magenta as high degree
    node_colors = [(sv, 0, 1) for sv in normalized_degrees.values()]
    
    # Draw the graph
    plt.figure(figsize=(10, 7))
    nx.draw(
        graph, pos,
        node_size=[node_size[v] for v in graph.nodes()],
        # Use normalized colors
        node_color=node_colors,
        with_labels=True
    )
    
    plt.show()

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

    min_overlap, max_overlap = min(overlap.values(), default=0), max(overlap.values(), default=1)
    edge_widths = [
        2 + 8 * (overlap[e] - min_overlap) / (max_overlap - min_overlap)
        if max_overlap > min_overlap else 2
        for e in graph.edges()
    ]

    # Draw graph
    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw nodes and edges separately
    node_scatter = nx.draw_networkx_nodes(graph, pos, ax=ax, node_size=300)
      
    # Set picker manually (5 pixels tolerance for clicks)
    node_scatter.set_picker(5)  # Set picker manually (5 pixels tolerance for clicks)

    nx.draw_networkx_edges(graph, pos, ax=ax, edge_color="black", width=edge_widths)
    nx.draw_networkx_labels(graph, pos, ax=ax)

    plt.title("Graph with Neighborhood Overlap")

    # Connect click event
    fig.canvas.mpl_connect("pick_event", on_click)

    plt.show()


def plot_bfs_tree(root):
    bfs_tree = nx.bfs_tree(original_graph, root)
    pos = hierarchy_pos(bfs_tree, root)
    
    plt.figure(figsize=(12, 10))
    nx.draw(bfs_tree, pos, with_labels=True, node_size=300, edge_color="blue", node_color="cyan")
    plt.title(f"BFS Tree from Node {root}")
    plt.show()

def hierarchy_pos(G, root=None, width=2.0, vert_gap=0.5, vert_loc=0, xcenter=0.5):
    pos = _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
    return pos

def _hierarchy_pos(G, root, width=2.0, vert_gap=0.5, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
        
    children = list(G.neighbors(root))
    if not isinstance(G, nx.DiGraph) and parent is not None:
        children.remove(parent)  
        
    if len(children) != 0:
        dx = width / len(children) 
        nextx = xcenter - width/2 - dx/2
        for child in children:
            nextx += dx
            pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc-vert_gap, xcenter=nextx, pos=pos, parent=root, parsed=parsed)
    
    return pos

def on_click(event):
    # Get the index of the clicked node(s)
    ind = event.ind 
    if ind is not None and len(ind) > 0:
        # Get corresponding node
        clicked_node = list(original_graph.nodes())[ind[0]] 
        print(f"Clicked on node: {clicked_node}")

        # Close the current plot and show BFS tree
        plt.close()
        plot_bfs_tree(clicked_node)


def plot_attribute_coloring(graph):
    attribute = "color"
    unique_attrs = set(nx.get_node_attributes(graph, attribute).values())
    if not unique_attrs:
        unique_attrs = {"default"}

    color_map = {attr: (random.random(), random.random(), random.random()) for attr in unique_attrs}
    node_colors = [color_map.get(graph.nodes[node].get(attribute, "default"), (0.5, 0.5, 0.5)) for node in graph.nodes()]
    edge_colors = []
    for u, v in graph.edges():
        if 'sign' in graph.edges[u, v]:
            if graph.edges[u, v]['sign'] == '+':
                edge_colors.append('red')
            elif graph.edges[u, v]['sign'] == '-':
                edge_colors.append('black')
            else:
                edge_colors.append('gray')
        else:
            edge_colors.append('gray')
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, node_color=node_colors, edge_color=edge_colors, with_labels=True)
    plt.title("Graph colored by Attribute")
    plt.show()
    
# Test for homophily based on a categorical node attribute
def verify_homophily(graph, attribute="color"):
    # Check if all nodes have the attribute
    if not all(attribute in graph.nodes[n] for n in graph.nodes):
        print(f"Error: Some nodes are missing the '{attribute}' attribute.")
        return
    
    same_type_edges = 0
    total_edges = graph.number_of_edges()

    # Count edges where both nodes share the same attribute
    for u, v in graph.edges():
        if graph.nodes[u][attribute] == graph.nodes[v][attribute]:
            same_type_edges += 1

    # Compute homophily ratio
    H = same_type_edges / total_edges if total_edges > 0 else 0

    # Generate random expectation for homophily (null hypothesis)
    node_attributes = [graph.nodes[n][attribute] for n in graph.nodes]
    random_homophily_scores = []
    
    # 1000 random shuffles
    for _ in range(1000):
        np.random.shuffle(node_attributes)
        shuffled_homophily = sum(
            node_attributes[list(graph.nodes).index(u)] == node_attributes[list(graph.nodes).index(v)]
            for u, v in graph.edges()
        ) / total_edges
        random_homophily_scores.append(shuffled_homophily)
    
    # Perform Student's t-test
    t_stat, p_value = ttest_1samp(random_homophily_scores, H)

    # Display results
    print(f"Observed Homophily: {H:.4f}")
    print(f"T-test p-value: {p_value:.4f}")

    if p_value < 0.05:
        print("Homophily is statistically significant (p < 0.05)")
    else:
        print("No strong evidence of homophily")

def verify_balanced_graph(graph):
    balanced = True
    cycles = list(nx.cycle_basis(graph))
    for cycle in cycles:
        negative_edges = 0
        for i in range(len(cycle)):
            u, v = cycle[i], cycle[(i + 1) % len(cycle)]
            if graph[u][v]["sign"] == "-":
                negative_edges += 1
        if negative_edges % 2 != 0:
            balanced = False
            break
    if balanced is True:
        print("balanced")
    else:
        print("NOT balanced")


def main():
    # Fetch arg combination
    args = parser_arguments()

    # Reads gml file
    graph = nx.read_gml(args.graph_file)

    # Calls partition_graph
    if args.components:
        graph = partition_graph(graph, args.components)

    # Plots graph based on if they receive C, N, or P
    if args.plot:
        if "C" in args.plot:
            plot_clustering_coefficient(graph)
        if "N" in args.plot:
            plot_graph(graph)
        if "P" in args.plot:
            plot_attribute_coloring(graph)

    # Verifies if the graph has evidence of a homophily
    if args.verify_homophily:
        verify_homophily(graph)

    # Verifies if the graph is balanced
    if args.verify_balanced_graph:
        verify_balanced_graph(graph)

    # Saves the file into an output file
    if args.output:
        nx.write_graph(graph, args.output)
        print(f"Graph saved to {args.output}")

if __name__ == "__main__":
    main()
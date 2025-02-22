import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import random

pos = None
original_graph = None

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

def plot_clustering_coefficient(graph):
    """Plots the graph highlighting clustering coefficients."""
    
    pos = nx.spring_layout(graph)  # Compute node positions
    
    # Compute clustering coefficients
    clustering_coeffs = nx.clustering(graph)
    cluster_min = min(clustering_coeffs.values())
    cluster_max = max(clustering_coeffs.values())

    # Compute node sizes based on clustering coefficient
    min_pixel, max_pixel = 100, 1000  # Define min and max sizes
    node_size = {
        v: min_pixel + ((clustering_coeffs[v] - cluster_min) / (cluster_max - cluster_min) * (max_pixel - min_pixel))
        if cluster_max > cluster_min else min_pixel  # Avoid division by zero
        for v in graph.nodes()
    }

    # Compute node colors based on degree
    degrees = dict(graph.degree())
    max_degree = max(degrees.values())
    normalized_degrees = {v: degrees[v] / max_degree for v in graph.nodes()}  # Normalize to [0, 1]
    
    # Assign color: Blue (low degree) → Magenta (high degree)
    node_colors = [(sv, 0, 1) for sv in normalized_degrees.values()]  # Matplotlib expects colors in range [0,1]
    
    # Draw the graph
    plt.figure(figsize=(10, 7))
    nx.draw(
        graph, pos,
        node_size=[node_size[v] for v in graph.nodes()],
        node_color=node_colors,  # Use normalized colors
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
    node_scatter = nx.draw_networkx_nodes(graph, pos, ax=ax, node_size=300)  # No picker argument here
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
    ind = event.ind  # Get the index of the clicked node(s)
    if ind is not None and len(ind) > 0:
        clicked_node = list(original_graph.nodes())[ind[0]]  # Get corresponding node
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

    percentile = sum(h >= H for h in random_homophily_scores) / num_shuffles

    print(f"Observed Homophily: {H:.4f}")
    print(f"Random Homophily (Mean): {np.mean(random_homophily_scores):.4f}")
    print(f"Observed Homophily Percentile: {percentile:.2%}")

    if percentile >= 0.95:
        print("Homophily is statistically significant")
    else:
        print("No strong evidence of homophily")

def verify_balanced_graph(graph):
    if not all('sign' in graph.edges[edge] for edge in graph.edges):
        print("Error: Some edges are missing the 'sign' attribute.")
        return
    
    unbalanced_triangles = 0
    balanced_triangles = 0

    def convert_sign(sign):
        return 1 if sign == "+" else -1 if sign == "-" else int(sign)

    for triangle in nx.enumerate_all_cliques(graph):
        if len(triangle) == 3:
            u, v, w = triangle

            if not (graph.has_edge(u, v) and graph.has_edge(v, w) and graph.has_edge(w, u)):
                print(f"Error: Missing edge in triangle {u}-{v}-{w}")
                continue

            try:
                # Convert 'sign' attribute safely
                sign_uv = convert_sign(graph.edges[u, v]['sign'])
                sign_vw = convert_sign(graph.edges[v, w]['sign'])
                sign_wu = convert_sign(graph.edges[w, u]['sign'])
            except ValueError:
                print(f"Error: Invalid sign attribute in edges {u}-{v}, {v}-{w}, {w}-{u}")
                return

            negative_edges = sum(s < 0 for s in [sign_uv, sign_vw, sign_wu])

            if negative_edges in [0, 2]:
                balanced_triangles += 1
            else:
                unbalanced_triangles += 1

    print(f"Balanced Triangles: {balanced_triangles}")
    print(f"Unbalanced Triangles: {unbalanced_triangles}")

    if unbalanced_triangles == 0:
        print("The graph is balanced.")
    else:
        print("The graph is NOT balanced.")


def main():
    args = parser_arguments()
    # valid_CNP = {"C", "N", "P"}

    graph = nx.read_gml(args.graph_file)

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

    if args.verify_balanced_graph:
        verify_balanced_graph(graph)

    if args.output:
        nx.write_graph(graph, args.output)
        print(f"Graph saved to {args.output}")

if __name__ == "__main__":
    main()
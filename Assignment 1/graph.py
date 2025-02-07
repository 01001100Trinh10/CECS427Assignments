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
    # Rewrites nodes as strings
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

# Combines arguments together to take any input in any order
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
    # Reads input and sets graph to None by default
    args = parser_arguments()
    graph = None

    # Reads graph. Throw error if the wrong graph was inputted
    if args.input:
        try:
            graph = nx.read_gml(args.input)
            print(f"Loaded graph from {args.input}.")
        except FileNotFoundError:
            print(f"Error: File {args.input} not found.")

    # Creates random graph. Also converts the values into integers before calculating the probability
    if args.create_random_graph:
        n, c = args.create_random_graph
        n = int(n)
        c = float(c)
        create_random_graph(n, c, args.output)
    
    # Plots graph, but only if there is a graph that exists
    if args.plot and graph:
        # Sets up graph
        plt.figure(figsize=(10, 8))
        # Reads BFS argument
        if args.BFS:
            try:
                # Computes bfs in the graph
                shortest_paths = bfs_shortest_path(graph, args.BFS)

                # Displays all the paths from root node and gives the length of teh path
                for node, path in shortest_paths.items():
                    print(f"Shortest path to {node}: {path}\nShortest path length to {node}: {len(path) - 1}")
                
                # Computes depth of the nodes
                bfs_levels = {}
                for node, path in shortest_paths.items():
                    bfs_levels[node] = len(path) - 1

                # Organizes nodes based on depth
                layers = {}
                for node, level in bfs_levels.items():
                    if level not in layers:
                        layers[level] = []
                    layers[level].append(node)

                # Assign hierarchical positions for BFS nodes
                bfs_pos = {}
                for level, nodes in layers.items():
                    for i, node in enumerate(nodes):
                        bfs_pos[node] = (i, -level)

                # Identifies nodes that are not reachable
                disconnected_nodes = set(graph.nodes()) - set(bfs_levels.keys())

                # Stores the unreachable nodes elseware using spring_layout
                extra_pos = nx.spring_layout(graph.subgraph(disconnected_nodes))

                # Merges BFS and extra positions to avoid missing nodes
                pos = {**bfs_pos, **extra_pos}
                
                # Draws all edges in gray and all the nodes to blue
                nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=500, font_size=10)

                # Extracts the edges part of the BFS tree
                bfs_edges = []
                for path in shortest_paths.values():
                    for i in range(len(path) - 1):
                        bfs_edges.append((path[i], path[i + 1]))

                # Overrides the BFS edges to be red to highlight the tree
                nx.draw_networkx_edges(graph, pos, edgelist=bfs_edges, edge_color="red", width=2)

                # Overrides the root node to be green
                nx.draw_networkx_nodes(graph, pos, nodelist=[args.BFS], node_color="green", node_size=700)
                print(f"Graph displayed in BFS hierarchical layout, starting from node {args.BFS}.")

            # Exception handler
            except ValueError as e:
                print(e)
        
        # Normal graph in case we don't call for a BFS
        else:
            pos = nx.spring_layout(graph)
            nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=500, font_size=10)

        # Displays graph
        plt.show()

    # Saves graph into gml and displays a success message
    if args.output and graph:
        nx.write_gml(graph, args.output)
        print(f"Graph saved to {args.output}")

# Running the actual code
if __name__ == "__main__":
    main()
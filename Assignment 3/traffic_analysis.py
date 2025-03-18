import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", type=str, help="Path to the .gml file")
    parser.add_argument("n", type=int, help="Number of vehicles")
    parser.add_argument("initial", type=int, help="Start node")
    parser.add_argument("final", type=int, help="End node")
    parser.add_argument("--plot", action="store_true", help="Plot the graph")
    return parser.parse_args()


def cost_function(flow, a, b):
    """Compute the travel cost for a given flow on an edge."""
    return (a * flow) + b


def compute_nash_equilibrium(graph, n, start, end):
    """
    Computes the Nash Equilibrium where each vehicle selfishly chooses the lowest-cost path
    and no vehicle can switch to improve their travel time.
    """
    flow_distribution = {edge: 0 for edge in graph.edges()}

    for _ in range(n):  # Distribute each vehicle
        shortest_path = nx.shortest_path(graph, source=start, target=end, weight=lambda u, v, d: cost_function(flow_distribution[(u, v)], d["a"], d["b"]),)

        # Increase flow along the chosen path
        for i in range(len(shortest_path) - 1):
            edge = (shortest_path[i], shortest_path[i + 1])
            flow_distribution[edge] += 1

    return flow_distribution


def social_objective(flow, graph):
    """
    Computes the total system cost for a given flow.
    """
    total_cost = 0
    for (u, v), f in flow.items():
        a, b = graph[u][v]["a"], graph[u][v]["b"]
        total_cost += cost_function(f, a, b) * f  # Total system cost
    return total_cost


def compute_social_optimum(graph, vehicles, start, end):
    """Compute the socially optimal path that minimizes the total system cost."""
    all_paths = list(nx.all_simple_paths(graph, start, end))
    min_cost = float("inf")
    best_path = None

    for path in all_paths:
        total_cost = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            a, b = graph[u][v]["a"], graph[u][v]["b"]
            total_cost += sum(cost_function(x, a, b) for x in range(1, vehicles + 1))

        if total_cost < min_cost:
            min_cost = total_cost
            best_path = path

    # Initialize flow distribution dictionary
    flow_distribution = {edge: 0 for edge in graph.edges()}

    # Assign all vehicles to the best path
    if best_path:
        for i in range(len(best_path) - 1):
            edge = (best_path[i], best_path[i + 1])
            flow_distribution[edge] = vehicles

    return flow_distribution


def plot_graph(graph, nash_eq):
    pos = nx.shell_layout(graph)
    edge_labels = {}

    for u, v in graph.edges():
        a, b = graph[u][v]["a"], graph[u][v]["b"]
        flow = nash_eq.get((u, v), 0)
        # travel_time = cost_function(flow, a, b)
        # potential = travel_time * flow
        edge_labels[(u, v)] = f"{a}x+{b}\nDrivers: {flow}"

    nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray", arrows=True)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.show()


def main():
    args = parse_arguments()
    graph = nx.read_gml(args.graph_file)

    start = str(args.initial)
    end = str(args.final)

    # Ensure all edges have 'a' and 'b' attributes
    for u, v in graph.edges():
        if "a" not in graph[u][v] or "b" not in graph[u][v]:
            raise ValueError(f"Edge ({u}, {v}) is missing 'a' or 'b' attributes")

    nash_eq = compute_nash_equilibrium(graph, args.n, start, end)
    social_opt = compute_social_optimum(graph, args.n, start, end)

    NE_PE = 0
    SO_PE = 0

    print("Nash Equilibrium:")
    for edge, flow in nash_eq.items():
        print(f"Edge {edge}: {flow} vehicles")
        NE_PE += int(flow)
    print(f"Potential Energy: {NE_PE}")

    print("\nSocial Optimum:")
    for edge, flow in social_opt.items():
        print(f"Edge {edge}: {flow} vehicles")
        SO_PE += int(flow)
    print(f"Potential Energy: {SO_PE}")

    if args.plot:
        plot_graph(graph, nash_eq)


if __name__ == "__main__":
    main()

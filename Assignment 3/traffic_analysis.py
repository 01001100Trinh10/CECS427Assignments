import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt

# Combines arguments together to take any input in any order
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", type=str, help="Path to the .gml file")
    parser.add_argument("n", type=int, help="Number of vehicles")
    parser.add_argument("initial", type=int, help="Start node")
    parser.add_argument("final", type=int, help="End node")
    parser.add_argument("--plot", action="store_true", help="Plot the graph")
    return parser.parse_args()


def cost_function(flow, a, b):
    #Compute the travel cost for a given flow on an edge.
    return ((a * flow) + b)

# Gets potential energy
def pe(flow, a, b):
    nflow = 0
    nb = 0
    while(flow != 0):
        nflow += flow
        nb += 1
        flow -= 1
    return (a * nflow) + (b * nb)

# Gets travel time
def tt(flow, a, b):
    f = 0
    # In case a in ax is 0
    if (a != 0):
        f = flow
    return (f * flow) + (b * flow)

def compute_nash_equilibrium(graph, n, start, end):
    #Computes the Nash Equilibrium where each vehicle selfishly chooses the lowest-cost path and no vehicle can switch to improve their travel time.
    flow_distribution = {edge: 0 for edge in graph.edges()}

    for _ in range(n):  # Distribute each vehicle
        shortest_path = nx.shortest_path(graph, source=start, target=end, weight=lambda u, v, d: cost_function(flow_distribution[(u, v)], d["a"], d["b"]),)

        # Increase flow along the chosen path
        for i in range(len(shortest_path) - 1):
            edge = (shortest_path[i], shortest_path[i + 1])
            flow_distribution[edge] += 1

    return flow_distribution

def compute_social_optimum(graph, vehicles, start, end, flow_distribution=None):
    #Recursively compute the social optimum by distributing vehicles to minimize total system cost.
    
    if flow_distribution is None:
        flow_distribution = {edge: 0 for edge in graph.edges()}  # Initialize flow distribution

    # Base Case if all vehicles are assigned, return the distribution
    if vehicles == 0:
        return flow_distribution

    # Get all simple paths from start to end
    all_paths = list(nx.all_simple_paths(graph, start, end))

    if not all_paths:
        return flow_distribution  # No valid paths

    # Compute the total system cost for each path **with all vehicles**
    path_costs = []
    for path in all_paths:
        total_cost = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            a, b = graph[u][v]["a"], graph[u][v]["b"]
            flow = flow_distribution[(u, v)] + 1
            for j in range(1, vehicles + 1):
                total_cost += tt(flow, a, b)
                total_cost += cost_function(flow, a, b)
            # total_cost += sum(tt(flow, a, b) for x in range(1, vehicles + 1))  # Consider all vehicles
        
        path_costs.append((path, total_cost))

    # Select the path
    path_costs.sort(key=lambda x: x[1])  # Sort paths by total system cost
    best_path = path_costs[0][0]  # Best path based on min cost

    # Assign a vehicle
    for i in range(len(best_path) - 1):
        edge = (best_path[i], best_path[i + 1])
        flow_distribution[edge] += 1

    # Recursive call with one less vehicle
    return compute_social_optimum(graph, vehicles - 1, start, end, flow_distribution)


def plot_graph(graph, eq):
    pos = nx.spring_layout(graph)
    edge_labels = {}

    for u, v in graph.edges():
        a, b = graph[u][v]["a"], graph[u][v]["b"]
        flow = eq.get((u, v), 0)
        potential = pe(flow, a, b)
        edge_labels[(u, v)] = f"{a}x+{b}\nDrivers: {flow}\nTravel Time: {tt(flow, a, b)}\nPotential Power: {potential}"

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

    totaltt1 = 0
    totaltt2 = 0
    totalpe1 = 0
    totalpe2 = 0
    print("Nash Equilibrium:")
    for edge, flow in nash_eq.items():
        a = graph[edge[0]][edge[1]]["a"]
        b = graph[edge[0]][edge[1]]["b"]
        pp = pe(flow, a, b)
        totalpe1 += pp
        totaltt1 += tt(flow, a, b)
        print(f"Edge {edge}: {flow} vehicles, Travel Time: {tt(flow, a, b)}, Potential Power: {pp}")
    print(f"Social Cost {totaltt1}\nPotential Power {totalpe1}")

    print("\nSocial Optimum:")
    for edge, flow in social_opt.items():
        a = graph[edge[0]][edge[1]]["a"]
        b = graph[edge[0]][edge[1]]["b"]
        pp = pe(flow, a, b)
        totalpe2 += pp
        totaltt2 += tt(flow, a, b)
        print(f"Edge {edge}: {flow} vehicles, Travel Time: {tt(flow, a, b)}, Potential Power: {pp}")
    print(f"Social Cost {totaltt2}\nPotential Power {totalpe2}")

    if args.plot:
        plot_graph(graph, nash_eq)
        plot_graph(graph, social_opt)


if __name__ == "__main__":
    main()

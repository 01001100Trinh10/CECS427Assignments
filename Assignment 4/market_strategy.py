import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt

def parser_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", type=str, help="Path to .gml file")
    parser.add_argument("--plot", action="store_true", help="Plot the graph")
    parser.add_argument("--interactive", action="store_true", help="Shows the output of every round graph")
    return parser.parse_args

def get_bipartite_sets(graph):
    A = [node for node in graph.nodes if int(node) < len(graph.nodes // 2)]
    B = [node for node in graph.nodes if int(node) >= len(graph.nodes) // 2]
    return A, B

def build_preference_graph(graph, A, B):
    pref_graph = nx.DiGraph()

    for b in B:
        max_profit = float('-inf')
        best_sellers = []

    for a in A:
        if graph.has_edge(b, a):
            value = graph.edge[b, a]['value']
            price = graph.nodes[a]['price']
            profit = value - price
            if profit > max_profit:
                max_profit = profit
                best_sellers = [a]
            if profit == max_profit:
                best_sellers.append(a)
        
        for a in best_sellers:
            pref_graph.add_edge(b, a)
    return pref_graph

def find_maximum_matching(pref_graph):
    matching = {}
    for b in pref_graph.nodes:
        for a in pref_graph.successors(b):
            if a not in matching.values():
                matching[b] = a
                break
    return matching

def find_constricted_set(pref_graph, matching, A, B):
    unmatched_buyers = [b for b in B if b not in matching]
    visited_buyers = set()
    reachable_sellers = set()

    queue = unmatched_buyers[:]
    while queue:
        b = queue.pop(0)
        for a in pref_graph.successors(b):
            reachable_sellers.add(a)
            # If matched, we explore matched buyer
            matched_buyer = [buyer for buyer, seller in matching.items() if seller == a]
            if matched_buyer:
                next_b = matched_buyer[0]
                if next_b not in visited_buyers:
                    queue.append(next_b)
    return reachable_sellers

def update_prices(graph, constricted_sellers, increment=1):
    for a in constricted_sellers:
        graph.nodes[a]['price'] += increment

def plot_graph(graph, A, B):
    pos = {}
    pos.update((node, (1, i)) for i, node in enumerate(A))
    pos.update((node, (2, i)) for i, node in enumerate(B))

    plt.figure(figsize=(10, 6))
    nx.draw(graph, pos, with_labels=True, node_color='blue', edge_color='black')
    edge_labels = nx.get_edge_attributes(graph, 'value')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    plt.title("Bipartite Market Graph")
    plt.show()

def market_clearing(graph, A, B):
    round_number = 0
    while True:
        print(f"\n--- Round {round_number} ---")
        pref_graph = build_preference_graph(graph, A, B)
        matching = find_maximum_matching(pref_graph)
        print(f"Matching size: {len(matching)}")
        print("Matching:")
        for b, a in matching.items():
            print(f"    Buyer {b} -> Seller {a}")
        if len(matching) == len(B):
            print("Market cleared.")
            break
        constricted = find_constricted_set(pref_graph, matching, A, B)
        if not constricted:
            print("No constricted set found")
            break
        print(f"Constricted sellers: {constricted}")
        update_prices(graph, constricted)
        round_num += 1


def main():
    args = parser_arguments()
    graph = nx.read_graph(args.graph_file)
    if args.plot:
        pass
        plot_graph(graph)

    if args.interactive:
        pass

if __name__ == "__main__":
    main()
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import sys
from collections import defaultdict

def parser_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", type=str, help="Path to .gml file")
    parser.add_argument("--plot", action="store_true", help="Plot the graph")
    parser.add_argument("--interactive", action="store_true", help="Shows the output of every round graph")
    return parser.parse_args()

def get_bipartite_sets(graph):
    sellers = [node for node in graph.nodes if graph.nodes[node].get('bipartite') == 0]
    buyers = [node for node in graph.nodes if graph.nodes[node].get('bipartite') == 1]
    prices = {seller: graph.nodes[seller]['price'] for seller in sellers}

    valuations = defaultdict(dict)
    for buyer in buyers:
        for seller in sellers:
            if graph.has_edge(buyer, seller):
                valuations[buyer][seller] = graph.edges[buyer, seller]['valuation']
            elif graph.has_edge(seller, buyer):
                valuations[buyer][seller] = graph.edges[seller, buyer]['valuation']
            else:
                valuations[buyer][seller] = float('-inf')

    return sellers, buyers, prices, valuations

def build_preference_set(sellers, buyers, prices, valuations):
    pref_set = {}

    for b in buyers:
        max_profit = float('-inf')
        best_sellers = []

        for s in sellers:
            profit = valuations[b][s] - prices[s]

            if profit > max_profit:
                max_profit = profit
                best_sellers = [s]
            elif profit == max_profit:
                best_sellers.append(s)
        pref_set = best_sellers
    return pref_set

def pref_graph(sellers, buyers, prices, valuations, pref_set):
    G = nx.DiGraph()
    G.add_nodes_from(sellers, bipartite=0)
    G.add_nodes_from(buyers, bipartite=1)

    for b in buyers:
        for s in pref_set[b]:
            profit = valuations[b][s] - prices[s]
            G.add_edge(b, s, weight=profit)

    return G

def find_constricted_set(G, sellers, buyers):
    matching = nx.bipartite.maximum_matching(G, top_nodes = buyers)
    if len(matching) == 2 * len(self.buyers):
        return None
    unmatched_buyers = [b for b in buyers if b not in matching]

    res = nx.DiGraph()
    res.add_nodes_from(G.nodes())
    for i, j in G.edges():
        if j in matching and matching[j] == i:
            res.add_edge(j, i)
        else:
            res.add_edge(i, j)

    constricted = set()
    neighborhood = set()
    for k in unmatched_buyers:
        visited = set()
        queue = [k]
        while queue:
            node = queue.pop()
            if node in visited:
                continue
            visited.add(node)
            if node in buyers:
                constricted.add(node)
            for neighbor in res.neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)
                    if neighbor in sellers:
                        neighborhood.add(neighbor)

    return (list(constricted), list(neighborhood)) if constricted else None


def update_prices(graph, sellers, buyers, prices, valuations, constricted):
    if not constricted:
        return
    
    # buyers, sellers = constricted

    demand = defaultdict(int)
    pref = build_preference_set(buyers, sellers, prices, valuations)
    for b in buyers:
        for s in pref[b]:
            if s in sellers:
                demand[s] += 1

    if not demand:
        return
    
    max_demand = max(demand.values())
    if max_demand <= 1:
        return
    
    for s in sellers:
        if demand.get(s, 0) == max_demand:
            prices[s] += 1

def plot_graph(graph, A, B):
    pos = {}
    pos.update((node, (1, i)) for i, node in enumerate(A))
    pos.update((node, (2, i)) for i, node in enumerate(B))

    plt.figure(figsize=(10, 6))
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='black')
    edge_labels = nx.get_edge_attributes(graph, 'valuation')
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
        changed = update_prices(graph, constricted)
        if not changed:
            print("No price update. Exiting.")
            break
        round_number += 1
        if round_number == 50:
            break


def main():
    args = parser_arguments()
    graph = nx.read_gml(args.graph_file)
    graph = nx.relabel_nodes(graph, lambda x: int(x))
    A, B = get_bipartite_sets(graph)
    for a in A:
        graph.nodes[a]['price'] = graph.nodes[a].get('price', 0)

    if args.plot:
        plot_graph(graph, A, B)

    if args.interactive:
        market_clearing(graph, A, B)

if __name__ == "__main__":
    main()
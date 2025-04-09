import argparse
import networkx as nx
import matplotlib.pyplot as plt
import sys
from collections import defaultdict

def parser_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", help="Path to .gml file")
    parser.add_argument("--plot", action="store_true", help="Plot the graph")
    parser.add_argument("--interactive", action="store_true", help="Shows the output of every round graph")
    return parser.parse_args()

def check_graph(graph):
    if not nx.is_bipartite(graph):
        raise ValueError("Graph must be bipartite")
    
    for n in graph.nodes():
        if "bipartite" not in graph.nodes[n]:
            raise ValueError(f"Node {n} is not bipartite")
        if graph.nodes[n]['bipartite'] == 0:
            if 'price' not in graph.nodes[n]:
                raise ValueError(f"Seller {n} does not contain a price")
    
    for i, j in graph.edges():
        if 'valuation' not in graph.edges[i, j]:
            raise ValueError(f"Edge ({i}, {j}) does not contain a valuation")

def initialize_variables(graph):
    sellers = [node for node in graph.nodes if graph.nodes[node].get('bipartite') == 0]
    buyers = [node for node in graph.nodes if graph.nodes[node].get('bipartite') == 1]
    prices = {seller: graph.nodes[seller]['price'] for seller in sellers}

    valuations = defaultdict(dict)
    for b in buyers:
        for s in sellers:
            if graph.has_edge(b, s):
                valuations[b][s] = graph.edges[b, s]['valuation']
            elif graph.has_edge(s, b):
                valuations[b][s] = graph.edges[s, b]['valuation']
            else:
                valuations[b][s] = float('-inf')

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
        pref_set[b] = best_sellers
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
    if len(matching) == 2 * len(buyers):
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


def update_prices(sellers, buyers, prices, pref, constricted):
    if not constricted:
        return prices

    buyers, seller_set = constricted
    demand = defaultdict(int)
    #pref = build_preference_set(buyers, sellers, prices, valuations)
    for b in buyers:
        for s in pref[b]:
            if s in sellers:
                demand[s] += 1

    if not demand:
        return prices
    
    max_demand = max(demand.values())
    if max_demand <= 1:
        return prices
    
    for s in sellers:
        if demand.get(s, 0) == max_demand:
            prices[s] += 1

    return prices


def plot_graph(graph, sellers, buyers, prices, title, interactive):
    pos = {}
    colors = []
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111)

    # Sellers side
    sellerY = 1.0
    sellerStep = 1.0 / (len(sellers) + 1)
    for i, s in enumerate(sellers):
        pos[s] = (0, sellerY - (i + 1) * sellerStep)
        colors.append('lightblue')

    # Buyers side
    buyerY = 1.0
    buyerStep = 1.0 / (len(buyers) + 1)
    for i, s in enumerate(buyers):
        pos[s] = (1, buyerY - (i + 1) * buyerStep)
        colors.append('lightgreen')

    nx.draw_networkx_nodes(graph, pos, node_size=1000, node_color=colors, ax=ax)

    sellerLabels = {s: f"{s}\nprice:{prices[s]}" for s in sellers}
    buyerLabels = {b: b for b in buyers}
    nx.draw_networkx_labels(graph, pos, labels=sellerLabels, ax=ax)
    nx.draw_networkx_labels(graph, pos, labels=buyerLabels, ax=ax)

    edgeLabels = {(u, v): f"{graph.edges[u, v]['weight']:.1f}" for u, v in graph.edges()}
    nx.draw_networkx_edges(graph, pos, ax=ax)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edgeLabels, ax=ax)

    ax.set_title(title)
    plt.tight_layout()
    if interactive:
        plt.pause(0.5)
    else:
        plt.show(block=False)
    

def market_clearing(graph, plot=False, interactive=False):
    sellers, buyers, prices, valuations = initialize_variables(graph)
    round_number = 0
    while round_number < 50:
        round_number += 1
        print(f"\n--- Round {round_number} ---")
        print(f"Price: {prices}")

        pref = build_preference_set(sellers, buyers, prices, valuations)
        print("Preferred Sellers:")
        for b in buyers:
            print(f"{b}: {pref[b]}")

        G = pref_graph(sellers, buyers, prices, valuations, pref)
        
        if plot:
            plot_graph(G, sellers, buyers, prices, f"Round {round_number}", interactive)

        constricted = find_constricted_set(G, sellers, buyers)
        print(f"Constricted Set: {constricted}")

        if not constricted:
            matching = nx.bipartite.maximum_matching(G, top_nodes=buyers)
            print("Market cleared!")
            print(f"Prices: {prices}")
            print("Optimal Matching:")
            for b in buyers:
                s = matching[b]
                profit = valuations[b][s] - prices[s]
                print(f"{b} -> {s} (Price: {prices[s]}, Profit: {profit:.1f})")

            if plot:
                plot_graph(G, sellers, buyers, prices, "Market Clearing Equilibrium", interactive)
                plt.show()
            break
        prices = update_prices(sellers, buyers, prices, pref, constricted)
        print(f"New Prices: {prices}")

        if not interactive and plot:
            plt.close()

def main():
    args = parser_arguments()
    
    try:
        graph = nx.read_gml(args.graph_file)
        check_graph(graph)
        market_clearing(graph, plot=args.plot, interactive=args.interactive)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
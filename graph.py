import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Creates random graph and save it as a gml
def create_random_graph(n, c, gml):
    # Given equation for the probability of generation of nodes (clnn)/n where n is the number of nodes
    p = c * np.log(n)
    p = p / n
    graph = nx.erdos_renyi_graph(n, p)
    if graph:
        nx.write_gml(graph, gml)
    print(f"Graph with {n} nodes created and saved to {gml}.")

    
import numpy as np
import networkx as nx
import argparse
import matplotlib.pyplot as plt

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", type=str, help="reads graph file")
    parser.add_argument("--action", type=str, help="simulates cascade effect or spread of pandemic (like COVID)")
    parser.add_argument("--initiator", type=str, help="Chooses the initial node (BOTH)")
    parser.add_argument("--threshold", type=str, help="Set the threshold value (between 0 and 1) of the cascade effect (BOTH)")
    parser.add_argument("--probability_of_infection", type=str, help="Set the probability of p of the infections (COVID)")
    parser.add_argument("--probability_of_death", type=str, help="Set the probability of q of death while infected (COVID)")
    parser.add_argument("--lifespan", type=str, help="Define lifespan in rounds (COVID)")
    parser.add_argument("--shelter", type=str, help="Set the shelter parameter (COVID)")
    parser.add_argument("--vaccination", type=str, help="Set the vaccination rate (COVID)")
    parser.add_argument("--interactive", action="store_true", help="Plot graph and state of the nodes for every round (COVID)")
    parser.add_argument("--plot", help="Plot the number of new infections per day when the simulation is complete (BOTH)")
    return parser.parse_args()

def cascade(graph, initiators, threshold, interactive=False):
    initiators = [int(n) if n.isdigit() else n for n in initiators]
    active = set(initiators)
    newly_active = set(initiators)

    pos = nx.spring_layout(graph)
    round = 0

    while newly_active:
        if interactive:
            color_map = ["red" if node in active else "lightgray" for node in graph.nodes]
            plt.figure()
            nx.draw(graph, pos, with_labels=True, node_color=color_map)
            plt.title(f"Round {round}")
            plt.show()

        next_active = set()
        for node in graph.nodes:
            if node not in active:
                predecessors = list(graph.predecessors(node))
                if not predecessors:
                    continue
                num_active = sum(1 for pred in predecessors if pred in active)
                fraction = num_active / len(predecessors)
                if fraction >= threshold:
                    next_active.add(node)
        if not next_active:
            break

        active.update(newly_active)
        newly_active = next_active
        round += 1
        print(f"Round {round}: newly activated nodes = {newly_active}")

    print(f"Final active set: {active}")
    print(f"Total rounds: {round}")

    if interactive:
        color_map = ["red" if node in active else "lightgray" for node in graph.nodes]
        plt.figure()
        nx.draw(graph, pos, with_labels=True, node_color=color_map)
        plt.title(f"Final Activated Nodes")
        plt.show()

    return active


def covid(graph, inf, death, life, shelter, vacc, plot, interactive):
    pass

def main():
    args = argument_parser()

    try:
        graph = nx.read_gml(args.graph_file)
    except FileNotFoundError:
        print("Graph file not found")
        return
    
    initiator = list(map(str.strip, args.initiator.split(',')))

    if args.action:
        if "cascade" in args.action:
            threshold = float(args.threshold)
            result = cascade(graph, initiator, threshold, interactve=args.interactive)
            if args.plot:
                color_map = ["red" if node in result else "lightgray" for node in graph.nodes]
                nx.draw(graph, with_labels=True, node_color=color_map)
                plt.title("Final Cascade Result")
                plt.show()
            
        elif "covid" in args.action:
            infection = float(args.probability_of_infection)
            death = float(args.probability_of_death) if args.probability_of_death else 0.00
            life = float(args.lifetime)
            shelter = float(args.shelter)
            vaccination = float(args.vaccination)

            covid(graph, infection, death, life, shelter, vaccination, args.plot, args.interactive)

        else:
            raise ValueError("Must choose between cascade/covid for your action")
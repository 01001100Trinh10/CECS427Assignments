import networkx as nx
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random
from collections import defaultdict

# Used to parse arguments based on what the user wants
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
    parser.add_argument("--plot", action="store_true", help="Plot the number of new infections per day when the simulation is complete (BOTH)")
    return parser.parse_args()

# Simulates the cascading affect and how users can get affected based on the neighbors around them over time
def cascade(graph, initiators, threshold, plot, interactive):
    # Initializes the starting nodes and considers them newly active
    active = set(initiators)
    newly_active = set(initiators)
    # Keeps track of the numbers to graph over time
    active_count = []
    total_count = []

    # Sets initial graph and round
    pos = nx.spring_layout(graph)
    round = 0

    # This model will repeat until there are no more newly-activated nodes
    while newly_active:
        # If interactive, show the current state of the graph at this specific round
        if interactive:
            color_map = ["red" if node in active else "lightgray" for node in graph.nodes]
            plt.figure()
            nx.draw(graph, pos, with_labels=True, node_color=color_map)
            plt.title(f"Round {round}")
            plt.show()

        # Set up current active nodes to simulate spread
        active.update(newly_active)
        next_active = set()
        # Iterate through all nodes
        for node in graph.nodes:
            if node not in active:
                # Fetches all neighbors of an inactive node
                neighbors = list(graph.neighbors(node))
                if not neighbors:
                    continue
                num_active = 0
                for n in neighbors:
                    if n in active:
                        num_active += 1
                # Sets fraction of active neighbors over total neighbors
                fraction = num_active / len(neighbors)
                # If above the threshold, the node is now in set_active
                if fraction >= threshold:
                    next_active.add(node)
        # Adds all newly active nodes and total
        active_count.append(len(newly_active))
        newly_active = next_active
        total_count.append(len(active))
        round += 1
        print(f"Round {round}: newly activated nodes = {newly_active}")

    # Displays final set
    print(f"Final active set: {active}")
    print(f"Total rounds: {round}")

    # Shows final graph of the cascade graph
    if interactive:
        color_map = ["red" if node in active else "lightgray" for node in graph.nodes]
        plt.figure()
        nx.draw(graph, pos, with_labels=True, node_color=color_map)
        plt.title(f"Final Activated Nodes")
        plt.show()

    # If plot, plots 2 lines for active cascading effect and total active nodes over time
    if plot:
        rounds = list(range(len(active_count)))
        plt.figure()
        plt.plot(rounds, active_count, label="Newly Active", marker='o')
        plt.plot(rounds, total_count, label="Total Active", marker='x')
        plt.xlabel("Rounds")
        plt.ylabel("Number of Active Nodes")
        plt.title("Cascade Activation Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

# Simulates infection from COVID in a graph
def covid(graph, initiators, inf, death, life, shelter, vacc, plot, interactive):
    # sets all nodes in a list
    nodes = list(graph.nodes)
    num_nodes = len(nodes)

    # Identifies initiators in a set
    initiator_set = set(initiators)

    # Randomly samples nodes for vaccinations, we're trying to avoid the initiator nodes so we can properly showcase infection
    eligible_vaccinations = list(set(nodes) - initiator_set)
    num_vaccinated = int(vacc * num_nodes)
    vaccinated = set(random.sample(eligible_vaccinations, min(num_vaccinated, len(eligible_vaccinations))))
    
    # Randomly samples nodes for sheltering, we're also trying to avoid initiator nodes for the same reason. We're also not including vaccinations
    eligible_sheltered = list(set(nodes) - initiator_set - vaccinated)
    num_sheltered = int(shelter * num_nodes)
    sheltered = set(random.sample(eligible_sheltered, min(num_sheltered, len(eligible_sheltered))))

    # Sets all nodes to s by default
    state = {node: "s" for node in nodes}
    time_infected = defaultdict(int)
    time_recovered = defaultdict(int)

    # In this simulation, we don't consider vaccinated as immune, just have an extra layer of protection against COVID
    for v in vaccinated:
        state[v] = "r"
        time_recovered[v] = 1

    # Setting all initiators as infected
    for i in initiators:
        state[i] = "i"
        time_infected[i] = 1

    # Setting all sheltered as u for "unchangeable"
    for sh in sheltered:
        state[sh] = "u"

    # Array to keep track of infection over time
    infection_counts = []

    pos = nx.spring_layout(graph)

    # Simulates a lifespan for this simulation
    for t in range(life):
        # If interactive, display a graph showing all the nodes and their respective assignment
        if interactive:
            color_map = []
            # Sets colors to all the nodes and their respective states
            for node in nodes:
                if state[node] == "s":
                    color_map.append("yellow")
                elif state[node] == "i":
                    color_map.append("red")
                elif state[node] == "r":
                    color_map.append("green")
                elif state[node] == "d":
                    color_map.append("lightgray")
                elif state[node] =="u":
                    color_map.append("lightblue")
            plt.figure()
            nx.draw(graph, pos, node_color=color_map, with_labels=True)
            plt.title(f"Day {t}")
            # Legend to label and identify which colors mean what
            legend_labels = [
                mpatches.Patch(color='yellow', label='Susceptible'),
                mpatches.Patch(color='red', label='Infected'),
                mpatches.Patch(color='green', label='Recovered'),
                mpatches.Patch(color='lightgray', label='Dead'),
                mpatches.Patch(color='lightblue', label='Sheltered')
            ]
            plt.legend(handles=legend_labels, loc="best")
            plt.show()

        # Arrays to keep track of the states of the node changes
        new_infections = []
        to_recover = []
        to_die = []
        newly_sus = []

        for node in nodes:
            # Identifies infected node and identifies its' neighbors
            if state[node] == "i":
                for neighbor in graph.neighbors(node):
                    if state[neighbor] == "s" and neighbor not in sheltered:
                        # Randomly sets the susceptible neighbors as infected if the random number is under the infection rate
                        if random.random() < inf:
                            new_infections.append(neighbor)

                # Randomly sets the infected node to death state if the random number is under the death rate
                if random.random() < death:
                    to_die.append(node)
                # If not, we add time to the dictionary of the infected nodes. We hardcoded infected nodes to recover after 5 days of infection
                else:
                    time_infected[node] += 1
                    if time_infected[node] >= 5:
                        to_recover.append(node)
            # After 1 day in recovery state, we set those nodes back to susceptible for the SIRS model (susceptible -> infected -> recovered -> susceptible)
            if state[node] == "r":
                time_recovered[node] += 1
                if time_recovered[node] >= 2:
                    newly_sus.append(node)

        # Set newly infected nodes
        for node in new_infections:
            state[node] = "i"
            time_infected[node] = 1
        # Set newly recovered nodes
        for node in to_recover:
            state[node] = "r"
            time_infected.pop(node, None)
        # Set newly dead nodes
        for node in to_die:
            state[node] = "d"
            time_infected.pop(node, None)
        # Set newly susceptible nodes
        for node in newly_sus:
            state[node] = "s"
            

        # Adds number of new infections
        infection_counts.append(len(new_infections))
    # If plot, we display the number of newly infected nodes over time
    if plot:
            days = list(range(len(infection_counts)))
            plt.figure()
            plt.plot(days, infection_counts, marker='o')
            plt.xlabel("Day")
            plt.ylabel("New Infections")
            plt.title("COVID Spread Simulation")
            plt.grid(True)
            plt.show()

def main():
    # Calls arguments
    args = argument_parser()

    # Reads gml file, gives error if graph is invalid or if there is no graph
    try:
        graph = nx.read_gml(args.graph_file)
        graph = graph.to_undirected()
        # After reading the file, we read the action. Shoot error if there's no action or invalid actions
        if args.action:
            # If user chooses cascade
            if "cascade" in args.action:
                # Strips the commas of all the initiators
                initiator = list(map(str.strip, args.initiator.split(',')))
                # Reads threshold as float
                threshold = float(args.threshold) if args.threshold else 0.00
                # Runs cascade model
                cascade(graph, initiator, threshold, args.plot ,args.interactive)
            
            # If user chooses covid
            elif "covid" in args.action:
                # Strips all commas from the initiators
                initiator = list(map(str.strip, args.initiator.split(',')))
                # Reads infection rate as float, 0.0 by default
                infection = float(args.probability_of_infection) if args.probability_of_infection else 0.00
                # Reads death rate as float, 0.0 by default
                death = float(args.probability_of_death) if args.probability_of_death else 0.00
                # Reads lifespan as int
                life = int(args.lifespan) if args.lifespan else 365
                # Reads shelter as float value, 0.0 by default
                shelter = float(args.shelter) if args.shelter else 0.00
                # Reads vaccination as float value, 0.0 by default
                vaccination = float(args.vaccination) if args.vaccination else 0.00
                # Runs covid simulation
                covid(graph, initiator, infection, death, life, shelter, vaccination, args.plot, args.interactive)
            else:
                raise ValueError("Must choose between cascade/covid for your action")
        else:
            raise ValueError("Must choose between cascade/covid for your action")
    except FileNotFoundError:
        print("Graph file not found")
        return
    
    
if __name__ == "__main__":
    main()
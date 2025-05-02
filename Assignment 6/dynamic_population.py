import numpy as np
import networkx as nx
import argparse
import matplotlib.pyplot as plt

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, help="simulates cascade effect or spread of pandemic (like COVID)")
    parser.add_argument("--initiator", type=str, help="Chooses the initial node (BOTH)")
    parser.add_argument("--threshold", type=str, help="Set the threshold value (between 0 and 1) of the cascade effect (BOTH)")
    parser.add_argument("--probability_of_infection", type=str, help="Set the probability of p of the infections (COVID)")
    parser.add_argument("--probability_of_death", type=str, help="Set the probability of q of death while infected (COVID)")
    parser.add_argument("--lifespan", type=str, help="Define lifespan in rounds (COVID)")
    parser.add_argument("--shelter", type=str, help="Set the shelter parameter (COVID)")
    parser.add_argument("--vaccination", type=str, help="Set the vaccination rate (COVID)")
    parser.add_argument("--interactive", help="Plot graph and state of the nodes for every round (COVID)")
    parser.add_argument("--plot", help="Plot the number of new infections per day when the simulation is complete (BOTH)")
    return parser.parse_args()

def cascade():
    pass

def covid():
    pass

def main():
    pass
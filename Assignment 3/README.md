**INSTRUCTIONS TO USE TRAFFIC_ANALYSIS.PY**

**Requirements before running the code:**

    - Python (I used version 3.11.7 for this lab)
    - numpy to compute the probability
    - networkx to perform BFS traversal
    - matplotlib.pyplot to visualize and display the graph
    - argparse for flexibility of arguments

**Explanation of Parameters:**

Quick Explanation on what parameters there are and how they work!

    graph_file:
    - Takes one input
    - Must be a .gml file in the same file as the program
    - This is required in order to run any visualization or analysis

    n:
    - This command represents the number of vehicles the map will contain and route
    - Must be a positive integer

    initial:
    - Must be an integer that matches one of the nodes in the graph
    - This represents the starting point you want to route the vehicles in

    final:
    - Must be an integer that matches one of the nodes in the graph
    - This represents the end point you want to route the vehicles in

    --plot
    - Takes no inputs
    - Plots 2 graphs, one graph shows the travel equilibrium and the other shows social optimality in a directed network

**Actually running the code:**

We will be running the code through the command prompt on Windows. In order to run the code, you must first be in the correct branch where the graph.py file is located. To do this, type the following line: "cd [INSERT PATH TO traffic_analysis.py HERE]"

Afterwards, we need a graph to be able to perform an analysis. This program does not create a graph so you're going to need a graph with written values for a and b. to run the code, you'll need to consider 3 things:
    - How many vehicles you want to introduce
    - Where you want to start on the graph
    - Where you want to end on the graph

To run it on the terminal, assuming you have the graph file called traffic.gml in the same file directory, let's say you want to introduce 4 vehicles from node 0 to node 3. To do this, type the following command:

python3 traffic_analysis.py traffic.gml 4 0 3 --plot

Here, you will get 2 different graphs. One will represent the mapping for the nash equilibrium and the second graph will be the social optima. Depending how many edges are in the graph, the plot may be a bit cluttered, but if you expand the window it will look a lot better. You can also see a breakdown in the terminal which shows you the edges the vehicles take, the travel time, and the potential power. At the end of each graph, there will be a total calculation for the social cost and the potential power
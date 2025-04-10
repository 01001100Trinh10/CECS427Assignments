**INSTRUCTIONS TO USE MARKET_STRATEGY.PY**

**Requirements before running the code:**

    - Python (I used version 3.11.7 for this lab)
    - networkx to create DiGraphs
    - matplotlib.pyplot to visualize and display the graph
    - defaultdict from collections to perform certain tasks
    - argparse for flexibility of arguments
    - sys for system functions

**Explanation of Parameters:**

Quick Explanation on what parameters there are and how they work!

    graph_file:
    - Takes one input
    - Must be a .gml file in the same file as the program
    - This is required in order to run any visualization or analysis

    --plot
    - Takes no inputs
    - Plots a graph that shows the sellers/buyers, prices, and 

    --interactive
    - takes no inputs
    - Plots a graph for each round of the market clearing algorithm


**Actually running the code:**

We will be running the code through the command prompt on Windows. In order to run the code, you must first be in the correct branch where the graph.py file is located. To do this, type the following line: "cd [INSERT PATH TO traffic_analysis.py HERE]"

Afterwards, we need a graph to be able to perform an analysis. This program requires a bipartite graph that contains prices and valuations. Otherwise, an excetion will be thrown.

To run it on the terminal, assuming you have the graph file called market.gml in the same file directory

python ./market_strategy.py market.gml --plot --interactive

Here, you will get multiple graphs at once. Each graph will represent a round of the market clearing algorithm until you eventually reach a cleared market. During each iteration, you will get a console response that shows the round number, the current prices of each seller, the preferred sellers, the constricted set. When the market is cleared, there will be one more graph that will show the cleared market. You will also get a console response that shows the current prices of each seller, the optimal matches from buyer to seller, and the proft each buyer/seller makes.
**INSTRUCTIONS TO USE GRAPH_ANALYSIS.PY**

**Requirements before running the code:**

    - Python (I used version 3.11.7 for this lab)
    - numpy to compute the probability
    - networkx to perform BFS traversal
    - matplotlib.pyplot to visualize and display the graph
    - argparse for flexibility of arguments
    - scipy in order to run the tstudent test for homophily

**Explanation of Parameters:**

Quick Explanation on what parameters there are and how they work!

    graph_file:
    - Takes one input
    - Must be a .gml file in the same file as the program
    - This is required in order to run any visualization or analysis

    --components:
    - Takes one input n
        - Must be an integer
    - Specifices how many components the graph should be partitioned into (subgraphs/clusters)

    --plot
    - Takes one input
        - MUST BE ONE OF 3 OPTIONS: 'C', 'N', OR 'P'
    - Determins how the graph should be plotted
    - C:
        - Clusters the graph where the lowest degree will be blue and the highest degree being closer to magenta
    - N:
        - Highlights neighborhood overlap measuring how much overlap there are between adjacent nodes. Similar to option C
        - This graph is interactive, upon clicking one of the nodes, another window will pop up showing a BFS tree where the clicked node will be the root.
    - P:
        - Colors the node based on the attribute if it was assigned.
        - Set to a default color if not.

    --verify_homophily
        - Tests for homophily in the graph based on the assigned node colors using the Student t-test.
        - Essentially measures whether nodes with the same color are more likely to connect.

    --verify_balanced_graph:
        - Checks if the graph is balanced based on the assigned edge signs. The graph is considered balance if the number of signs are consistent with the node attributes.

    --output
    - Takes in one argument:
            - takes in a file name that MUST BE IN .gml FORMAT!
    - Stores the graph you created in the same folder that graph_analysis.py is in

**Actually running the code:**

We will be running the code through the command prompt on Windows. In order to run the code, you must first be in the correct branch where the graph.py file is located. To do this, type the following line: "cd [INSERT PATH TO graph.py HERE]"

Afterwards, we need a graph to be able to perform an analysis. Before we start, we must first have a .gml file. It can either be imported or created, but it must be in the same folder as the graph_analysis.py file.

Firstly, I tested the cluster command by running the following command with karate.gml:

python ./graph_analysis.py karate.gml --components 2 --plot C

This should give you a graph that was split into 2 clusters. It should also return which edges were removed in order to get those two subgraphs.

The next test is with the same karate.gml file which will show the overlap within the graph:

python ./graph_analysis.py karate.gml --plot N

This should give you a graph with edges of varying thickness. This thickness is important as it highlights the overlap between the nodes. If you click on one of the nodes on the graph, it will display a different graph in BFS hierarchal format where the root is the node you clicked on. To return to the original graph, you can simply click on the graph again to return and explore a different node.

The next test will test the homophily of the graph. In the example I used a graph that shows evidence of a homophily:

python ./graph_analysis.py homophily.gml --plot P --verify_homophily

This will first display the graph but after you close it, the command line will return the homophily ratio and p-value. Afterwards it will classify on whether or not the graph shows evidence of a homophily.

Next we will showcase the balanced graph function with a balanced graph gml file like so:

python ./graph_analysis.py balanced_graph.gml --plot P --verify_balanced_graph

This will display a graph with different types of edges. Black represent negative and red represents positive edges. After you close the graph, the command line will return the result on whether or not the graph is balanced.
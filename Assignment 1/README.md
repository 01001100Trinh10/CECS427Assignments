**INSTRUCTIONS TO USE GRAPH.PY**

**Requirements before running the code:**
    - Python (I used version 3.11.7 for this lab)
    - numpy to compute the probability
    - networkx to perform BFS traversal
    - matplotlib.pyplot to visualize and display the graph
    - argparse for flexibility of arguments

**Explanation of Parameters:**
    --input:
        - Takes in a graph file
        - Has to be in .gml format to be properly read
        - The graph file MUST be in the same folder as the graph.py file!
        - This parameter is required to provide the initial graph data for analysis/visualization

    --create_random_graph:
        - Takes in two arguments:
            --nodes:
                - How many nodes you wish to be included when creating your graph
                - required parameter in order to create a graph
            --constant:
                - Constant that influences the generation of the graph
                - required parameter in order to create a graph
    
    --BFS:
        - Takes in one argument being the starting node
        - requires the starting node in order to perform BFS traversal
    
    --plot:
        - Simple request that visualizes the graph
        - It doesn't have any arguments
        - However, if you want to display the graph as a BFS hierarchy make sure to include --BFS in your argument!
        - If you want to see your initally generated graph, leave out the --BFS argument!
    
    --output:
        - Takes in one argument:
            - takes in a file name that MUST BE IN .gml FORMAT!
        - Stores the graph you created in the same folder that graph.py is in

**Actually running the code:**
    We will be running the code through the command prompt on Windows. In order to run the code, you must first be in the correct branch where the graph.py file is located. To do this, type the following line: "cd [INSERT PATH TO graph.py HERE]"

    Now that you're in the correct directory, you are now able to run the code! If you do not have a graph, you must first create one! To do so simply type the following line:

    python ./graph.py --create_random_graph 20 1.1 --output out_graph_file.gml

    Here, you created a random graph with 20 nodes and constant 1.1 and stored it in the file out_graph_file.gml. You can change up the number of nodes or the constant factor, but I found these parameters to be the best to show the graph. any number greater than 20 may create a cluttered-looking graph so be careful!

    After creating the graph, you can type the following command(If you already have a graph file, you can replace the "out_graph_file.gml" with the graph file you wish to visualize):

    python ./graph.py --input out_graph_file.gml --BFS 1 --plot

    Here, you call BFS which will display all the paths from the starting node (in this case, it's 1) as well as the length of these paths. Afterwards, a BFS graph will be displayed on a separate window popup. You will notice that there are different colored edges and nodes. The gray edges represent edges that exist in the network but are not necessarily part of the BFS network because it is not the shortest path from the starting node. The red edges represent the shortest path from the current node to the starting node. There will only be one green node which will represent the starting node while all the rest of the nodes will be blue.

    Like the previous command, you can change around the starting node. As long as the number is an existing node it will work. However, there may be nodes that are not reachable from the BFS tree, these nodes will be separated from the rest of the nodes.
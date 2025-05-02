**INSTRUCTIONS TO USE PAGE_RANK.PY**

**Requirements before running the code:**

    - Python (I used version 3.11.7 for this lab)
    - networkx to create DiGraphs
    - matplotlib.pyplot to visualize and display the graph
    - scrapy to perform the webcrawler
    - urllib to parse urls
    - os to help read files
    - argparse for flexibility of arguments
    - sys for system functions

**Explanation of Parameters:**

Quick Explanation on what parameters there are and how they work!

    --crawler
        - Requires a txt file in a specific format:
            - max_nodes value (any int > 0)
            - domain that the webcrawler will reference
            - the seed url where the crawler will traverse through
        - Will send a webcrawler through the given url in the .txt file
    --input
        - Takes in a graph (.gml) file
        - displays the graph in forms of nodes, edges, and the url the node represents
    --loglogplot
        - Generates a degree distribution of the graph via matplotlib
    --crawler_graph
        - Generates a crawler graph based on the information fromt he --crawler
        - Stores it in out_graph.gml
    --pagerank_values
        - Uses the pagerank algorithms on all the urls to represent the most interconnected url
        - ranks the urls and pastes them all in node_rank.txt

**Actually running the code:**

In order to run the program, you must first have a proper txt file with the correct information. This first includes an integer greater than 0. This decides how many urls the algorithm will rank and find the interconnections with.

After that, you can run the following code to generate the crawler graph:

python ./page_rank.py --crawler crawler.txt --crawler_graph out_graph.gml

This will generate a graph via out_graph.gml

If you want to display the graph, you would run the following line assuming you have out_graph.gml in the same folder

python ./page_rank.py --crawler crawler.txt --input graph.gml

To visualize the loglog plot, you would run the following plot

python ./page_rank.py --crawler crawler.txt --loglogplot

This will give you a degree distribution graph based on the max nodes given in the txt file.

lastly, if you want to view the pagerank, you would run the following line

python ./page_rank.py --crawler crawler.txt --pagerank_values node_rank.txt

This will store the hierarchy in the txt files with their rank values as well as the rank of each node descending
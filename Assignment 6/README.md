**INSTRUCTIONS TO USE DYNAMIC_POPULATION.PY**

**Requirements before running the code:**

    - Python (I used version 3.11.7 for this lab)
    - networkx to create DiGraphs
    - matplotlib.pyplot to visualize and display the graph
    - matplotlib.patches mpatches so we can include a legend for the covid simulation
    - argparse for flexibility of arguments
    - collections defaultdict to include dictionaries for graphing

**Explanation of Parameters:**

Quick Explanation on what parameters there are and how they work!

    --action
        - Chooses the model you want to run your gml file in.
        - Must have a pre-made gml file (will return an error if you don't have one)
        - You must choose between a cascade model or a covid model
        - cascade:
            - must be all lower-cased
            - Runs the cascade model of the graph and display the active nodes per round
        - covid:
            - must be all lower-cased
            - Runs the covid model of the graph and how nodes can infect their neighbors over time
    --initiator
        - Must be node values in your graph file
        - Chooses the starting point of your model
            - For cascade, it's the first active node(s)
            - For covid, it's the first infected node(s)
        - To set multiple initiators, you must separate them with commas
    --threshold
        - Takes one parameter q
        - USED FOR THE CASCADE MODEL
        - Sets the threshold value (between 0 and 1) of the cascade effect
        - Set to 0.0 by default
    -- probability_of_infection
        - Takes one parameter p
        - USED FOR THE COVID MODEL
        - Sets the probability on whether a neighboring node of an infected nodes gets infected.
        - Set to 0.0 by default
    --probability_of_death
        - Takes one parameter q
        - USED FOR THE COVID MODEL
        - Sets the probability on whether an infected node dies after a round
        - Set to 0.0 by default
    --lifespan
        - Takes one parameter l
        - USED FOR THE COVID MODEL
        - Sets the number of days you want to have the simulation in
        - Set to 365 (one year) by default
    --shelter
        - Takes one parameter s
        - USED FOR THE COVID MODEL
        - Sets the percentage of nodes you want sheltered
        - This is a unique state where sheltered nodes cannot get infected
        - SET to 0.0 by default
    --vaccination
        - Takes one parameter r
        - USED FOR THE COVID MODEL
        - Sets the percentage of nodes you want vaccinated
        - Vaccinated nodes are hardcoded to be in the recovery state (cannot be infected)
        - Vaccinated users can become susceptible after some time to simulate evolving diseases such as COVID and their variants
        - Set to 0.0 by default
    --interactive
        - CAN BE USED FOR BOTH MODELS
        - Used to simulate change over time in a graph
        - Creates new graphs after every iteration and also finished graph after all conditionals are met
            - Cascade model: stops once there are no more newly-activated nodes
            - COVID model: Stops once the end of the lifespan paramter is met
    --plot
        - CAN BE USED FOR BOTH MODELS
        - Used to graph lines that shows the infection rate over time depending on the model.
            

**Actually running the code:**

In order to run the program, you must first have a premade gml file to run either action. This program does not create any graphs and you will run into errors if you pass an invalid file. You would also need to pass valid initiator values (id in your gml file) in order for the models to actually work.

To run the cascade model, let's say we try to pass the gml file cascadebehaviour.gml file to the program. We also want to set the initiators for the effect to actually occur. Let's say we set nodes 1, 2, and 5 as the initiators. Afterwards, we want to set the threshold value to 0.33 to allow some resistance of activation of neighboring nodes. Afterwards, we want to make sure this process is visualized with graphs and lines with interactive in plot. With that we would run the following command:

python ./dynamic_population.py cascadebehaviour.gml --action cascade --initiator 1,2,5 --threshold 0.33 --interactive --plot

Here, you will get multiple graphs that shows the step-by-step process of nodes getting active over time and a graph that displays this process and activation over time.

Next, let's try and use the covid model on the same gml file. Here, we want to set the initiators to nodes 3 and 4. For the infection rate, we will try 20% and death rate to 5 percent and have this process go through 100 days. We'll set the shelter value to 30 percent of the population and 24 percent of the population will be vaccinated. We will also want this process interactive and plotted over time. With that, we would want to run the following command.

python ./dynamic_population.py cascadebehaviour.gml --action covid --initiator 3,4 --probability_of_infection 0.2 --probability_of_death 0.05 --lifespan 100 --shelter 0.30 --vaccination 0.24 --interactive --plot

With this, the program will return multiple graphs to simulate the spread of a disease overtime. Since the infection/death rate are random, you can adjust the rates high/lower to simulate various simulations
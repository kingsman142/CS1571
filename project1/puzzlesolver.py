import sys
import os
import math

def execute_search(filename, keyword):
    # Output:
    # The solution path (or "No solution" if nothing was found): print one state per line.
    # Time: expressed in terms of the total number of nodes created.
    # Space: expressed as the maximum number of nodes kept in memory (the biggest size
    #    that the frontier list grew to) as well as the maximum number of states stored on the
    #    explored list. Please report these as two separate numbers.
    # Cost: the final cost of the specified path or configuration.
    with open(filename, "r") as config_file:
        input = config_file.readlines()
        input[0] = input[0].rstrip()
    for i in xrange(1, len(input)):
        if len(input[i]) > 2:
            input[i] = eval(input[i].rstrip())
        else:
            input.remove(input[i])
    #print(input)
    #print("input len: " + str(len(input)))
    if input[0] == "monitor":
        if not len(input) == 3:
            print("Invalid input file; it should only have two lines of input!")
            return
        monitor(input, keyword)
    elif input[0] == "aggregation":
        aggregation(input, keyword)

def unicost(init_state, actions, goal_state, transition, unique_value, optimal_cost, get_optimal_goal_state):
    frontier = []
    explored = set([])
    frontier.append(init_state)
    goal_states = []
    time = 1 # We already created 1 node, the initial state
    frontier_space = 1 # Maximum amount of space the frontier grew to
    visited = 0 # Number of nodes we have visited

    while frontier:
        # Find the lowest cost here
        curr_state = optimal_cost(frontier) # Loop through all states and find lowest cost
        state_unique_identifier = unique_value(curr_state)
        if goal_state(curr_state): # Check if we've reached the goal state or not
            goal_states.append(curr_state)
            the_state, max_cost = get_optimal_goal_state(goal_states)
            return (the_state, time, (frontier_space, visited), max_cost)
        elif not state_unique_identifier or not frozenset(state_unique_identifier) in explored: # Check if we've explored this state before or not
            explored.add(frozenset(state_unique_identifier)) # Add this state to the explored set so we never travel it again
            visited += 1
            for action in actions: # Execute each action
                new_state = transition(action, curr_state) # Generate the outcome states for this action
                for state in new_state:
                    time += 1
                    frontier.append(state) # Add each new state to the frontier for us to explore later
                frontier_space = max(len(frontier), frontier_space) # Generate the new maximum frontier size
    #state, max_cost = get_optimal_goal_state(goal_states)
    #return (state, time, (frontier_space, visited), max_cost) # end state, time, space, cost

def iddfs(init_state, actions, goal_state, transition, unique_value, get_optimal_goal_state):
    goal_states = []
    nodes_created = 0
    max_frontier_size = 0
    max_explored_size = 0
    for i in xrange(0, 100): # From 0 depth to 100 depth (chosen arbitrarily), perform DFS
        info = dfs(init_state, actions, goal_state, set([]), transition, unique_value, 0, i, 1, 0, 0) # initial state,
        if info:
            nodes_created = max(info[1], nodes_created)
            max_frontier_size = max(max_frontier_size, info[2])
            max_explored_size = max(max_explored_size, info[3])
            if info[0]: # We found the first goal state, so append it to the goal states list and return its information
                goal_states.append(info[0][0])
                break
            #for state in info[0]: # for state in goal states
                #goal_states.append(state)
    state, max_cost = get_optimal_goal_state(goal_states)
    return (state, nodes_created, (max_frontier_size, len(max_explored_size)), max_cost) # end state, time, space, cost

def dfs(state, actions, goal_state, explored, transition, unique_value, depth, max_depth, nodes_created, frontier_size, max_frontier_size):
    state_unique_identifier = unique_value(state) # Find the unique identifier for this state so we can add it to the explored set
    if goal_state(state): # We have reached the goal!
        return ([state], 1, max_frontier_size, explored) # return the goal state, nodes created up to this point, max frontier size up to this point, and the explored states
    elif not state_unique_identifier or not frozenset(state_unique_identifier) in explored: # We haven't visited this state yet
        explored.add(frozenset(state_unique_identifier)) # Add the state to the explored set
        if depth < max_depth: # We can only go up to a certain depth, so if we're already there, don't go any further
            goal_states = []
            for action in actions: # Execute each action
                new_state = transition(action, state)
                for state in new_state: # For each new state that is returned, perform DFS
                    frontier_size -= 1 # We have visited a new state, so decrease the frontier size
                    return_value = dfs(state, actions, goal_state, explored, transition, unique_value, depth+1, max_depth, 0, frontier_size+len(new_state), max(max_frontier_size, frontier_size+len(new_state)))
                    #print("ok: " + return_value[1])
                    if not return_value is None: # We have achieved some kind of goal state, so we can work with some new information
                        max_frontier_size = max(max_frontier_size, return_value[2]) # If we increased the frontier size, update it accordingly
                        nodes_created += return_value[1] # Sum up the number of nodes in each sumtree / path we travel
                        for return_state in return_value[0]: # Basically pass the goal states up the DFS chain to the root node so we can return every single goal state in the end
                            goal_states.append(return_state) # Transfer the goal states to the new set
                        if len(goal_states) > 0:
                            return (goal_states, nodes_created + 1, max_frontier_size, explored)
            nodes_created += 1 # Finally, add this node to the number of nodes created so we can recursively pass it up
            return (goal_states, nodes_created, max_frontier_size, explored)
    return None

def bfs(init_state, actions, goal_state, transition, unique_value, get_optimal_goal_state):
    frontier = []
    explored = set([])
    frontier.append(init_state)
    goal_states = []
    time = 1 # We already created 1 node, the initial state
    frontier_space = 1 # Maximum amount of space the frontier grew to
    visited = 0 # Number of nodes we have visited
    #print("bfs frontier size: " + str(len(frontier)))

    while frontier:
        curr_state = frontier.pop(0) # Pop from the left of the list
        state_unique_identifier = unique_value(curr_state)
        if goal_state(curr_state):
            goal_states.append(curr_state)
            break
        elif not state_unique_identifier or not frozenset(state_unique_identifier) in explored: # If we haven't explored this state yet
            if state_unique_identifier:
                explored.add(frozenset(state_unique_identifier))
            visited += 1
            for action in actions:
                new_state = transition(action, curr_state)
                for state in new_state:
                    time += 1
                    frontier.append(state)
                frontier_space = max(len(frontier), frontier_space)

    goal_state, max_cost = get_optimal_goal_state(goal_states)
    return (goal_state, time, (frontier_space, visited), max_cost) # return solution path, time, space, and cost

def monitor_find_optimal_goal_state(goal_states):
    max_cost = -sys.maxint
    goal_state = ()
    for state in goal_states:
        if state[3] > max_cost:
            max_cost = state[3]
            goal_state = state
    return (goal_state, max_cost)

def find_next_optimal_cost_monitor(frontier):
    max_cost = 0
    curr_state = ()
    for state in frontier:
        if state[3] > max_cost:
            max_cost = state[3]
            curr_state = state
    frontier.remove(curr_state)
    return curr_state

def find_next_target_sensor(action, state):
    sensors = state[0]
    targets = state[1]
    output = state[2]
    do_not_modify_targets = state[4]

    new_states = []

    if sensors and not targets: # There are more sensors than targets, so just explore the search space and attach every sensor to every target to
                                # find the most optimal cost value.
        for sensor in sensors:
            for target in do_not_modify_targets: # This is why we needed this immutable list, so we can scan over it later and find every target easier.
                # Make a copy of the sensors and output in the current state, then remove the current sensor because we're adding it to the output pairs list.
                sensor_copy = list(sensors)
                output_copy = set(output)
                sensor_copy.remove(sensor)

                # Grab the x and y coordinates of the sensor and target, then calculate their distance and find the sensor's power.
                # Finally, calculate the cost, which is the number of time units the sensor is watching the target in this case.
                s_x, s_y = sensor[1], sensor[2]
                t_x, t_y = target[1], target[2]
                distance = euclidian_distance(s_x, s_y, t_x, t_y)
                sensor_power = sensor[3]
                cost = sensor_power / distance

                # This is a new pair in our output for the solution.
                new_pair = (sensor, target, cost)
                output_copy.add(new_pair)

                # Now that we added another sensor to a target, we have to calculate the local cost for each target, then the lowest cost for
                # the entire sensor and target dataset.
                new_target_cost = sys.maxint
                target_cost_dict = {}
                for pair in output_copy: # Calculate the highest cost for each target so we find the maximum time it is being watched
                    if pair[1] in target_cost_dict: # The target is currently in the dictionary, so take the maximum value of this current target and the value in the dictionary currently.
                        target_cost_dict[pair[1]] = max(target_cost_dict[pair[1]], pair[2])
                    else:
                        target_cost_dict[pair[1]] = pair[2] # We have encountered this target for the first time in the output list so assign this value to its current cost.
                for key, val in target_cost_dict.iteritems(): # Scan over every target in the dictionary and find the minimum cost across all targets.
                    if val < new_target_cost:
                        new_target_cost = val

                # Straightforward; we are just generating a new permutation of sensors assigned to targets with their updated cost
                new_state = (sensor_copy, targets, output_copy, new_target_cost, do_not_modify_targets)
                new_states.append(new_state)
    else:
        for sensor in sensors:
            for target in targets:
                # Make a copy of the sensors and output in the current state, then remove the current sensor and target because we're adding them to the output pairs list.
                sensor_copy = list(sensors)
                target_copy = list(targets)
                output_copy = set(output)
                sensor_copy.remove(sensor)
                target_copy.remove(target)

                # Grab the x and y coordinates of the sensor and target, then calculate their distance and find the sensor's power.
                # Finally, calculate the cost, which is the number of time units the sensor is watching the target in this case.
                s_x, s_y = sensor[1], sensor[2]
                t_x, t_y = target[1], target[2]
                distance = euclidian_distance(s_x, s_y, t_x, t_y)
                sensor_power = sensor[3]
                cost = sensor_power / distance

                # This is a new pair (permutation of sensor/target) generated for our solution.
                new_pair = (sensor, target, cost)
                output_copy.add(new_pair)

                # Straightforward; we are just generating a new permutation of sensors assigned to targets with their updated cost
                new_state = (sensor_copy, target_copy, output_copy, min(state[3], cost), do_not_modify_targets)
                new_states.append(new_state)
    return new_states # Return the new set of states that we should scan over

# Calculate the distance between any two given points
# sqrt ( (x2 - x1)^2 + (y2 - y1)^2 )
def euclidian_distance(x_1, y_1, x_2, y_2):
    x_dist = math.pow(x_2 - x_1, 2)
    y_dist = math.pow(y_2 - y_1, 2)
    return math.sqrt(x_dist + y_dist)

def monitor_unique_value(curr_state):
    return curr_state[2] # Return the already formed set of sensor-target pairs

# In the monitoring problem, we have reached a goal state if there are no more sensors or targets to be assigned
def monitor_goal_test(curr_state):
    if not curr_state[0] and not curr_state[1]:
        return True
    else:
        return False

def monitor(search_info, search_type): # search_info is a list of the sensors IDs, location and power to start with
                          # The following index is a list of the target IDs and locations
                          # Power loss function is, Pt = P(t-1) - Euclidian distance between target and sensor
                          # search_type is the type of search we're doing (bfs, unicost, greedy, iddfs and Astar )
    sensor_info = search_info[1]
    target_info = search_info[2]
    results = ()
    if len(sensor_info) < len(target_info): # There are more targets than sensors, no solution is possible
        print("No solution was found")
        return
    if search_type == "bfs":
        init_state = (sensor_info, target_info, [], sys.maxint, target_info) # sensors, targets, sensor-target pairs, cost, another copy of targets list (DO NOT MANIPULATE THIS)
        actions = [""]
        results = bfs(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, monitor_find_optimal_goal_state)
    elif search_type == "unicost":
        init_state = (sensor_info, target_info, [], sys.maxint, target_info) # sensors, targets, sensor-target pairs, cost, another copy of targets list (DO NOT MANIPULATE THIS)
        actions = [""]
        results = unicost(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, find_next_optimal_cost_monitor, monitor_find_optimal_goal_state)
    elif search_type == "greedy":
        pass
    elif search_type == "iddfs":
        init_state = (sensor_info, target_info, [], sys.maxint, target_info)
        actions = [""]
        results = iddfs(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, monitor_find_optimal_goal_state)
        #print(results[0])
    elif search_type == "Astar":
        pass
    for pair in results[0][2]:
        print(pair[0][0] + " monitors " + pair[1][0])
    print("Time: " + str(results[1]))
    print("Space: Frontier " + str(results[2][0]) + ", Visited " + str(results[2][1]))
    print("Cost: " + str(results[3]))
    return

def aggregation_unique_value(curr_state):
    return curr_state[4]

def aggregation_find_optimal_goal_state(goal_states):
    min_cost = sys.maxint
    goal_state = ()
    for state in goal_states:
        if state[3] < min_cost:
            min_cost = state[3]
            goal_state = state
    return (goal_state, min_cost)

def find_next_network_connection(action, state):
    nodes = state[0]
    edges = state[1]
    path = state[2]
    edge_list = state[4]

    new_states = []
    #print("curr path: " + str(path))

    if not path:
        for node in nodes:
            new_path = list(path)
            new_path.append(node)
            new_state = (state[0], state[1], new_path, state[3], state[4])
            new_states.append(new_state)
    else:
        path_end_node = path[-1] # Get the node at the end of the current path so we can find which nodes have a connection with it
        path_end_node_name = path_end_node[0]
        for edge in edges:
            if edge[0] == path_end_node_name or edge[1] == path_end_node_name:
                connecting_node = str(edge[1]) if edge[0] == path_end_node_name else str(edge[0])
                node_already_exists = False
                for node in path:
                    if connecting_node == node[0]: # This edge's node is already in the path, we can't add it again or there will be a cycle
                        node_already_exists = True
                        break
                if not node_already_exists:
                    new_path = list(path)
                    new_edge_list = list(edge_list)
                    actual_connecting_node = ()
                    for node in nodes:
                        if node[0] == connecting_node:
                            actual_connecting_node = node
                            break
                    new_path.append(actual_connecting_node)
                    new_edge_list.append(edge)
                    new_state = (state[0], state[1], new_path, state[3] + edge[2], new_edge_list) # Update the cost of the path and the actual path
                    new_states.append(new_state)
    return new_states # Return the new set of states that we should scan over

def find_next_optimal_cost_aggregator(frontier):
    max_cost = sys.maxint
    curr_state = ()
    for state in frontier:
        if state[3] < max_cost:
            max_cost = state[3]
            curr_state = state
    frontier.remove(curr_state)
    return curr_state

def aggregation_goal_test(curr_state):
    num_nodes = len(curr_state[0])
    path_length = len(curr_state[2])
    if path_length == num_nodes:
        return True
    else:
        return False

def aggregation(search_info, search_type): # search_info is a list of the node IDs and locations of the nodes
                              # Each of the following indices specifies a connection between two nodes and the
                              #     time delay between the two nodes.
                              # search_type is the type of search we're doing (bfs, unicost, greedy, iddfs and Astar )
    #print(search_info)
    edges = []
    for i in xrange(2, len(search_info)):
        edges.append(search_info[i])
    if search_type == "bfs":
        init_state = (search_info[1], edges, [], 0, []) # nodes, edges, path, cost, edges used in path
        actions = [""]
        results = bfs(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, aggregation_find_optimal_goal_state)
    elif search_type == "unicost":
        init_state = (search_info[1], edges, [], 0, []) # nodes, edges, path, cost, edges used in path
        actions = [""]
        results = unicost(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, find_next_optimal_cost_aggregator, aggregation_find_optimal_goal_state)
    elif search_type == "greedy":
        pass
    elif search_type == "iddfs":
        init_state = (search_info[1], edges, [], 0, []) # nodes, edges, path, cost, edges used in path
        actions = [""]
        results = iddfs(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, aggregation_find_optimal_goal_state)
    elif search_type == "Astar":
        pass
    #print("results: " + str(results))
    for node in results[0][2]:
        print(node[0])
    print("Time: " + str(results[1]))
    print("Space: Frontier " + str(results[2][0]) + ", Visited " + str(results[2][1]))
    print("Cost: " + str(results[3]))
    return

if not len(sys.argv) == 3:
    print("Invalid number of arguments; two are required!")
    sys.exit()
if not sys.argv[2] in ["bfs", "unicost", "greedy", "iddfs", "Astar"]:
    print("Invalid keyword input!")
    sys.exit()
if not os.path.exists(sys.argv[1]):
    print("The specified file doesn't exist!")
    sys.exit()
execute_search(sys.argv[1], sys.argv[2])

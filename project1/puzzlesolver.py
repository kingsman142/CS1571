import sys
import os
import math
import time as ti

TEN_MINUTES = 600 # number of seconds in TEN minutes; indicates we should say no solution was found

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
        try:
            input[0] = input[0].rstrip().lower() # This input line states the type of problem
        except Exception as e:
            print("There was an error parsing the input!")
            return
    for i in xrange(1, len(input)): # Loop through the rest of the lines and turn strings into lists/tuples
        if len(input[i]) > 2:
            try:
                input[i] = eval(input[i].rstrip())
            except Exception as e:
                print("There was an error parsing the input!")
                return
        else:
            input.remove(input[i]) # The length of this line is just 1 or 2, so it might be a line containing just \n; remove it

    if input[0] == "monitor":
        if not len(input) == 3:
            print("Invalid input file; it should only have two lines of input!")
            return
        monitor(input, keyword.lower())
    elif input[0] == "aggregation":
        aggregation(input, keyword.lower())
    elif input[0] == "pancakes":
        pancakes(input, keyword.lower())
    else:
        print("That's an invalid problem!")

def unicost(init_state, actions, goal_state, transition, unique_value, optimal_cost, get_cost, unique_value_is_a_set):
    frontier = []
    explored = set([])
    frontier.append(init_state) # Append the initial state to the frontier
    time = 1 # We already created 1 node, the initial state
    frontier_space = 1 # Maximum amount of space the frontier grew to; right now it starts as 1 because of init_state
    visited = 0 # Number of nodes we have visited

    begin_time = ti.time()

    while frontier:
        curr_time = ti.time()
        if curr_time - begin_time >= TEN_MINUTES: # This algorithm is taking way too long on this input
            break

        curr_state = optimal_cost(frontier) # Loop through all states and find lowest cost
        state_unique_identifier = unique_value(curr_state)
        if unique_value_is_a_set: # Our unique identifier is a list/set and we can't add that directly to explored because explored is a set.
                                  # One workout for this is to just convert the list/set to a frozenset.
            state_unique_identifier = frozenset(state_unique_identifier)

        if goal_state(curr_state): # Check if we've reached the goal state or not
            cost = get_cost(curr_state)
            return (curr_state, time, (frontier_space, visited), cost)
        elif not state_unique_identifier or not state_unique_identifier in explored: # Check if we've explored this state before or not
            explored.add(state_unique_identifier) # Add this state to the explored set so we never travel it again
            visited += 1 # We have visited a new node
            for action in actions: # Execute each action
                new_state = transition(action, curr_state) # Generate the outcome states for this action
                for state in new_state: # For every new state we just generated
                    time += 1
                    frontier.append(state) # Add each new state to the frontier for us to explore later
                frontier_space = max(len(frontier), frontier_space) # Generate the new maximum frontier size
    print("No solution was found!")

def iddfs(init_state, actions, goal_state, transition, unique_value, get_cost, unique_value_is_a_set):
    nodes_created = 0
    max_frontier_size = 0
    max_explored_size = 0
    begin_time = ti.time()

    for i in xrange(0, 100): # From 0 depth to 100 depth (chosen arbitrarily), perform DFS
        curr_time = ti.time()
        if curr_time - begin_time >= TEN_MINUTES: # This algorithm is taking way too long on this input
            break

        return_info = dfs(init_state, actions, goal_state, set([]), transition, unique_value, 0, i, 1, 1, 1, unique_value_is_a_set) # initial state,
        if return_info:
            nodes_created = max(return_info[1], nodes_created)
            max_frontier_size = max(max_frontier_size, return_info[2])
            max_explored_size = max(max_explored_size, return_info[3])
            if return_info[0]: # We found a goal state, so return it
                cost = get_cost(return_info[0][0])
                return (return_info[0][0], nodes_created, (max_frontier_size, len(max_explored_size)), cost) # end state, time, (frontier space, explored space), cost
    print("No solution was found!")

def dfs(state, actions, goal_state, explored, transition, unique_value, depth, max_depth, nodes_created, frontier_size, max_frontier_size, unique_value_is_a_set):
    state_unique_identifier = unique_value(state) # Find the unique identifier for this state so we can add it to the explored set
    if unique_value_is_a_set: # Our unique identifier is a list/set and we can't add that directly to explored because explored is a set.
                              # One workout for this is to just convert the list/set to a frozenset.
        state_unique_identifier = frozenset(state_unique_identifier)

    if goal_state(state): # We have reached the goal!
        return ([state], 1, max_frontier_size, explored) # return the goal state, nodes created up to this point, max frontier size up to this point, and the explored states
    elif not state_unique_identifier or not state_unique_identifier in explored: # We haven't visited this state yet
        explored.add(state_unique_identifier) # Add the state to the explored set
        if depth < max_depth: # We can only go up to a certain depth, so if we're already there, don't go any further
            goal_states = []
            for action in actions: # Execute each action
                new_state = transition(action, state)
                for state in new_state: # For each new state that is returned, perform DFS
                    frontier_size -= 1 # We have visited a new state, so decrease the frontier size
                    return_value = dfs(state, actions, goal_state, explored, transition, unique_value, depth+1, max_depth, 0, frontier_size+len(new_state), max(max_frontier_size, frontier_size+len(new_state)), unique_value_is_a_set)
                    if not return_value is None: # We have achieved some kind of goal state, so we can work with some new information
                        max_frontier_size = max(max_frontier_size, return_value[2]) # If we increased the frontier size, update it accordingly
                        nodes_created += return_value[1] # Sum up the number of nodes in each sumtree / path we travel
                        for return_state in return_value[0]: # Basically pass the goal states up the DFS chain to the root node so we can return every single goal state in the end
                            goal_states.append(return_state)
                        if len(goal_states) > 0:
                            return (goal_states, nodes_created + 1, max_frontier_size, explored)
            nodes_created += 1 # Finally, add this node to the number of nodes created so we can recursively pass it up
            return (goal_states, nodes_created, max_frontier_size, explored)
    return None

def bfs(init_state, actions, goal_state, transition, unique_value, get_cost, unique_value_is_a_set):
    frontier = []
    explored = set([])
    frontier.append(init_state)
    time = 1 # We already created 1 node, the initial state
    frontier_space = 1 # Maximum amount of space the frontier grew to
    visited = 0 # Number of nodes we have visited
    begin_time = ti.time()

    while frontier:
        curr_time = ti.time()
        if curr_time - begin_time >= TEN_MINUTES: # This algorithm is taking way too long on this input
            break

        curr_state = frontier.pop(0) # Pop from the left of the list
        state_unique_identifier = unique_value(curr_state) # Grab this state's unique value
        if unique_value_is_a_set: # Our unique identifier is a list/set and we can't add that directly to explored because explored is a set.
                                  # One workout for this is to just convert the list/set to a frozenset.
            state_unique_identifier = frozenset(state_unique_identifier)

        if goal_state(curr_state): # We found a goal state!
            cost = get_cost(curr_state)
            return (curr_state, time, (frontier_space, visited), cost) # return solution path, time, space, and cost
        elif not state_unique_identifier or not state_unique_identifier in explored: # If we haven't explored this state yet
            if state_unique_identifier: # Add the unique identifier to the explored set
                explored.add(state_unique_identifier)
            visited += 1 # We have visited a new node
            for action in actions:
                new_state = transition(action, curr_state)
                for state in new_state: # For every state we just generated from executing the action "action"
                    time += 1
                    frontier.append(state)
                frontier_space = max(len(frontier), frontier_space)
    print("No solution was found!")

def greedy(init_state, actions, goal_state, transition, unique_value, get_cost, unique_value_is_a_set, best_first_greedy):
    frontier = []
    explored = set([])
    frontier.append(init_state)
    time = 1 # We already created 1 node, the initial state
    frontier_space = 1 # Maximum amount of space the frontier grew to
    visited = 0 # Number of nodes we have visited
    begin_time = ti.time()

    while frontier:
        curr_time = ti.time()
        if curr_time - begin_time >= TEN_MINUTES: # This algorithm is taking way too long on this input
            break

        curr_state = best_first_greedy(frontier) # Find the most greedy next state
        state_unique_identifier = unique_value(curr_state) # Get this state's unique identifier for the explored set
        if unique_value_is_a_set: # Our unique identifier is a list/set and we can't add that directly to explored because explored is a set.
                                  # One workout for this is to just convert the list/set to a frozenset.
            state_unique_identifier = frozenset(state_unique_identifier)

        if goal_state(curr_state): # We found a goal state!
            cost = get_cost(curr_state)
            return (curr_state, time, (frontier_space, visited), cost) # return solution path, time, space, and cost
        elif not state_unique_identifier or not state_unique_identifier in explored: # If we haven't explored this state yet
            if state_unique_identifier:
                explored.add(state_unique_identifier)
            visited += 1
            for action in actions: # Execute every action from this current state
                new_state = transition(action, curr_state) # All the new states generated after executing that action
                for state in new_state: # Add each new state to the frontier
                    time += 1
                    frontier.append(state)
                frontier_space = max(len(frontier), frontier_space)
    print("No solution was found!")

def astar(init_state, actions, goal_state, transition, unique_value, get_cost, unique_value_is_a_set, best_first_astar):
    frontier = []
    explored = set([])
    frontier.append(init_state)
    time = 1 # We already created 1 node, the initial state
    frontier_space = 1 # Maximum amount of space the frontier grew to
    visited = 0 # Number of nodes we have visited
    begin_time = ti.time()

    while frontier:
        curr_time = ti.time()
        if curr_time - begin_time >= TEN_MINUTES: # This algorithm is taking way too long on this input
            break

        curr_state = best_first_astar(frontier) # Find the next optimal state found with A*
        state_unique_identifier = unique_value(curr_state)
        if unique_value_is_a_set: # Our unique identifier is a list/set and we can't add that directly to explored because explored is a set.
                                  # One workout for this is to just convert the list/set to a frozenset.
            state_unique_identifier = frozenset(state_unique_identifier)

        if goal_state(curr_state): # We found a goal state!
            cost = get_cost(curr_state)
            return (curr_state, time, (frontier_space, visited), cost) # return solution path, time, space, and cost
        elif not state_unique_identifier or not state_unique_identifier in explored: # If we haven't explored this state yet
            if state_unique_identifier:
                explored.add(state_unique_identifier)
            visited += 1
            for action in actions: # Execute each action from this current state
                new_state = transition(action, curr_state) # All the new states generated from that action
                for state in new_state: # Add each new state to the frontier
                    time += 1
                    frontier.append(state)
                frontier_space = max(len(frontier), frontier_space)
    print("No solution was found!")

# Flips a set of pancakes (1, 2, 3, 4, 5) <--- (top to bottom format) at a specified index
# This index will flip all the pancakes from 0 to index
def flip_pancakes(index, curr_state):
    pancakes = curr_state[0]
    new_pancakes_list = tuple((-i for i in pancakes[0:index][::-1])) + pancakes[index:len(pancakes)] # Reverse the first "index" elements and append it to the rest of the original array
    new_pancakes_num_flips = curr_state[2] + 1 # We just executed one more flip
    new_state = (new_pancakes_list, curr_state[1], new_pancakes_num_flips)
    new_states = [new_state]
    return new_states

# Check if our pancakes are in their goal state
def pancakes_goal_test(curr_state):
    pancakes = curr_state[0]
    pancake_n = len(pancakes) # Number of pancakes to iterate over; they should be ordered from 1 to n
    for i in xrange(0, pancake_n):
        if not pancakes[i] == (i+1):
            return False # If the pancake we came across is not in decreasing diameter size or not in the correct spot in the array, we have not reached a goal state
    return True

# The unique value for the pancakes are their current order
def pancakes_unique_value(curr_state):
    return curr_state[0] # Return the pancakes list

# Current cost at a current state
def pancakes_get_cost(state):
    return state[2] # Grab the number of flips

# This is our function to find the next state for unicost
def find_next_optimal_pancakes(frontier):
    best_choice = frontier[0]
    frontier.remove(best_choice)
    return best_choice

def pancakes_similarity_to_goal(state):
    pancakes = state[0]
    pancakes_n = len(pancakes)
    distance = 0 # For every pancake we find that's not in its correct index, we add 1 to the distance
                 # For every pancake we find that's negative, we add 1 to the distance
    for i in xrange(1, pancakes_n+1):
        if pancakes[i-1] < 0:
            distance += 1
        if not abs(pancakes[i-1]) == i:
            distance += 1
    return distance

def pancakes_greedy_best_first(frontier):
    # Select the one that's most similar to the goal
    best_choice = None
    best_similarity_to_goal = sys.maxint
    for state in frontier:
        this_state_similarity = pancakes_similarity_to_goal(state)
        if best_choice is None:
            best_choice = state
            best_similarity_to_goal = this_state_similarity
        elif this_state_similarity < best_similarity_to_goal:
            best_choice = state
            best_similarity_to_goal = this_state_similarity
    frontier.remove(best_choice)
    return best_choice

def pancakes_astar_best_first(frontier):
    # Select the one with lowest sum of (similarity to the goal) and (steps taken so far)
    best_choice = None
    best_similarity_to_goal = sys.maxint
    lowest_steps_so_far = 0
    for state in frontier:
        this_state_similarity = pancakes_similarity_to_goal(state)
        if best_choice is None:
            best_choice = state
            best_similarity_to_goal = this_state_similarity
            lowest_steps_so_far = state[2]
        elif (this_state_similarity + state[2]) < (best_similarity_to_goal + lowest_steps_so_far):
            best_choice = state
            best_similarity_to_goal = this_state_similarity
            lowest_steps_so_far = state[2]
    frontier.remove(best_choice)
    return best_choice

# Execute the pancakes problem
def pancakes(search_info, search_type):
    pancake_start = search_info[1]
    pancake_goal = search_info[2]
    results = None
    init_state = (pancake_start, pancake_goal, 0) # pancakes, goal state, 0 steps so far
    actions = [i for i in range(1, len(pancake_goal)+1)] # Create a list from 1 to n; this indicates where we place the pancake flipper for each iteration
    if search_type == "bfs":
        results = bfs(init_state, actions, pancakes_goal_test, flip_pancakes, pancakes_unique_value, pancakes_get_cost, False)
    elif search_type == "unicost":
        results = unicost(init_state, actions, pancakes_goal_test, flip_pancakes, pancakes_unique_value, find_next_optimal_pancakes, pancakes_get_cost, False)
    elif search_type == "greedy":
        results = greedy(init_state, actions, pancakes_goal_test, flip_pancakes, pancakes_unique_value, pancakes_get_cost, False, pancakes_greedy_best_first)
    elif search_type == "iddfs":
        results = iddfs(init_state, actions, pancakes_goal_test, flip_pancakes, pancakes_unique_value, pancakes_get_cost, False)
    elif search_type == "astar":
        results = astar(init_state, actions, pancakes_goal_test, flip_pancakes, pancakes_unique_value, pancakes_get_cost, False, pancakes_astar_best_first)

    if not results is None:
        print("Time: " + str(results[1]))
        print("Space: Frontier " + str(results[2][0]) + ", Visited " + str(results[2][1]))
        print("Cost: " + str(results[3]) + " flips")
    return

# Get the cost of a monitor state
def monitor_get_cost(state):
    return state[3]

# Our function for the monitor problem, unicost search
def find_next_optimal_cost_monitor(frontier):
    max_cost = 0
    curr_state = ()
    for state in frontier:
        if state[3] > max_cost:
            max_cost = state[3]
            curr_state = state
    frontier.remove(curr_state)
    return curr_state

# Transition function for the monitoring problem
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
                new_state = (sensor_copy, targets, output_copy, new_target_cost, do_not_modify_targets, state[5], state[6])
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
                new_state = (sensor_copy, target_copy, output_copy, min(state[3], cost), do_not_modify_targets, state[5], state[6])
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

def monitor_greedy_best_first(frontier):
    best_choice = None
    total_sum_distances = sys.maxint
    for state in frontier:
        total_sensor_dist = 0
        total_target_dist = 0
        for sensor in state[0]: # for each sensor in this state's available sensors
            total_sensor_dist += euclidian_distance(sensor[1], sensor[2], state[5][0], state[5][1])
        for target in state[1]: # for each target in this state's available targets
            total_target_dist += euclidian_distance(target[1], target[2], state[6][0], state[6][1])

        if best_choice is None:
            best_choice = state
            total_sum_distances = total_sensor_dist + total_target_dist
            pass
        elif (total_sensor_dist + total_target_dist) < total_sum_distances:
            best_choice = state
            total_sum_distances = total_sensor_dist + total_target_dist
    frontier.remove(best_choice)
    return best_choice

def monitor_astar_best_first(frontier):
    best_choice = None
    total_sum_distances = sys.maxint
    for state in frontier:
        total_sensor_dist = 0
        total_target_dist = 0
        for sensor in state[0]: # for each sensor in this state's available sensors
            total_sensor_dist += euclidian_distance(sensor[1], sensor[2], state[5][0], state[5][1])
        for target in state[1]: # for each target in this state's available targets
            total_target_dist += euclidian_distance(target[1], target[2], state[6][0], state[6][1])

        if best_choice is None:
            best_choice = state
            total_sum_distances = state[3] + total_sensor_dist + total_target_dist # state[3] (current cost) + cost to get to the goal state
            pass
        elif (state[3] + total_sensor_dist + total_target_dist) > total_sum_distances:
            best_choice = state
            total_sum_distances = state[3] + total_sensor_dist + total_target_dist
    frontier.remove(best_choice)
    return best_choice

def find_average_location_monitor(nodes):
    x_sum = 0
    y_sum = 0
    n = 0
    for node in nodes:
        x_sum += node[1]
        y_sum += node[2]
        n += 1
    x_avg = x_sum/n
    y_avg = y_sum/n
    return (x_avg, y_avg)

def monitor(search_info, search_type): # search_info is a list of the sensors IDs, location and power to start with
                          # The following index is a list of the target IDs and locations
                          # Power loss function is, Pt = P(t-1) - Euclidian distance between target and sensor
                          # search_type is the type of search we're doing (bfs, unicost, greedy, iddfs and Astar )
    sensor_info = search_info[1]
    target_info = search_info[2]
    results = None
    average_sensor_x, average_sensor_y = find_average_location_monitor(sensor_info)
    average_target_x, average_target_y = find_average_location_monitor(target_info)

    # available sensors, available targets, target-sensor pairs, max time monitoring, immutable target copy list, average location of sensors, average location of targets
    init_state = (sensor_info, target_info, [], sys.maxint, target_info, (average_sensor_x, average_sensor_y), (average_target_x, average_target_y))
    actions = [""] # Create a list from 1 to n; this indicates where we place the pancake flipper for each iteration
    if len(sensor_info) < len(target_info): # There are more targets than sensors, no solution is possible
        print("No solution was found")
        return
    if search_type == "bfs":
        results = bfs(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, monitor_get_cost, True)
    elif search_type == "unicost":
        results = unicost(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, find_next_optimal_cost_monitor, monitor_get_cost, True)
    elif search_type == "greedy":
        results = greedy(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, monitor_get_cost, True, monitor_greedy_best_first)
    elif search_type == "iddfs":
        results = iddfs(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, monitor_get_cost, True)
    elif search_type == "astar":
        results = astar(init_state, actions, monitor_goal_test, find_next_target_sensor, monitor_unique_value, monitor_get_cost, True, monitor_astar_best_first)

    if not results is None:
        for pair in results[0][2]:
            print(pair[0][0] + " monitors " + pair[1][0])
        print("Time: " + str(results[1]))
        print("Space: Frontier " + str(results[2][0]) + ", Visited " + str(results[2][1]))
        print("Cost: " + str(results[3]))
    return

def aggregation_unique_value(curr_state):
    return curr_state[4]

# Get the cost of an aggregation state
def aggregation_get_cost(state):
    return state[3]

# Transition function for the aggregation problem
def find_next_network_connection(action, state):
    nodes = state[0]
    edges = state[1]
    path = state[2]
    edge_list = state[4]
    new_states = []

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

# For our unicost search problem
def find_next_optimal_cost_aggregator(frontier):
    max_cost = sys.maxint
    curr_state = ()
    for state in frontier:
        if state[3] < max_cost:
            max_cost = state[3]
            curr_state = state
    frontier.remove(curr_state)
    return curr_state

# Check if we have connected all nodes
def aggregation_goal_test(curr_state):
    num_nodes = len(curr_state[0])
    path_length = len(curr_state[2])
    if path_length == num_nodes:
        return True
    else:
        return False

def aggregation_greedy_best_first(frontier):
    best_choice = None
    for state in frontier:
        if best_choice is None:
            best_choice = state
        elif len(state[4]) > 0:
            if len(best_choice[4]) > 0:
                if state[4][-1][2] < best_choice[4][-1][2]:
                    best_choice = state
            else:
                best_choice = state
    frontier.remove(best_choice)
    return best_choice

def aggregation_astar_best_first(frontier):
    best_choice = None
    for state in frontier:
        if best_choice is None:
            best_choice = state
        elif len(state[4]) > 0:
            if len(best_choice[4]) > 0:
                if (state[3] + state[4][-1][2]) < (best_choice[3] + best_choice[4][-1][2]): # state[4][-1][2] gets the state's edges, then the last edge in that list, and finally its latency
                    best_choice = state
            else:
                best_choice = state
    frontier.remove(best_choice)
    return best_choice

def aggregation(search_info, search_type): # search_info is a list of the node IDs and locations of the nodes
                              # Each of the following indices specifies a connection between two nodes and the
                              #     time delay between the two nodes.
                              # search_type is the type of search we're doing (bfs, unicost, greedy, iddfs and Astar )
    edges = []
    for i in xrange(2, len(search_info)):
        edges.append(search_info[i])
    init_state = (search_info[1], edges, [], 0, []) # nodes, edges, path, cost, edges used in path
    actions = [""]
    results = None

    if search_type == "bfs":
        results = bfs(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, aggregation_get_cost, True)
    elif search_type == "unicost":
        results = unicost(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, find_next_optimal_cost_aggregator, aggregation_get_cost, True)
    elif search_type == "greedy":
        results = greedy(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, aggregation_get_cost, True, aggregation_greedy_best_first)
    elif search_type == "iddfs":
        results = iddfs(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, aggregation_get_cost, True)
    elif search_type == "astar":
        results = astar(init_state, actions, aggregation_goal_test, find_next_network_connection, aggregation_unique_value, aggregation_get_cost, True, aggregation_astar_best_first)

    if not results is None:
        print("Path in order of when a node is visited:")
        for node in results[0][2]:
            print(node[0])
        print("Time: " + str(results[1]))
        print("Space: Frontier " + str(results[2][0]) + ", Visited " + str(results[2][1]))
        print("Cost: " + str(results[3]))
    return

if not len(sys.argv) == 3:
    print("Invalid number of arguments; two are required!")
    sys.exit()
if not sys.argv[2] in ["bfs", "unicost", "greedy", "iddfs", "astar"]:
    print("Invalid keyword input!")
    sys.exit()
if not os.path.exists(sys.argv[1]):
    print("The specified file doesn't exist!")
    sys.exit()
execute_search(sys.argv[1], sys.argv[2])

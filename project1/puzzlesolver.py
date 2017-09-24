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
        input[i] = eval(input[i].rstrip())
    print(input)
    print("input len: " + str(len(input)))
    #print("input[0]: " + str(input[0]))
    if input[0] == "monitor":
        if not len(input) == 3:
            print("Invalid input file; it should only have two lines of input!")
            return
        monitor(input, keyword)
    elif input[0] == "aggregation":
        aggregation(input, keyword)

def bfs(init_state, actions, goal_state, transition):
    frontier = []
    frontier.append(init_state)
    goal_states = []
    print("bfs frontier size: " + str(len(frontier)))

    while frontier:
        curr_state = frontier.pop(0) # Pop from the left of the list
        if goal_state(curr_state):
            #print(curr_state)
            goal_states.append(curr_state)
        for action in actions:
            #print(str(curr_state))
            new_state = transition(action, curr_state)
            for state in new_state:
                frontier.append(state)

    return goal_states

def find_next_target_sensor(action, state):
    sensors = state[0]
    targets = state[1]
    output = state[2]
    do_not_modify_targets = state[4]
    #print(sensors)
    #print(targets)

    new_states = []

    if sensors and not targets:
        for sensor in sensors:
            for target in do_not_modify_targets:
                sensor_copy = list(sensors)
                output_copy = list(output)
                sensor_copy.remove(sensor)
                s_x, s_y = sensor[1], sensor[2]
                t_x, t_y = target[1], target[2]
                distance = euclidian_distance(s_x, s_y, t_x, t_y)
                sensor_power = sensor[3]
                cost = sensor_power / distance
                new_pair = (sensor, target, cost)
                output_copy.append(new_pair)

                new_target_cost = sys.maxint
                target_cost_dict = {}
                for pair in output_copy:
                    if pair[1] in target_cost_dict:
                        target_cost_dict[pair[1]] = max(target_cost_dict[pair[1]], pair[2])
                        #if sensor[0] == 'S_4' and target[0] == 'T_2':
                        #    print("val of " + str(pair[1]) + " = " + str(target_cost_dict[pair[1]]))
                    else:
                        target_cost_dict[pair[1]] = pair[2]
                        #if sensor[0] == 'S_4' and target[0] == 'T_2':
                        #    print("val of " + str(pair[1]) + " = " + str(target_cost_dict[pair[1]]))
                #if sensor[0] == 'S_4' and target[0] == 'T_2':
                #    print()
                for key, val in target_cost_dict.iteritems():
                    if val < new_target_cost:
                        new_target_cost = val

                new_state = (sensor_copy, targets, output_copy, new_target_cost, do_not_modify_targets)
                #print(str(sensor) + ", " + str(target) + ", " + str(output_copy))
                #if sensor[0] == 'S_4' and target[0] == 'T_2':
                #    print(str(output_copy) + ", " + str(new_target_cost))
                new_states.append(new_state)
    else:
        for sensor in sensors:
            for target in targets:
                sensor_copy = list(sensors)
                target_copy = list(targets)
                output_copy = list(output)
                sensor_copy.remove(sensor)
                target_copy.remove(target)
                s_x, s_y = sensor[1], sensor[2]
                t_x, t_y = target[1], target[2]
                distance = euclidian_distance(s_x, s_y, t_x, t_y)
                sensor_power = sensor[3]
                cost = sensor_power / distance
                new_pair = (sensor, target, cost)
                output_copy.append(new_pair)
                #print(str(sensor) + ", " + str(target) + ", " + str(output_copy))
                new_state = (sensor_copy, target_copy, output_copy, min(state[3], cost), do_not_modify_targets)
                new_states.append(new_state)
    #print("returning...")
    return new_states

def euclidian_distance(x_1, y_1, x_2, y_2):
    x_dist = math.pow(x_2 - x_1, 2)
    y_dist = math.pow(y_2 - y_1, 2)
    return math.sqrt(x_dist + y_dist)

def monitor_goal_test(curr_state):
    #print("len sens: " + str(len(curr_state[0])) + ", len targ: " + str(len(curr_state[1])))
    if not curr_state[0] and not curr_state[1]: #and len(curr_state[2]) == len(curr_state[0]):
        return True
    else:
        return False

def monitor(search_info, search_type): # search_info is a list of the sensors IDs, location and power to start with
                          # The following index is a list of the target IDs and locations
                          # Power loss function is, Pt = P(t-1) - Euclidian distance between target and sensor
                          # search_type is the type of search we're doing (bfs, unicost, greedy, iddfs and Astar )
    sensor_info = search_info[1]
    target_info = search_info[2]
    if len(sensor_info) < len(target_info): # There are more targets than sensors, no solution is possible
        print("No solution was found")
        return
    if search_type == "bfs":
        init_state = (sensor_info, target_info, [], sys.maxint, target_info) # sensors, targets, sensor-target pairs, cost, another copy of targets list (DO NOT MANIPULATE THIS)
        actions = [""]
        goal_state = ([], [])
        results = bfs(init_state, actions, monitor_goal_test, find_next_target_sensor)
        max_cost = (0, 0, 0, 0)
        for result in results:
            if result[3] > max_cost[3]:
                max_cost = result
        print(max_cost)
        pass
    elif search_type == "unicost":
        pass
    elif search_type == "greedy":
        pass
    elif search_type == "iddfs":
        pass
    elif search_type == "Astar":
        pass
    return

def aggregation(search_info, search_type): # search_info is a list of the node IDs and locations of the nodes
                              # Each of the following indices specifies a connection between two nodes and the
                              #     time delay between the two nodes.
                              # search_type is the type of search we're doing (bfs, unicost, greedy, iddfs and Astar )
    if search_type == "bfs":
        pass
    elif search_type == "unicost":
        pass
    elif search_type == "greedy":
        pass
    elif search_type == "iddfs":
        pass
    elif search_type == "Astar":
        pass
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

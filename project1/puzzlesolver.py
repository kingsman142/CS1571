import sys
import os

def execute_search(filename, keyword):
    # Output:
    # The solution path (or “No solution” if nothing was found): print one state per line.
    # Time: expressed in terms of the total number of nodes created.
    # Space: expressed as the maximum number of nodes kept in memory (the biggest size
    #    that the frontier list grew to) as well as the maximum number of states stored on the
    #    explored list. Please report these as two separate numbers.
    # Cost: the final cost of the specified path or configuration.
    with open(filename, "r") as config_file:
        input = config_file.readlines()
    print(input)
    if input[0] == "monitor":
        if not len(input) == 3:
            print("Invalid input file; it should only have two lines of input!")
            return
        monitor(input, keyword)
    elif input[0] == "aggregation":
        aggregation(input, keyword)

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

def bfs():
    return

if not len(sys.argv) == 3:
    print("Invalid number of arguments; two are required!")
    return
if not sys.argv[2] in ["bfs", "unicost", "greedy", "iddfs", "Astar"]:
    print("Invalid keyword input!")
    return
if not os.path.exists(sys.argv[1]):
    print("The specified file doesn't exist!")
    return
execute_search(sys.argv[1], sys.argv[2])

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
    if not len(input) == 2:
        print("Invalid input file; it should only have two lines of input!")
        return
    if input[0] == "monitor":
        monitor()
    elif input[0] == "aggregation":
        aggregation()

def monitor(search_info): # search_info is a list of the sensors IDs, location and power to start with

    return

def aggregation(search_info): # search_info is a list of the node IDs and locations of the nodes
                              # Each of the following indices specifies a connection between two nodes and the
                              #     time delay between the two nodes.
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

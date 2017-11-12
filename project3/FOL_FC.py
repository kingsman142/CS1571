import sys
import os

SYMBOLS = ["^", "v", "->"]

class Clause:
    def __init__(self, fact):
        self.fact = fact
        self.variables = []

        left_paren_index = self.fact.find("(")
        right_paren_index = self.fact.find(")")
        args = self.fact[left_paren_index+1 : right_paren_index]
        self.variables = args.split(",")
        self.fact = self.fact[0:left_paren_index]

    def str(self):
        return self.fact + "(" + ",".join(self.variables) + ")"

class Predicate:
    def __init__(self, logic):
        self.parse_logic(logic)

    def parse_logic(self, logic):
        self.clauses = filter(None, logic.split(" ")) # Filter function removes '' items from list
        #print("clauses: " + str(self.clauses))
        if "->" in self.clauses:
            self.LHS, self.RHS = self.convert_rule_to_clauses(self.clauses)
        else:
            self.LHS = self.clauses
            self.RHS = []

        new_clauses = []
        self.LHS_objects = []
        self.RHS_objects = []
        still_in_LHS = True
        for clause in self.clauses:
            if not clause in SYMBOLS:
                new_clause = Clause(clause)
                new_clauses.append(new_clause)
                if clause in self.LHS:
                    self.LHS_objects.append(new_clause)
                else:
                    self.RHS_objects.append(new_clause)
            else:
                new_clauses.append(clause)
                if not clause == "->":
                    if still_in_LHS:
                        self.LHS_objects.append(clause)
                    else:
                        self.RHS_objects.append(clause)
                else:
                    still_in_LHS = False

        self.clauses_objects = new_clauses
        #print("objects: " + str(self.clauses_objects))

    def convert_rule_to_clauses(self, rule):
        index_of_implication = rule.index("->")
        LHS = rule[ : index_of_implication]
        RHS = rule[index_of_implication : len(rule)+1]
        return (LHS, RHS)

    def find_match(self, predicate):
        for clause in self.clauses_objects:
            if not clause in SYMBOLS:
                if predicate.fact == clause.fact:
                    self.unify(self.clauses_objects, clause, predicate)
                    if self.is_satisfied():
                        self.clauses_objects = self.RHS_objects

    def is_satisfied(self):
        for clause in self.clauses_objects:
            if clause not in SYMBOLS:
                for variable in clause.variables:
                    if not self.is_instance(variable):
                        return False
        return True

    def unify(self, clauses, clause, predicate):
        clause_var = clause.variables
        predicate_var = predicate.variables
        substitutions = {}
        for i in xrange(0, len(clause_var)):
            #print("check if " + clause_var[i] + " is a variable")
            if not self.is_instance(clause_var[i]): # Current clause arg is a variable, not an instance, so look for a replacement
                if self.is_instance(predicate_var[i]):
                    #print("substitute " + clause_var[i] + " with " + predicate_var[i])
                    substitutions[clause_var[i]] = predicate_var[i]

        for curr_clause in clauses:
            if not curr_clause in SYMBOLS:
                for i in xrange(0, len(curr_clause.variables)):
                    variable = curr_clause.variables[i]
                    if variable in substitutions:
                        curr_clause.variables[i] = substitutions[variable] # Substitute a variable for an instance

    def is_instance(self, arg):
        return not arg.islower()

    def get_predicate(self):
        return self.clauses_objects

    def str(self):
        output = ""
        for clause in self.clauses_objects:
            if clause in SYMBOLS:
                output += clause + " "
            else:
                output += clause.str() + " "
        output = output.rstrip()
        return output

def read_input(test_file):
    with open(test_file) as test_case:
        logic = test_case.readlines()
    logic = [line.rstrip() for line in logic]
    return logic

def create_statements(logic):
    predicates = []
    line_number = 1
    prev_begin_line_number = 1
    goal = None

    rules = []
    facts = []

    for predicate in logic:
        if "PROVE" in predicate:
            goal = filter(None, predicate.split(" "))[1]
            print(str(line_number) + ". Goal: " + goal)
        else:
            new_predicate = Predicate(predicate)
            predicates.append(new_predicate)
            if "->" in predicate:
                rules.append(new_predicate)
            else:
                facts.append(new_predicate)
            print(str(line_number) + ". " + new_predicate.str() + " --  Given")
        line_number += 1

    found_goal = False
    # TODO: SPLIT UP PREDICATES FROM FACTS/ATOMIC STATEMENTS SO WE KNOW WHEN TO STOP ONCE ALL FACTS ARE DEPLETED (create 'rules' and 'facts' lists)
    while len(predicates) > 1 and not found_goal:
        new_predicates = []
        for i in xrange(0, len(predicates)):
            pred_original = predicates[i].str()
            for j in xrange(0, len(predicates)):
                if not predicates[i] == predicates[j] and len(predicates[j].get_predicate()) == 1:
                    pred_before = predicates[i].str()
                    predicates[i].find_match(predicates[j].get_predicate()[0])
                    if not pred_before == predicates[i].str():
                        if len(predicates[i].str()) > 0:
                            #print(str(line_number) + ". " + predicates[i].str() + " --  Resolve from " + str(prev_begin_line_number + i) + " and " + str(prev_begin_line_number + j))
                            print(str(line_number) + ". " + predicates[i].str())
                        line_number += 1
            if len(predicates[i].str()) > 0 and not pred_original == predicates[i].str():
                if predicates[i].str() == goal:
                    found_goal = True
                    #print("pred: " + predicates[i].str() + " and goal: " + goal + " MATCH!")
                    break
                new_predicates.append(predicates[i])

            if found_goal:
                break

        predicates = new_predicates
        prev_begin_line_number = line_number

    if found_goal:
        print("\nDue to our final statement, we have arrived at our goal. \nTherefore, our proof is correct!")
    else:
        print("\nUnfortunately, our proof is incorrect!")

    return predicates

if not len(sys.argv) == 2:
    print("Invalid number of arguments!")

test_file = sys.argv[1]
propositional_logic = read_input(test_file)
parsed_logic = create_statements(propositional_logic)

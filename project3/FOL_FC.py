import sys
import os

class Clause:
    def __init__(self, fact):
        self.fact = fact
        self.negation = False
        self.variables = []
        if fact[0] == "~":
            self.negation = True
            self.fact = self.fact.strip("~")

        left_paren_index = self.fact.find("(")
        right_paren_index = self.fact.find(")")
        args = self.fact[left_paren_index+1 : right_paren_index]
        self.variables = args.split(",")
        self.fact = self.fact[0:left_paren_index]

    def negated(self):
        return self.negation

    def str(self):
        if self.negation:
            return "~" + self.fact + "(" + ",".join(self.variables) + ")"
        else:
            return self.fact + "(" + ",".join(self.variables) + ")"

    def negate(self):
        self.negation = not self.negation

class Predicate:
    def __init__(self, logic):
        self.parse_logic(logic)

    def parse_logic(self, logic):
        self.clauses = filter(None, logic.split(" ")) # Filter function removes '' items from list
        if "->" in self.clauses:
            self.clauses = self.convert_rule_to_clauses(self.clauses)
        elif "PROVE" in self.clauses:
            self.clauses = self.convert_to_assumption(self.clauses)
        else:
            pass

        new_clauses = []
        for clause in self.clauses:
            if not clause in ["^", "v"]:
                new_clause = Clause(clause)
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause)

        self.clauses_objects = new_clauses

    def convert_rule_to_clauses(self, rule):
        index_of_implication = rule.index("->")
        #print("index: " + str(index_of_implication))
        for i in xrange(0, index_of_implication):
            if rule[i] == "^":
                rule[i] = "v"
            elif rule[i] == "v":
                rule[i] = "^"
            else: # Current index is a predicate
                rule[i] = "~" + rule[i]
        rule[index_of_implication] = "v"
        return rule

    def convert_to_assumption(self, statement):
        return ["~" + statement[1]]

    def find_negation(self, predicate):
        for clause in self.clauses_objects:
            if not clause in ["^", "v"]:
                if predicate.negated() and not clause.negated():
                    if predicate.fact == clause.fact:
                        self.unify(self.clauses_objects, clause, predicate)
                        i = 0
                        while i < len(self.clauses_objects):
                            if isinstance(self.clauses_objects[i], Clause) and self.clauses_objects[i].fact == predicate.fact:
                                if i < len(self.clauses_objects)-1:
                                    del self.clauses_objects[i+1]
                                    del self.clauses_objects[i]
                                elif i > 0:
                                    del self.clauses_objects[i]
                                    del self.clauses_objects[i-1]
                                else:
                                    del self.clauses_objects[i]
                            i += 1
                elif clause.negated() and not predicate.negated():
                    if clause.fact == predicate.fact:
                        self.unify(self.clauses_objects, clause, predicate)
                        i = 0
                        while i < len(self.clauses_objects):
                            if isinstance(self.clauses_objects[i], Clause) and self.clauses_objects[i].fact == predicate.fact:
                                if i < len(self.clauses_objects)-1:
                                    del self.clauses_objects[i+1]
                                    del self.clauses_objects[i]
                                elif i > 0:
                                    del self.clauses_objects[i]
                                    del self.clauses_objects[i-1]
                                else:
                                    del self.clauses_objects[i]
                            i += 1

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
            if not curr_clause in ["^", "v"]:
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
            if clause in ["^", "v"]:
                output += clause + " "
            else:
                output += clause.str() + " "
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

    for predicate in logic:
        new_predicate = Predicate(predicate)
        predicates.append(new_predicate)
        print(str(line_number) + ". " + new_predicate.str() + " --  Given")
        line_number += 1

    while len(predicates) > 1:
        new_predicates = []
        for i in xrange(0, len(predicates)):
            pred_original = predicates[i].str()
            for j in xrange(i+1, len(predicates)):
                if not predicates[i] == predicates[j] and len(predicates[j].get_predicate()) == 1:
                    pred_before = predicates[i].str()
                    predicates[i].find_negation(predicates[j].get_predicate()[0])
                    if not pred_before == predicates[i].str():
                        if len(predicates[i].str()) == 0:
                            #print(str(line_number) + ". {} --  Resolve from " + str(prev_begin_line_number + i) + " and " + str(prev_begin_line_number + j))
                            print(str(line_number) + ". {} " + predicates[i].str())
                        else:
                            #print(str(line_number) + ". " + predicates[i].str() + " --  Resolve from " + str(prev_begin_line_number + i) + " and " + str(prev_begin_line_number + j))
                            print(str(line_number) + ". " + predicates[i].str())
                        line_number += 1
            if len(predicates[i].str()) > 0 and not pred_original == predicates[i].str():
                new_predicates.append(predicates[i])
        predicates = new_predicates
        prev_begin_line_number = line_number

    if len(predicates) == 0:
        print("\nDue to our final statement, we have arrived at an empty predicate. \nOur initial assumption is false, so our proof is correct!")
    else:
        print("\nWe have arrived at a non-empty predicate. \nOur initial assumption is true.  Therefore, our proof is incorrect!")

    return predicates

if not len(sys.argv) == 2:
    print("Invalid number of arguments!")

test_file = sys.argv[1]
propositional_logic = read_input(test_file)
parsed_logic = create_statements(propositional_logic)

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
        #print("vars: " + str(self.variables))

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
        #print(logic)
        self.parse_logic(logic)

    def parse_logic(self, logic):
        self.clauses = filter(None, logic.split(" ")) # Filter function removes '' items from list
        if "->" in self.clauses:
            #print("Rule: ")
            self.clauses = self.convert_rule_to_clauses(self.clauses)
        elif "PROVE" in self.clauses:
            #print("Assumption: ")
            self.clauses = self.convert_to_assumption(self.clauses)
        else:
            pass#print("Fact: ")

        new_clauses = []
        for clause in self.clauses:
            if not clause in ["^", "v"]:
                new_clause = Clause(clause)
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause)

        self.clauses_objects = new_clauses
        #print(self.clauses)

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
                #print("predicate: " + predicate.fact + ", clause: " + clause.fact)
                #print(str(type(predicate)) + " and " + str(type(clause)))
                if predicate.negated() and not clause.negated():
                    #predicate.negate()
                    if predicate.fact == clause.fact:
                        #print("Found negation a")
                        #print("predicate args: " + str(predicate.variables))
                        #print("clause args: " + str(clause.variables))
                        self.unify(self.clauses_objects, clause, predicate)
                        #print("clause fact: " + clause.fact + ", predicate fact: " + predicate.fact)
                        i = 0
                        #print("before a: " + self.str())
                        while i < len(self.clauses_objects):
                            #print("i: " + str(i))
                            if isinstance(self.clauses_objects[i], Clause) and self.clauses_objects[i].fact == predicate.fact:
                                #print("trying to remove " + self.clauses_objects[i].str())
                                if i < len(self.clauses_objects)-1:
                                    #print("removing indices " + str(i) + " and " + str(i+1))
                                    del self.clauses_objects[i+1]
                                    del self.clauses_objects[i]
                                elif i > 0:
                                    #print("removing indices " + str(i) + " and " + str(i-1))
                                    del self.clauses_objects[i]
                                    del self.clauses_objects[i-1]
                                else:
                                    del self.clauses_objects[i]
                                #if i > 0:
                                #    self.clauses_objects.remove(self.clauses_objects[i-1])
                            i += 1
                        #self.clauses_objects = [clause for clause in self.clauses_objects if clause in ["^", "v"] or (isinstance(clause, Clause) and not clause.fact == predicate.fact)]
                        #print("predicate args: " + str(predicate.variables))
                        #print("clause args: " + str(clause.variables))
                        #print(self.str())
                elif clause.negated() and not predicate.negated():
                    if clause.fact == predicate.fact:
                        #print("Found negation b")
                        #print("predicate args: " + str(predicate.variables))
                        #print("clause args: " + str(clause.variables))
                        self.unify(self.clauses_objects, clause, predicate)
                        #print("clause fact: " + clause.fact + ", predicate fact: " + predicate.fact)
                        i = 0
                        #print("\nbefore b (len = " + str(len(self.clauses_objects)) + "): " + self.str())
                        while i < len(self.clauses_objects):
                            #print("i: " + str(i))
                            if isinstance(self.clauses_objects[i], Clause) and self.clauses_objects[i].fact == predicate.fact:
                                #print("trying to remove " + self.clauses_objects[i].str())
                                if i < len(self.clauses_objects)-1:
                                    #print("removing indices " + str(i) + " and " + str(i+1))
                                    del self.clauses_objects[i+1]
                                    del self.clauses_objects[i]
                                elif i > 0:
                                    #print("removing indices " + str(i) + " and " + str(i-1) + " for " + predicate.fact + " in " + self.str())
                                    del self.clauses_objects[i]
                                    del self.clauses_objects[i-1]
                                else:
                                    #print("bfore removing 0: " + self.str() + ", len: " + str(len(self.clauses_objects)))
                                    #print("removing index 0")
                                    del self.clauses_objects[i]
                                #if i > 0:
                                #    self.clauses_objects.remove(self.clauses_objects[i-1])
                            i += 1
                        #self.clauses_objects = [clause for clause in self.clauses_objects if clause in ["^", "v"] or (isinstance(clause, Clause) and not clause.fact == predicate.fact)]
                        #print("predicate args: " + str(predicate.variables))
                        #print("clause args: " + str(clause.variables))
                        #print("result: " + self.str())

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
    for predicate in logic:
        new_predicate = Predicate(predicate)
        predicates.append(new_predicate)
        print(new_predicate.str())

    while len(predicates) > 1:
        new_predicates = []
        print("len: " + str(len(predicates)))
        for i in xrange(0, len(predicates)):
            print("i BEFORE: " + predicates[i].str())
            if len(predicates[i].get_predicate()) > 1:
                for j in xrange(i, len(predicates)):
                    if not predicates[i] == predicates[j] and len(predicates[j].get_predicate()) == 1:
                        print("j: " + predicates[j].str())
                        pred_before = predicates[i].str()
                        predicates[i].find_negation(predicates[j].get_predicate()[0])
                        if not pred_before == predicates[i].str():
                            print("i AFTER: " + predicates[i].str())
                if len(predicates[i].str()) > 0:
                    print("pushing " + predicates[i].str())
                    new_predicates.append(predicates[i])
        predicates = new_predicates
        print()

    if len(predicates) == 0:
        print("Our initial assumption is false, so our proof is correct!")
    else:
        print(predicates[0].str())
        print("Our initial assumption is true.  Therefore, our proof is incorrect!")

    return predicates

if not len(sys.argv) == 2:
    print("Invalid number of arguments!")

test_file = sys.argv[1]
propositional_logic = read_input(test_file)
parsed_logic = create_statements(propositional_logic)

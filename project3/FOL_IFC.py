import sys
import os

SYMBOLS = ["^", "v", "->"]

class Clause:
    def __init__(self, fact):
        if not fact is None:
            self.fact = fact
            self.variables = []

            left_paren_index = self.fact.find("(")
            right_paren_index = self.fact.find(")")
            args = self.fact[left_paren_index+1 : right_paren_index]
            self.variables = args.split(",")
            self.fact = self.fact[0:left_paren_index]

    def str(self):
        return self.fact + "(" + ",".join(self.variables) + ")"

    def copy(self):
        new_fact = str(self.fact)
        new_variables = list(self.variables)
        new_clause = Clause(None)
        new_clause.fact = new_fact
        new_clause.variables = new_variables
        return new_clause

class Predicate:
    def __init__(self, logic):
        if not logic is None:
            self.parse_logic(logic)
        self.substitutions = {}

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

    def find_match(self, predicate, facts):
        #print("find match for " + predicate.str())
        new_predicate = self
        for clause in new_predicate.clauses_objects:
            if not clause in SYMBOLS:
                if predicate.fact == clause.fact:
                    #print("unifying " + clause.str() + " and " + predicate.str())
                    new_predicate = new_predicate.unify(new_predicate.clauses_objects, clause, predicate)
                    if new_predicate is None:
                        #print("new predicate: None")
                        continue
                    #print("new predicate: " + new_predicate.str())
                    if is_satisfied(new_predicate, facts):
                        #print("SATISFIED")
                        new_predicate.clauses_objects = new_predicate.RHS_objects
        return new_predicate

    def unify(self, clauses, clause, predicate):
        clause_var = list(clause.variables)
        predicate_var = predicate.variables
        sub_copy = dict(self.substitutions)
        clauses_copy = []
        LHS_objects_copy = []
        RHS_objects_copy = []

        for i in xrange(0, len(clause_var)):
            #print("check if " + clause_var[i] + " is a variable")
            if not self.is_instance(clause_var[i]): # Current clause arg is a variable, not an instance, so look for a replacement
                if self.is_instance(predicate_var[i]) and predicate_var[i] not in sub_copy.values():
                    #print("sub values: " + str(self.substitutions.values()))
                    #print("substitute " + clause_var[i] + " with " + predicate_var[i])
                    sub_copy[clause_var[i]] = predicate_var[i]
            else:
                if not predicate_var[i] == clause_var[i]:
                    return self

        for curr_clause in clauses:
            if not curr_clause in SYMBOLS:
                new_clause = curr_clause.copy()
                #print("clause copy before: " + new_clause.str())
                for i in xrange(0, len(new_clause.variables)):
                    variable = new_clause.variables[i]
                    if variable in sub_copy:
                        new_clause.variables[i] = sub_copy[variable] # Substitute a variable for an instance
                        #print("clause copy after: " + new_clause.str())
                clauses_copy.append(new_clause)
                if curr_clause in self.LHS_objects:
                    LHS_objects_copy.append(new_clause)
                elif curr_clause in self.RHS_objects:
                    RHS_objects_copy.append(new_clause)
            else:
                clauses_copy.append(curr_clause)

        new_predicate = Predicate(None)
        new_predicate.variables = clause_var
        new_predicate.substitutions = sub_copy
        new_predicate.clauses = list(self.clauses)
        new_predicate.clauses_objects = clauses_copy
        new_predicate.LHS = list(self.LHS)
        new_predicate.RHS = list(self.RHS)
        new_predicate.LHS_objects = LHS_objects_copy
        new_predicate.RHS_objects = RHS_objects_copy
        #print("new: " + new_predicate.str())
        return new_predicate

    def is_instance(self, arg):
        return not arg.islower()

    def get_predicates(self):
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

def is_satisfied(predicate, facts):
    #print("checking satisfiable: " + predicate.str())
    for clause in predicate.LHS_objects:
        if clause not in SYMBOLS:
            #print("clause: " + clause.str())
            for variable in clause.variables:
                if not predicate.is_instance(variable):
                    return False
            valid = False
            for fact in facts:
                #print("comparing " + fact.str() + " to " + clause.str())
                if fact.str() == clause.str():
                    #print("clause " + clause.str() + " is a fact")
                    valid = True
                    break
            if not valid:
                return False
    return True

def generate_all_facts_and_rules(rule, all_facts, facts_index, all_existing_facts):
    if facts_index == len(all_facts):
        return [rule]

    new_predicates = []
    for i in xrange(facts_index, len(all_facts)):
        pred_before = rule.str()
        #print("find match between " + all_facts[i].get_predicates()[0].str() + " and " + pred_before)
        new_rule = rule.find_match(all_facts[i].get_predicates()[0], all_facts + all_existing_facts)
        if not new_rule.str() == pred_before:
            new_predicates.append(new_rule)
            new_rules = generate_all_facts_and_rules(new_rule, all_facts, i+1, all_existing_facts)
            for k in new_rules:
                if not k.str() == pred_before:
                    new_predicates.append(k)
    return new_predicates

def create_statements(logic):
    predicates = []
    line_number = 1
    prev_begin_line_number = 1
    goal = None

    rules = []
    facts = []
    all_facts = []
    all_rules = []

    for predicate in logic:
        if "PROVE" in predicate:
            goal = filter(None, predicate.split(" "))[1]
            print(str(line_number) + ". Goal: " + goal)
        else:
            new_predicate = Predicate(predicate)
            predicates.append(new_predicate)
            if "->" in predicate:
                rules.append(new_predicate)
                all_rules.append(new_predicate)
            else:
                facts.append(new_predicate)
                all_facts.append(new_predicate)
            print(str(line_number) + ". " + new_predicate.str() + "  --  Given")
        line_number += 1

    found_goal = False
    # TODO: SPLIT UP PREDICATES FROM FACTS/ATOMIC STATEMENTS SO WE KNOW WHEN TO STOP ONCE ALL FACTS ARE DEPLETED (create 'rules' and 'facts' lists)
    old_facts_len = len(all_facts)
    old_rules_len = len(all_rules)
    incremental_facts_index = 0
    while len(all_facts) > 0 and len(rules) > 0 and not found_goal:
        new_facts = []
        new_rules = []
        i = 0
        #print("# facts: " + str(len(all_facts)) + ", # rules: " + str(len(rules)))
        while i < len(all_rules) and i < 5:
            #print("I = " + str(i) + ", len: " + str(len(all_rules)))
            pred_original = all_rules[i].str()
            #print("original: " + pred_original)
            new_rule = None
            #print("try to generate new rules and facts from " + all_rules[i].str())
            new_facts_and_rules = generate_all_facts_and_rules(all_rules[i], facts, 0, all_facts + new_facts)
            for new_info in new_facts_and_rules:
                if len(new_info.get_predicates()) == 1:
                    fact_exists = False
                    for fact in all_facts:
                        if fact.str() == new_info.str():
                            fact_exists = True
                            break
                    for fact in new_facts:
                        if fact.str() == new_info.str():
                            fact_exists = True
                            break
                    if not fact_exists:
                        print(str(line_number) + ". " + new_info.str() + "  --  created from rule " + pred_original)# + " and fact " + all_facts[i].str()) # change this i back to a j
                        line_number += 1
                        if new_info.str() == goal:
                            found_goal = True
                            break
                        new_facts.append(new_info)
                        #all_facts.append(new_info)
                else:
                    rule_exists = False
                    for rule in all_rules:
                        if rule.str() == new_info.str():
                            rule_exists = True
                            break
                    for rule in new_rules:
                        if rule.str() == new_info.str():
                            rule_exists = True
                            break
                    if not rule_exists and not is_satisfied(new_info, all_facts + new_facts):
                        #all_rules.append(new_info)
                        new_rules.append(new_info)
                        #print("found new rule: " + new_info.str())
                        #print(str(line_number) + ". " + new_rule.str())
                        if new_info.str() == goal:
                            found_goal = True
                            break
                        #line_number += 1
                    elif not rule_exists:
                        pass
                        #print("found fact that was a rule: " + new_info.str())

            #j = incremental_facts_index

            if found_goal:
                break
            i += 1

        incremental_facts_index = len(all_facts)
        #facts = new_facts
        #all_facts = all_facts + new_facts
        facts = new_facts
        all_facts = all_facts + new_facts
        #rules = new_rules
        all_rules = all_rules + new_rules
        if len(all_facts) <= old_facts_len and len(all_rules) <= old_rules_len: # We didn't add any new facts
            #print("facts breaking")
            break
        else:
            old_facts_len = len(all_facts)
            old_rules_len = len(all_rules)

        #print("# rules: " + str(len(rules)) + ", # facts: " + str(len(facts)))
        prev_begin_line_number = line_number

    if found_goal:
        print("\nDue to our final statement, we have arrived at our goal. \nTherefore, our proof is correct!")
    else:
        #print("# facts: " + str(len(facts)) + ", # rules: " + str(len(rules)))
        print("\nUnfortunately, our proof is incorrect!")

    return predicates

if not len(sys.argv) == 2:
    print("Invalid number of arguments!")

test_file = sys.argv[1]
propositional_logic = read_input(test_file)
parsed_logic = create_statements(propositional_logic)

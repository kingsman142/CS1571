import sys
import os

SYMBOLS = ["^", "v", "->"] # Create a global constant that contains all the symbols of the predicates

class Clause:
    def __init__(self, fact):
        if not fact is None: # When this is None, we will manually set the variables, so don't run the below code
            self.fact = fact # e.g. fact of Parent(x, y) = Parent
            self.variables = [] # variables in the parentheses of the fact

            left_paren_index = self.fact.find("(")
            right_paren_index = self.fact.find(")")
            args = self.fact[left_paren_index+1 : right_paren_index]
            self.variables = args.split(",")
            self.fact = self.fact[0:left_paren_index]

    def str(self):
        return self.fact + "(" + ",".join(self.variables) + ")"

    def copy(self): # Send a copy of this clause as a reference to a new clause
        new_fact = str(self.fact)
        new_variables = list(self.variables)
        new_clause = Clause(None)
        new_clause.fact = new_fact
        new_clause.variables = new_variables
        return new_clause

class Predicate:
    UNIFICATIONS = 0
    
    def __init__(self, logic):
        if not logic is None:
            self.parse_logic(logic) # given e.g. Owns(Nono,x)  ^  Missile(x)  ->  Sells(West,Nono,x), separate everything into clauses and symbols
        self.substitutions = {} # The substituted variables for instances in this particular predicate

    def parse_logic(self, logic): # Separate the entire predicate into Clause objects
        self.clauses = filter(None, logic.split(" ")) # Filter function removes '' items from list
        if "->" in self.clauses:
            self.LHS, self.RHS = self.convert_rule_to_clauses(self.clauses) # We need to separate all the clauses on the left of the -> from the clauses on the right
        else: # This predicate is a fact, so there is no RHS; we just want to put all the clauses in the LHS
            self.LHS = self.clauses
            self.RHS = []

        new_clauses = []
        self.LHS_objects = []
        self.RHS_objects = []
        still_in_LHS = True # Since we have to separate clauses into LHS and RHS, we need to know when to switch between lists
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
                    still_in_LHS = False # Found the implication arrow; we have officially moved to the RHS

        self.clauses_objects = new_clauses # Different from self.clauses; this stores references to Clause instances that we can use later for unification

    def convert_rule_to_clauses(self, rule): # Separate the text of the predicate into two strings; one represents the LHS; the other represents RHS
        index_of_implication = rule.index("->")
        LHS = rule[ : index_of_implication]
        RHS = rule[index_of_implication : len(rule)+1]
        return (LHS, RHS)

    def find_match(self, predicate, facts): # Given another predicate (guaranteed to be a fact), find if there is a match with this predicate.  In other words, try to unify the fact with this predicate.
        new_predicate = self # This is an immutable function.  If anything needs to be modified in this predicate, return a new Predicate instance with the new information.
        for clause in new_predicate.clauses_objects: # Iterate through all the clauses in this predicate
            if not clause in SYMBOLS:
                if predicate.fact == clause.fact: # We found a match!  Now check if the variables and instances can be intertwined.
                    new_predicate = new_predicate.unify(new_predicate.clauses_objects, clause, predicate) # Try to unify
                    if new_predicate is None: # Unification failed; something went wrong, so just try to unify with a similar clause later in the predicate
                        continue
                    if is_satisfied(new_predicate, facts): # This predicate is satisfied, so we have reached the conclusion, which is the clause on the RHS of the predicate.
                        new_predicate.clauses_objects = new_predicate.RHS_objects
        return new_predicate # Return instance of new Predicate.  This may be a fact or a new rule.

    def unify(self, clauses, clause, predicate): # Unify this predicate with a fact; this function is immutable
        Predicate.UNIFICATIONS += 1
        clause_var = list(clause.variables)
        predicate_var = predicate.variables # The fact's variables; these may be instances or just variables
        sub_copy = dict(self.substitutions)
        clauses_copy = []
        LHS_objects_copy = []
        RHS_objects_copy = []

        # Try to find any possible substitions
        for i in xrange(0, len(clause_var)):
            if not self.is_instance(clause_var[i]): # Current clause arg is a variable, not an instance, so look for a replacement
                if self.is_instance(predicate_var[i]) and predicate_var[i] not in sub_copy.values(): # The fact's current arg is an instance and the instance hasn't been used in this overarching predicate yet, so it's compatible
                    sub_copy[clause_var[i]] = predicate_var[i]
            else: # The clauses's arg is an instance, so if the fact's current arg (an instance) doesn't match, there's no way we can merge the two
                if not predicate_var[i] == clause_var[i]:
                    return self

        # Perform the actual substition of variables
        for curr_clause in clauses:
            if not curr_clause in SYMBOLS:
                new_clause = curr_clause.copy() # Create a new copy of the clause for the new predicate we're creating since this function is immutable
                for i in xrange(0, len(new_clause.variables)): # Loop through all the variables in this clause and just try to substitute all of them
                    variable = new_clause.variables[i]
                    if variable in sub_copy:
                        new_clause.variables[i] = sub_copy[variable] # Substitute a variable for an instance
                clauses_copy.append(new_clause)
                if curr_clause in self.LHS_objects:
                    LHS_objects_copy.append(new_clause)
                elif curr_clause in self.RHS_objects:
                    RHS_objects_copy.append(new_clause)
            else: # Can't substitute a symbol
                clauses_copy.append(curr_clause)

        # Set all of the attributes of the new Predicate reference with copied over/modified data
        new_predicate = Predicate(None)
        new_predicate.variables = clause_var
        new_predicate.substitutions = sub_copy
        new_predicate.clauses = list(self.clauses)
        new_predicate.clauses_objects = clauses_copy
        new_predicate.LHS = list(self.LHS)
        new_predicate.RHS = list(self.RHS)
        new_predicate.LHS_objects = LHS_objects_copy
        new_predicate.RHS_objects = RHS_objects_copy
        return new_predicate

    def is_instance(self, arg): # Checks whether a clause's given argument is a variable or instance (all lower = variable, beginning uppercase letter = instance)
        return not arg.islower()

    def get_predicates(self): # Return all the clauses in this predicate
        return self.clauses_objects

    def str(self):
        output = ""
        for clause in self.clauses_objects:
            if clause in SYMBOLS:
                output += clause + " "
            else:
                output += clause.str() + " "
        output = output.rstrip() # Strip trailing whitespace
        return output

def get_num_unifications():
    return Predicate.UNIFICATIONS

def read_input(test_file): # From a given test file, read all the lines containing the proof's base logic
    with open(test_file) as test_case:
        logic = test_case.readlines()
    logic = [line.rstrip() for line in logic]
    return logic

def is_satisfied(predicate, facts): # Given a predicate and all the facts we know, return True or False depending on whether all the LHS clauses are true
    for clause in predicate.LHS_objects:
        if clause not in SYMBOLS:
            for variable in clause.variables:
                if not predicate.is_instance(variable):
                    return False
            valid = False
            for fact in facts: # Is this current clause a fact?
                if fact.str() == clause.str():
                    valid = True
                    break
            if not valid:
                return False
    return True

def generate_all_facts_and_rules(rule, all_facts, facts_index, all_existing_facts): # Given a rule and all the current iteration's facts, generate all combinations of the
                                                                                    # facts for each rule to prepare for the next iteration.
    if facts_index == len(all_facts): # BASE CASE: We ran out of facts
        return [rule]

    new_predicates = [] # All the new rules and facts that are generated
    for i in xrange(facts_index, len(all_facts)): # Generic permutation generation loop
        pred_before = rule.str()
        new_rule = rule.find_match(all_facts[i].get_predicates()[0], all_facts + all_existing_facts) # See if we can unify this current fact with the predicate
        if not new_rule.str() == pred_before: # There was a successful unification
            new_predicates.append(new_rule) # New rule or fact was generated
            new_rules = generate_all_facts_and_rules(new_rule, all_facts, i+1, all_existing_facts) # Recursively try to generate more facts and rules
            for k in new_rules: # For all the rules that were just recursively generated, if they aren't repeats, add them to the new predicates list
                if not k.str() == pred_before:
                    new_predicates.append(k)
    return new_predicates

def is_rule_eligible(predicate): # If a predicate has at least one variable in it, it's considered a rule
    for clause in predicate.LHS_objects: # Loop through all the clauses
        if clause not in SYMBOLS:
            for variable in clause.variables: # Loop through all the arguments in this clause
                if not predicate.is_instance(variable): # If it's a variable and not an instance, this is a rule
                    return True
    return False

def create_statements(logic): # Write out the actual proof to the user
    predicates = []
    line_number = 1 # The line number; makes it easier for the user to follow
    prev_begin_line_number = 1
    goal = None # Goal we're trying to find

    rules = []
    facts = []
    all_facts = [] # All the facts we've ever come across or generated
    all_rules = [] # All the rules we've ever come across or generated

    # Generate all the predicates from the text file logic given to us
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

    found_goal = False # When the goal is found, this will be switched to True and the loops will break
    old_facts_len = len(all_facts) # Keep track of whether we actually added new facts in the current iteration
    old_rules_len = len(all_rules) # Keep track of whether we actually added new rules in the current iteration
    while len(all_facts) > 0 and len(rules) > 0 and not found_goal:
        new_facts = [] # Facts generated in this current iteration
        new_rules = [] # Rules generated in this current iteration
        i = 0
        while i < len(all_rules): # Loop through all the rules we've ever generated
            pred_original = all_rules[i].str() # Keep track of this rule's original contents so we know if any changes were made to it
            new_facts_and_rules = generate_all_facts_and_rules(all_rules[i], facts, 0, all_facts + new_facts) # Given this rule, loop over all the facts in this iteration and generate all possible new rules and facts
            for new_info in new_facts_and_rules: # new_info could be a rule or a fact
                if len(new_info.get_predicates()) == 1: # Fact
                    fact_exists = False
                    for fact in all_facts: # Make sure this fact wasn't generated in previous iterations
                        if fact.str() == new_info.str():
                            fact_exists = True
                            break
                    for fact in new_facts: # Make sure this fact wasn't already generated in this current iteration
                        if fact.str() == new_info.str():
                            fact_exists = True
                            break
                    if not fact_exists: # This fact doesn't exist yet, so we can successfully add it to our facts list and print it to the user as new knowledge
                        print(str(line_number) + ". " + new_info.str())
                        line_number += 1
                        if new_info.str() == goal: # Check if we've reached the goal!
                            found_goal = True
                            break
                        new_facts.append(new_info)
                else: # Rule
                    rule_exists = False
                    for rule in all_rules: # Make sure this rule wasn't generated in previous iterations
                        if rule.str() == new_info.str():
                            rule_exists = True
                            break
                    for rule in new_rules: # Make sure this rule wasn't already generated in this current iteration
                        if rule.str() == new_info.str():
                            rule_exists = True
                            break
                    if not rule_exists and not is_satisfied(new_info, all_facts + new_facts) and is_rule_eligible(new_info): # This fact doesn't exist yet AND it isn't completely satisfied (it's a legitimate rule, not a fact with all clause arguments as instances)
                        new_rules.append(new_info)
                        print(str(line_number) + ". " + new_info.str())
                        line_number += 1
                        if new_info.str() == goal: # Check if we've reached the goal!  Honestly, this shouldn't ever occur in the rules section, but I put it in as a safeguard.
                            found_goal = True
                            break
                    elif not rule_exists: # It's a fact that was disguised as a rule
                        pass

            if found_goal:
                break
            i += 1

        facts = new_facts # Next iteration's facts are replaced by the new facts generated in this iteration
        all_facts = all_facts + new_facts # Add the new facts to the list of all facts ever generated
        all_rules = all_rules + new_rules # Add the new rules to the list of all rules ever generated
        if len(all_facts) <= old_facts_len and len(all_rules) <= old_rules_len: # We didn't add any new facts or rules, so we can't do anything new in the proof
            break
        else: # Set the old lengths of the facts and rules list so we can check the above if statement in the future
            old_facts_len = len(all_facts)
            old_rules_len = len(all_rules)

        prev_begin_line_number = line_number

    if found_goal:
        print("\nDue to our final statement, we have proved the goal correct!")
    else:
        print("\nUnfortunately, we were not able to prove the goal! \nWe exhausted all rules and facts.")
    print("Unification attempts: " + str(get_num_unifications()))

    return predicates

if not len(sys.argv) == 2:
    print("Invalid number of arguments!")

test_file = sys.argv[1]
propositional_logic = read_input(test_file)
parsed_logic = create_statements(propositional_logic)

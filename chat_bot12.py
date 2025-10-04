import itertools
import re

# --- 1. Expression Evaluation and Parsing ---

def evaluate_expression(expression, assignment):
    """
    Evaluates a propositional logic expression based on a truth assignment.
    
    The evaluation substitutes propositions (like P, Q) with their truth values (True/False)
    and uses Python's logic operators (and, or, not) for the connectives.
    """
    
    # 1. Substitute Connectives with Python Operators
    expr = expression.replace('->', 'implies')  # Custom 'implies' for A->B = (not A) or B
    expr = expr.replace('<->', 'iff')          # Custom 'iff' for A<->B = (A and B) or (not A and not B)
    expr = expr.replace('^', 'and')            # Conjunction
    expr = expr.replace('&', 'and')            # Conjunction
    expr = expr.replace('v', 'or')             # Disjunction
    expr = expr.replace('~', 'not ')           # Negation (note the space for clarity)
    expr = expr.replace('!', 'not ')           # Negation
    
    # 2. Define Custom Logic Functions for non-standard Python operators
    def implies(a, b):
        return (not a) or b
        
    def iff(a, b):
        return (a and b) or (not a and not b)

    # 3. Substitute Propositions with their Truth Values
    for prop, value in assignment.items():
        # Ensure only whole proposition symbols are replaced (e.g., 'P' not part of 'Q')
        # We use regex for this precise substitution: \b matches word boundaries
        expr = re.sub(r'\b' + prop + r'\b', str(value), expr)
        
    # 4. Evaluate the Expression String
    try:
        # Use eval to execute the logical expression string
        result = eval(expr, {'implies': implies, 'iff': iff}, {})
        return result
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return False

def get_propositions(expression):
    """
    Extracts all unique proposition symbols (single uppercase letters)
    from the expression.
    """
    # Regex to find all uppercase letters not preceded by a logical symbol that might look like a letter
    propositions = set(re.findall(r'[A-Z]', expression))
    return sorted(list(propositions))

# --- 2. The Main Validity Checker ---

def check_validity(expression):
    """
    Checks if a logical expression is a TAUTOLOGY (always True) 
    using the Truth Table method.
    """
    props = get_propositions(expression)
    num_props = len(props)
    
    if num_props == 0:
        return "Error: No propositional symbols found (use P, Q, R, etc.)."
        
    # Generate all possible truth assignments (2^n rows)
    # The permutations are tuples of (True, False, ...)
    truth_values = [True, False]
    all_assignments = list(itertools.product(truth_values, repeat=num_props))
    
    is_tautology = True
    
    # Iterate through all rows of the truth table
    for assignment_tuple in all_assignments:
        
        # Create a dictionary mapping the proposition symbol to its value
        assignment = dict(zip(props, assignment_tuple))
        
        # Evaluate the expression for this assignment
        result = evaluate_expression(expression, assignment)
        
        # If any result is False, it's not a tautology
        if result is False:
            is_tautology = False
            # Find the counterexample (the assignment that makes it False)
            counterexample = {p: assignment[p] for p in props}
            return False, counterexample

    # If the loop completes without finding a False case
    return True, None

# --- 3. Simple Chatbot Interface ---

def run_chatbot():
    """
    A simple command-line interface to interact with the checker.
    """
    print("🤖 Welcome to the Propositional Logic Checker!")
    print("Operators supported: -> (Implies), <-> (Iff), ^ or & (And), v (Or), ~ or ! (Not)")
    print("Use uppercase letters (P, Q, R) for propositions.")
    print("Type 'exit' to quit.")
    print("-" * 40)
    
    while True:
        try:
            expression = input("Enter expression: ").strip()
            
            if expression.lower() == 'exit':
                print("Goodbye! 👋")
                break
                
            if not expression:
                continue

            # Run the validity check
            result, data = check_validity(expression)
            
            if result is True:
                print(f"✅ The expression '{expression}' is a **TAUTOLOGY** (logically valid).")
            
            elif result is False:
                print(f"❌ The expression '{expression}' is **NOT a TAUTOLOGY**.")
                # Format and print the counterexample
                formatted_example = ", ".join([f"{p}={v}" for p, v in data.items()])
                print(f"   **Counterexample:** The expression is **False** when {formatted_example}.")
            
            else:
                # Handle error message from check_validity
                print(f"⚠️ {result}")
                
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# --- Execute the Chatbot ---
if __name__ == "__main__":
    # Example test cases (you can uncomment these to run tests)
    # print(check_validity("P v ~P"))             # Tautology (True)
    # print(check_validity("(P ^ Q) -> Q"))       # Tautology (True)
    # print(check_validity("P -> Q"))             # Not a Tautology (False)
    # print(check_validity("P ^ ~P"))             # Contradiction (False)
    
    run_chatbot()
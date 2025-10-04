from flask import Flask, render_template, request
import itertools, re

app = Flask(__name__)

# --- Logic Functions ---
def evaluate_expression(expression, assignment):
    # Standardize operator symbols for Python's eval
    # 1. Replace complex operators first, adding generous spaces
    expr = expression.replace('->', ' implies ').replace('<->', ' iff ')
    expr = expr.replace('^', ' and ').replace('&', ' and ')
    expr = expr.replace('v', ' or ')
    
    # 2. Replace negation operators
    # We replace '~' and '!' with ' not '
    expr = expr.replace('~', ' not ').replace('!', ' not ') 
    
    # 3. Clean up extra spaces
    expr = re.sub(r'\s+', ' ', expr).strip()
    
    # CRITICAL FIX: Ensure every 'not P' term is parenthesized to fix operator precedence issues in eval().
    # This specifically targets 'not' followed by an uppercase letter (P, Q, R...)
    # We look for 'not' followed by 1 or more spaces, and then an uppercase letter.
    # We replace it with 'not (uppercase_letter)'
    expr = re.sub(r'(not\s+)([A-Z]+)', r'not (\2)', expr)
    
    # Define custom logic functions for implied operators
    def implies(a, b): return (not a) or b
    def iff(a, b): return (a and b) or (not a and not b)

    # Prepare globals and locals for SAFE evaluation.
    globals_dict = {
        'implies': implies, 
        'iff': iff, 
        'True': True, 
        'False': False
    }
    locals_dict = assignment

    try:
        # Use eval with the proposition assignments in locals_dict
        return eval(expr, globals_dict, locals_dict)
    except Exception as e:
        # For debugging purposes, print the failed expression and error
        print(f"Evaluation Failed: Expression='{expr}', Error={e}")
        return False


def get_propositions(expression):
    # Find all single alphabetic characters to use as propositional symbols
    return sorted(list(set(re.findall(r'[A-Z]', expression))))


def check_validity(expression):
    # Enforce capitalization since get_propositions only looks for [A-Z]
    if any(c.islower() for c in expression if c.isalpha()):
         return "Error: Please use only uppercase letters (P, Q, R, etc.) for propositions.", None
         
    props = get_propositions(expression)
    if not props:
        # Check for malformed or empty expressions
        if not expression or expression.isspace():
             return "Error: Expression is empty.", None
        return "Error: No propositional symbols found (use uppercase letters).", None

    # Generate all possible truth assignments (Truth Table)
    all_assignments = list(itertools.product([True, False], repeat=len(props)))

    # Iterate through all assignments to find a counterexample
    for assignment_tuple in all_assignments:
        assignment = dict(zip(props, assignment_tuple))
        result = evaluate_expression(expression, assignment)
        
        # If the result is False, we found a counterexample
        if not result:
            formatted = ", ".join([f"{p}={v}" for p, v in assignment.items()])
            return False, formatted # Not a tautology

    # If all assignments yielded True, it is a tautology
    return True, None


# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    expression = ""
    if request.method == "POST":
        expression = request.form.get("expression", "").strip()
        if expression:
            check = check_validity(expression)
            if isinstance(check, tuple):
                valid, counter = check
                if valid:
                    result = f"✅ '{expression}' is a TAUTOLOGY"
                else:
                    # IMPROVEMENT: Format the counterexample for better readability (T/F instead of True/False)
                    readable_counter = counter.replace('True', 'T').replace('False', 'F')
                    result = f"❌ '{expression}' is NOT a tautology. Counterexample: {readable_counter}"
            else:
                # Handle error messages returned from check_validity
                result = f"⚠️ {check}"
        else:
            result = "⚠️ Please enter a propositional logic expression to check."
            
    return render_template("index.html", result=result, expression=expression)


if __name__ == "__main__":
    app.run(debug=True)

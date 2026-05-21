n = int(input("Enter number of Python code lines: "))
print("Enter Python code:")
pl = []
for i in range(n):
    pl.append(input())
cl = []
vt = {}
# This function identifies datatype
def get_type(v):
    v = v.strip()
    if v.lstrip('-').isdigit():
        return "int"
    elif v.replace('.', '', 1).lstrip('-').isdigit():
        return "float"
    elif v.startswith('"') or v.startswith("'"):
        return "char*"
    else:
        return "int"
# Converting Python boolean syntax into C boolean syntax
def convert_condition(cond):
    import re #Used for advanced pattern matching and text replacement. and also for regex based transformations.
    # re.sub() Find pattern inside text and replace it.
    cond = re.sub(r'\bnot\s+', '!', cond)
    cond = re.sub(r'\band\b', '&&', cond)
    cond = re.sub(r'\bor\b', '||', cond)
    cond = re.sub(r'\bTrue\b', '1', cond)
    cond = re.sub(r'\bFalse\b', '0', cond)
    return cond
indent_stack = [0]
stopped = False
# ---------------- MAIN LOOP ----------------
for line in pl:
    if line.strip() == "":
        continue
    indent = len(line) - len(line.lstrip())
    l = line.strip() # contains current Python line without extra spaces. and remove spaces from both start & ends of the line.
    # If current indentation becomes smaller than previous indentation, close block.
    while len(indent_stack) > 1 and indent < indent_stack[-1]: 
        cl.append("}")
        indent_stack.pop()
    # convert comments
    if l.startswith("#"):
        comment_text = l[1:].strip()
        cl.append(f'// {comment_text}')
        continue
    # unsupported features
    unsupported = [
        "def ",
        "class ",
        "return",
        "break",
        "continue",
        "import ",
        "try",
        "except"
    ]
    for kw in unsupported:
        if l.startswith(kw):
            print("\nSorry, this feature is not supported yet.")
            stopped = True
            break
    if stopped:
        break



    # IF
    # contains current Python line without extra spaces.
    if l.startswith("if "):
        condition = convert_condition(l[3:].rstrip(":")) # Extract condition and convert it to C syntax
        cl.append(f'if ({condition})' + " {")
        indent_stack.append(indent + 4)
    # ELIF
    elif l.startswith("elif "):
        condition = convert_condition(l[5:].rstrip(":"))
        cl.append(f'else if ({condition})' + " {")
        indent_stack.append(indent + 4)
    # ELSE
    elif l.startswith("else"):
        cl.append("else {")
        indent_stack.append(indent + 4)



    # WHILE LOOP
    elif l.startswith("while "):
        condition = convert_condition(l[6:].rstrip(":"))
        cl.append(f'while ({condition})' + " {")
        indent_stack.append(indent + 4)



    # FOR LOOP
    elif l.startswith("for ") and "range" in l:
        parts = l.split() # Split the line into parts based on whitespace. This will help us extract the loop variable and range parameters.
        var = parts[1] # The loop variable is the second part of the line (after 'for').
        range_part = l[l.find("range(")+6 : l.rfind(")")] # +6 is there because moves cursor AFTER "range("   and l.rfind(")" this finds closing bracket
        nums = [x.strip() for x in range_part.split(",")] # if range is "1,5,2" then split will be ["1", "5", "2"] and if range is "5" then nums will be ["5"]
        if len(nums) == 1:
            start = "0"
            end = nums[0]
            step = "1"
        elif len(nums) == 2:
            start, end = nums
            step = "1"
        else:
            start, end, step = nums
        if step.startswith("-"): # it check if loop is decrementing or incrementing. if step is negative then condition will be var > end otherwise var < end
            condition = f"{var} > {end}" # negative step for decrementing
        else:
            condition = f"{var} < {end}"
        cl.append(
            f'for (int {var} = {start}; {condition}; {var} += {step})' + " {"
        )
        indent_stack.append(indent + 4)



    # INPUT
    elif "input(" in l and "=" in l:
        var = l.split("=")[0].strip()
        rhs = l.split("=", 1)[1].strip()
        if rhs.startswith("int("):
            t = "int"
            scan = f'scanf("%d", &{var});'
        elif rhs.startswith("float("):
            t = "float"
            scan = f'scanf("%f", &{var});'
        else:
            t = "char"
            scan = f'scanf("%s", {var});'
        ip = rhs[rhs.find("input(")+6 : rhs.rfind(")")] # extract prompt message
        if t == "char": #string need array in C, so we declare char array of size 100. you can adjust size as needed.
            cl.append(f'char {var}[100];')
        else:
            cl.append(f'{t} {var};')
        if ip.startswith('"') or ip.startswith("'"):
            prompt = ip.replace("'", '"')
            cl.append(f'printf({prompt});')
        cl.append(scan)
        vt[var] = t # store variable type in variable table for later use in print statements




    # PRINT statements
    elif l.startswith("print("):
        inner = l[6 : l.rfind(")")]
        if inner.startswith('"') or inner.startswith("'"):
            text = inner.replace("'", '"')
            cl.append(f'printf({text});')
        elif inner in vt:
            t = vt[inner]
            if t == "int":
                fmt = "%d"
            elif t == "float":
                fmt = "%f"
            else:
                fmt = "%s"
            cl.append(f'printf("{fmt}\\n", {inner});')
        else:
            cl.append(f'printf("%d\\n", {inner});')


    # ASSIGNMENT
    elif "=" in l:
        var = l.split("=")[0].strip() # Extract variable name (left side of assignment)
        val = l.split("=", 1)[1].strip() # Extract value/expression (right side of assignment)
        # ---------- INCREMENT / DECREMENT OPTIMIZATION ----------
        # Handles: x = x + 1  →  x++
        #          x = x - 1  →  x--
        #          x += 1     →  x++
        #          x -= 1     →  x--
        #          x = x + n  →  x += n
        #          x = x - n  →  x -= n
        optimized = False # Flag to track if optimization was applied
        if l.startswith(var + " +=") or l.startswith(var + " -="):
            op = "+=" if "+=" in l else "-=" # Determine if it's an increment or decrement operation
            amount = l.split(op, 1)[1].strip() # Extract the amount being added or subtracted
            if amount == "1":
                cl.append(f'{var}{"++"}' + ';') if op == "+=" else cl.append(f'{var}{"--"}' + ';')
            else:
                cl.append(f'{var} {op} {amount};') # Generate the appropriate C code for the increment/decrement operation
            optimized = True # conversion already handle
        elif val.startswith(var + " +") or val.startswith(var + " -"):
            if val.startswith(var + " +"):
                amount = val[len(var) + 2:].strip()
                if amount == "1":
                    cl.append(f'{var}++;')
                else:
                    cl.append(f'{var} += {amount};')
            else:
                amount = val[len(var) + 2:].strip()
                if amount == "1":
                    cl.append(f'{var}--;')
                else:
                    cl.append(f'{var} -= {amount};')
            optimized = True
        if not optimized:
            t = get_type(val)
            if var in vt:
                if t == "char*":
                    val = val.replace("'", '"')
                cl.append(f'{var} = {val};')
            else:
                vt[var] = t
                if t == "char*":
                    val = val.replace("'", '"')
                cl.append(f'{t} {var} = {val};')




# Close any remaining open blocks
while len(indent_stack) > 1:
    cl.append("}")
    indent_stack.pop()



# Output generated C code
if not stopped:
    print("\nGenerated C Code:\n")
    print("#include <stdio.h>")
    print()
    print("int main()")
    print("{")
    for line in cl:
        print("    " + line)
    print()
    print("    return 0;")
    print("}")

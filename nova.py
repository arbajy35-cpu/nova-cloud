import sys

variables = {}
functions = {}

def process_text(line):
    print(line[5:])

def process_set(line):
    try:
        parts = line[4:].split("=")
        var = parts[0].strip()
        val = parts[1].strip()
        variables[var] = val
    except:
        print("Error: Invalid set command")

def process_if(line, lines_iter):
    try:
        condition = line[3:].strip()
        var_name, op, value = condition.split()
        var_value = variables.get(var_name, "0")
        exec_condition = f"{var_value} {op} {value}"
        result = eval(exec_condition)

        # Read next lines until we hit else or end of if block
        true_line = None
        false_line = None
        while True:
            next_line = next(lines_iter).strip()
            if next_line == "" or next_line.startswith("#"):
                continue
            if next_line.startswith("else"):
                false_line = next(lines_iter).strip()
                break
            else:
                true_line = next_line
                break

        if result:
            process_line(true_line, lines_iter)
        else:
            process_line(false_line, lines_iter)

    except StopIteration:
        pass
    except Exception as e:
        print("Error in if:", e)

def process_func(line, lines_iter):
    try:
        func_name = line[4:].strip()
        body = []
        while True:
            next_line = next(lines_iter).strip()
            if next_line == "end":
                break
            if not next_line.startswith("#") and next_line != "":
                body.append(next_line)
        functions[func_name] = body
    except Exception as e:
        print("Error in def:", e)

def run_func(func_name):
    if func_name in functions:
        for line in functions[func_name]:
            process_line(line, None)

def process_line(line, lines_iter=None):
    if line == "" or line.startswith("#"):
        return  # ignore blank lines & comments
    if line.startswith("text "):
        process_text(line)
    elif line.startswith("set "):
        process_set(line)
    elif line.startswith("if ") and lines_iter is not None:
        process_if(line, lines_iter)
    elif line.startswith("def ") and lines_iter is not None:
        process_func(line, lines_iter)
    elif line.startswith("call "):
        func_name = line[5:].strip()
        run_func(func_name)
    else:
        # Unknown command print only if not else
        if line != "else":
            print("Unknown command:", line)

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    file = sys.argv[1]
    with open(file, "r") as f:
        lines_iter = iter(f)
        for line in lines_iter:
            process_line(line.strip(), lines_iter)

import sys
import operator

# ==================
# GLOBAL STATE
# ==================
variables = {}
functions = {}
return_flag = False
return_value = None

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv
}

CMP = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">":  lambda a, b: a > b,
    "<":  lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b
}

# ==================
# HELPERS
# ==================
def is_number(x):
    try:
        int(x)
        return True
    except:
        return False

def get_value(token):
    # String methods support
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    if "." in token:  # string methods: name.upper() etc
        var, method = token.split(".", 1)
        val = variables.get(var, var)
        if method.startswith("upper()"):
            return str(val).upper()
        if method.startswith("lower()"):
            return str(val).lower()
        if method.startswith("len()"):
            return len(str(val))
        return val
    if token in variables:
        return variables[token]
    if is_number(token):
        return int(token)
    return token

def eval_math(expr):
    # Basic math parser (left-to-right)
    parts = expr.split()
    val = get_value(parts[0])
    i = 1
    while i < len(parts):
        op = OPS[parts[i]]
        nxt = get_value(parts[i + 1])
        val = op(val, nxt)
        i += 2
    return val

# ==================
# COMMANDS
# ==================
def cmd_text(args):
    parts = args.split()
    out = [str(get_value(p)) for p in parts]
    print(" ".join(out))

def cmd_set(args):
    var, val = args.split("=", 1)
    var = var.strip()
    val = val.strip()
    # Math support
    if any(o in val for o in OPS):
        variables[var] = eval_math(val)
    else:
        variables[var] = get_value(val)

def cmd_if(condition, lines, i):
    global return_flag
    var, op, val = condition.split()
    left = get_value(var)
    right = get_value(val)

    if op not in CMP:
        raise Exception("Invalid comparison operator")

    result = CMP[op](left, right)
    true_block = []
    false_block = []
    block = true_block

    i += 1
    while i < len(lines):
        line = lines[i]
        if line == "else":
            block = false_block
        elif line == "end":
            break
        else:
            block.append(line)
        i += 1

    run_lines(true_block if result else false_block)
    if return_flag:
        return i
    return i

def cmd_loop(count, lines, i):
    global return_flag
    body = []
    i += 1
    while lines[i] != "end":
        body.append(lines[i])
        i += 1

    for _ in range(int(get_value(count))):
        run_lines(body)
        if return_flag:
            break
    return i

def cmd_func(header, lines, i):
    parts = header.split()
    name = parts[1]
    params = parts[2:]
    body = []

    i += 1
    while lines[i] != "end":
        body.append(lines[i])
        i += 1

    functions[name] = (params, body)
    return i

def cmd_call(args):
    global return_flag, return_value
    parts = args.split()
    name = parts[0]
    values = parts[1:]

    if name not in functions:
        raise Exception(f"Function '{name}' not found")

    params, body = functions[name]
    backup = variables.copy()
    return_flag = False
    return_value = None

    for p, v in zip(params, values):
        variables[p] = get_value(v)

    run_lines(body)

    # capture return
    ret = return_value
    return_flag = False
    return_value = None

    variables.clear()
    variables.update(backup)
    return ret

def cmd_return(arg):
    global return_flag, return_value
    return_value = get_value(arg)
    return_flag = True

# ==================
# RUNNER
# ==================
def run_lines(lines):
    global return_flag
    i = 0
    while i < len(lines):
        try:
            line = lines[i]
            if line == "" or line.startswith("#"):
                i += 1
                continue

            if return_flag:
                break

            if line.startswith("text "):
                cmd_text(line[5:])
            elif line.startswith("set "):
                cmd_set(line[4:])
            elif line.startswith("if "):
                i = cmd_if(line[3:], lines, i)
            elif line.startswith("loop "):
                i = cmd_loop(line[5:], lines, i)
            elif line.startswith("func "):
                i = cmd_func(line, lines, i)
            elif line.startswith("call "):
                ret = cmd_call(line[5:])
                # optional: allow inline assignment
                if "set " in line:
                    parts = line.split("=")
                    var = parts[0].replace("set","").strip()
                    variables[var] = ret
            elif line.startswith("return "):
                cmd_return(line[7:])
            else:
                raise Exception(f"Unknown command -> {line}")

        except Exception as e:
            print(f"🔥 NovaError at line {i + 1}: {e}")
            return

        i += 1

# ==================
# MAIN
# ==================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nova.py file.nova")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        code = [line.strip() for line in f]

    print("🔥 Nova v3.1 Engine Started")
    run_lines(code)

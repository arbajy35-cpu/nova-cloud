import sys

file = sys.argv[1]  # file name argument

with open(file, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("text "):
            print(line[5:])
        else:
            print("Unknown command:", line)

import csv
import sys

with open(sys.argv[1]) as f:
    reader = csv.reader(f, delimiter="|")
    print([len(line) for line in reader])

import sys
import os

with open('credentials.txt', 'r') as file:
    lines = file.readlines()
    code_path = lines[4].strip()

sys.path.append(os.path.abspath(code_path))
from common import *

make_random_lists()
result = my_random_lists_html()
print(result)

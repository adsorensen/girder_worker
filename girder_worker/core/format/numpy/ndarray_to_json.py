import json
import numpy as np
import pickle

#output = pickle.dumps(input.tolist())
#output = pickle.dumps(input, protocol=0)
output = json.dumps(input.tolist())

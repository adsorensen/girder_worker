import json
import numpy as np
#import simplejson
from json_tricks.np import dump, dumps, load, loads
#output = json.dumps(input)

#output = simplejson.dumps(input.tolist())

output = json.dumps(input.tolist())

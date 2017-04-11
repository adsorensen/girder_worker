import celery

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'add numpy arrays',
    'inputs': [
        {'name': 'a', 'type': 'string', 'format': 'text'},
        {'name': 'b', 'type': 'string', 'format': 'text'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'numpy', 'format': 'ndarray'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': ('import numpy as np; data = np.loadtxt(a); '
    'data2 = np.loadtxt(b); '
    #'data = data.astype(int); data2 = data2.astype(int);'
    'c = data + data2; f = isinstance(c, np.ndarray);'),
    'mode': 'python'
}

task2 = {
    'name': 'add numpy arrays',
    'inputs': [
        {'name': 'a', 'type': 'string', 'format': 'text'},
        {'name': 'b', 'type': 'string', 'format': 'text'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'numpy', 'format': 'ndarray'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': ('import numpy as np; data = np.loadtxt(a); '
    'data2 = np.loadtxt(b); '
    'data = data.astype(int); data2 = data2.astype(int);'
    'c = data + data2 + data; f = isinstance(c, np.ndarray);'),
    'mode': 'python'
}

output = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'text', 'data': "/home/adam/Downloads/array.txt"},
        'b': {'format': 'text', 'data': "/home/adam/Downloads/array2.txt"}
    },
    'outputs': {
        'c': {'format': 'json', 'uri': 'file://output.json'},
        'f': {'format': 'json', 'uri': 'file://output.json'}
    }
},)

output2 = celeryapp.send_task('girder_worker.run', [task2], {
    'inputs': {
        'a': {'format': 'text', 'data': "/home/adam/Downloads/array.txt"},
        'b': {'format': 'text', 'data': "/home/adam/Downloads/array2.txt"}
    },
    'outputs': {
        'c': {'format': 'json', 'uri': 'file://output2.json'},
        'f': {'format': 'json', 'uri': 'file://output2.json'}
    }
}, serializer='pickle')

#serializer='pickle'
print output.get()
print output2.get()

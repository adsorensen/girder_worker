import celery
import numpy as np
import scipy

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/',
    task_serializer='pickle',
    result_serializer='pickle',
    serializer='pickle')

task = {
    'name': 'add_numpy_arrays',
    'inputs': [
        {'name': 'a', 'type': 'numpy', 'format': 'ndarray'},
        {'name': 'b', 'type': 'numpy', 'format': 'ndarray'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'numpy', 'format': 'ndarray'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': 'import numpy as np; c = a + b; f = isinstance(c, np.ndarray)',
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'ndarray', 'data': np.array([[1, 2, 3], [4, 5, 6]])},
        'b': {'format': 'ndarray', 'data': np.array([[10, 20, 30], [40, 50, 60]])}
    },
    'outputs': {
        'c': {'format': 'json', 'uri': 'file://output.json'},
        'f': {'format': 'boolean', 'uri': 'file://output.json'}
    }
}, result_serializer='pickle', serializer='pickle')

print async_result.get()

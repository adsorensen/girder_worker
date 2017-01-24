import celery
import numpy
import scipy

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'append_tables',
    'inputs': [
        {'name': 'a', 'type': 'numpy', 'format': 'numpy.ndarray'},
        {'name': 'b', 'type': 'numpy', 'format': 'numpy.ndarray'}
    ],
    'outputs': [{'name': 'c', 'type': 'numpy', 'format': 'numpy.ndarray'}],
    'script': 'c = a + b',
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'numpy.ndarray', 'data': ([1, 2, 3], [4, 5, 6])},
        'b': {'format': 'numpy.ndarray', 'data': ([2, 4, 6], [1, 3, 5])}
    },
    'outputs': {
        'c': {'format': 'numpy.ndarray', 'uri': 'file://output.json'}
    }
})

print async_result.get()

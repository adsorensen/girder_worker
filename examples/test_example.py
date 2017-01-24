import celery

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'int test',
    'inputs': [
        {'name': 'a', 'type': 'number_list', 'format': 'number_list'},
        {'name': 'b', 'type': 'number_list', 'format': 'number_list'}
    ],
    'outputs': [{'name': 'c', 'type': 'number_list', 'format': 'number_list'}],
    'script': 'c = a + b',
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'number_list', 'data': [10, 20, 30]},
        'b': {'format': 'number_list', 'data': [1, 2, 3]}
    },
    'outputs': {
        'c': {'format': 'number_list', 'uri': 'file://output.json'}
    }
})

print async_result.get()

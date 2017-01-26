import celery

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'number list test',
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

task2 = {
    'name': 'txt test',
    'inputs': [
        {'name': 'a', 'type': 'string', 'format': 'string'},
        {'name': 'b', 'type': 'string', 'format': 'string'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'string', 'format': 'string'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': 'c = a + b; f = isinstance(a, str)',
    'mode': 'python'
}

async_result2 = celeryapp.send_task('girder_worker.run', [task2], {
    'inputs': {
        'a': {'format': 'string', 'data': "hello "},
        'b': {'format': 'string', 'data': "world"}
    },
    'outputs': {
        'c': {'format': 'string', 'uri': 'file://output.json'},
        'f': {'format': 'boolean', 'uri': 'file://output.json'}
    }
})

#print async_result.get()
print async_result2.get()

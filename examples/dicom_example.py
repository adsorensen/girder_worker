import celery
import dicom as di

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'dicom_example_test',
    'inputs': [
        {'name': 'a', 'type': 'string', 'format': 'string'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'pydicom', 'format': 'dataset.FileDataset'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': 'import dicom as di; c = di.read_file(a); f = isinstance(c, di.dataset.FileDataset)',
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'string', 'data': '/home/adam/Downloads/test.dcm' }
    },
    'outputs': {
        'c': {'format': 'dataset.FileDataset', 'uri': 'file://output.json'},
        'f': {'format': 'boolean', 'uri': 'file://output.json'}
    }
}, serializer='pickle')

print async_result.get()

import celery
import dicom as di

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'dicom_example_test',
    'inputs': [
        {'name': 'a', 'type': 'pydicom', 'format': 'dataset.FileDataset'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'string', 'format': 'string'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': ('import dicom as di; a.ContentDate = \'200\';'
        ' c = a.ContentDate; b = a; f = isinstance(b, di.dataset.FileDataset)'),
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'dataset.FileDataset', 'data': di.read_file("/home/adam/Downloads/test.dcm") }
    },
    'outputs': {
        'c': {'format': 'string', 'uri': 'file://output.json'},
        'f': {'format': 'boolean', 'uri': 'file://output.json'}
    }
}, serializer='pickle')

print async_result.get()

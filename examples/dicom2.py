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
        {'name': 'c', 'type': 'numpy', 'format': 'ndarray'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'},
        {'name': 'ff', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': ('import dicom as di; import numpy as np; c = a.pixel_array;'
        ' b = a; f = isinstance(b, di.dataset.FileDataset);'
        'ff = isinstance(c, np.ndarray)'),
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'dataset.FileDataset', 'data': di.read_file("/home/adam/Downloads/test.dcm") }
    },
    'outputs': {
        'c': {'format': 'json', 'uri': 'file://output.json'},
        'f': {'format': 'boolean', 'uri': 'file://output.json'},
        'ff': {'format': 'boolean', 'uri': 'file://output.json'}
    }
}, serializer='pickle')

print async_result.get()

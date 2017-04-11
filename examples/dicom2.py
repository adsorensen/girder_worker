import celery
import dicom as di

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'dicom_example_test',
    'inputs': [
        {'name': 'a', 'type': 'string', 'format': 'text'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'numpy', 'format': 'ndarray'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'},
        {'name': 'ff', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': ('import dicom as di; import numpy as np; aa = di.read_file(a); c = aa.pixel_array;'
        ' b = aa; f = isinstance(b, di.dataset.FileDataset);'
        'ff = isinstance(c, np.ndarray); '
        'c = np.array([1, 2]);'
        ),
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'text', 'data': "/home/adam/Downloads/test.dcm" }
    },
    'outputs': {
        'c': {'format': 'json', 'uri': 'file://output.json'},
        'f': {'format': 'boolean', 'uri': 'file://output.json'},
        'ff': {'format': 'boolean', 'uri': 'file://output.json'}
    }
}, serializer='pickle')

print async_result.get()

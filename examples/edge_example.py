import celery
import numpy as np
import scipy
import matplotlib.pyplot as plt

celeryapp = celery.Celery(
    'girder_worker',
    backend='amqp://guest@localhost/',
    broker='amqp://guest@localhost/')

task = {
    'name': 'edge detection test',
    'inputs': [
        {'name': 'a', 'type': 'string', 'format': 'text'}
    ],
    'outputs': [
        {'name': 'c', 'type': 'numpy', 'format': 'ndarray'},
        {'name': 'f', 'type': 'boolean', 'format': 'boolean'}
    ],
    'script': ('import numpy as np; import scipy; import matplotlib.pyplot as plt; from skimage import feature; '
    'im = scipy.misc.imread(a); c = np.mean(im[:,:,0:2],2); edges1 = feature.canny(c); '
    'edges2 = feature.canny(c, sigma=4); f = isinstance(c, np.ndarray); '
    'fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(8, 4), sharex=True, sharey=True); '
    'ax1.imshow(gryim, cmap=plt.cm.jet); ax1.axis(\'off\'); ax1.set_title(\'original\'); '
    'ax2.imshow(edges1, cmap=plt.cm.gray); ax2.axis(\'off\'); ax2.set_title(\'what\'); '
    'ax3.imshow(edges2, cmap=plt.cm.gray); ax3.axis(\'off\'); ax3.set_title(\'huh\') '
    'fig.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9, bottom=0.02, left=0.02, right=0.98); '
    'plt.show(); ') ,
    'mode': 'python'
}

async_result = celeryapp.send_task('girder_worker.run', [task], {
    'inputs': {
        'a': {'format': 'text', 'data': "/home/adam/Downloads/apple.png"}
    },
    'outputs': {
        'c': {'format': 'json', 'uri': 'file://output.json'},
        'f': {'format': 'boolean', 'uri': 'file://output.json'}
    }
}, serializer='pickle')

print async_result.get()

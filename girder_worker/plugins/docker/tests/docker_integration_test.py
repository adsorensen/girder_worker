import ConfigParser
import os
import shutil
import six
import stat
import sys
import unittest
import docker

import girder_worker
from girder_worker.core import run, io

test_image = 'girder/girder_worker_test:latest'


def setUpModule():
    global _tmp
    _tmp = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '_tmp', 'docker')
    girder_worker.config.set('girder_worker', 'tmp_root', _tmp)
    try:
        girder_worker.config.add_section('docker')
    except ConfigParser.DuplicateSectionError:
        pass

    if os.path.isdir(_tmp):
        shutil.rmtree(_tmp)


def tearDownModule():
    if os.path.isdir(_tmp):
        shutil.rmtree(_tmp)


class TestDockerMode(unittest.TestCase):
    """
    Integration tests that call out to docker rather than using mocks.
    """

    def setUp(self):
        self._test_message = 'Hello from girder_worker!'
        self._tmp = os.path.join(_tmp, 'testing')
        if not os.path.isdir(self._tmp):
            os.makedirs(self._tmp)

    def tearDown(self):
        shutil.rmtree(self._tmp)

    def testDockerModeStdio(self):
        """
        Test writing to stdout.
        """

        task = {
            'mode': 'docker',
            'docker_image': test_image,
            'pull_image': True,
            'container_args': ['$input{test_mode}', '$input{message}'],
            'inputs': [{
                'id': 'test_mode',
                'name': '',
                'format': 'string',
                'type': 'string'
            }, {
                'id': 'message',
                'name': '',
                'format': 'string',
                'type': 'string'
            }],
            'outputs': []
        }

        inputs = {
            'test_mode': {
                'format': 'string',
                'data': 'stdio'
            },
            'message': {
                'format': 'string',
                'data': self._test_message
            }
        }

        _old = sys.stdout
        stdout_captor = six.StringIO()
        sys.stdout = stdout_captor
        run(
            task, inputs=inputs, _tempdir=self._tmp, cleanup=True, validate=False,
            auto_convert=False)
        sys.stdout = _old
        lines = stdout_captor.getvalue().splitlines()
        self.assertEqual(lines[-1], self._test_message)

        task = {
            'mode': 'docker',
            'docker_image': test_image,
            'pull_image': True,
            'container_args': ['$input{test_mode}', '$input{message}'],
            'inputs': [{
                'id': 'test_mode',
                'name': '',
                'format': 'string',
                'type': 'string'
            }, {
                'id': 'message',
                'name': '',
                'format': 'string',
                'type': 'string'
            }],
            'outputs': []
        }
        _old = sys.stdout
        stdout_captor = six.StringIO()
        sys.stdout = stdout_captor
        run(
            task, inputs=inputs, cleanup=True, validate=False,
            auto_convert=False)
        sys.stdout = _old

        lines = stdout_captor.getvalue().splitlines()
        self.assertEqual(lines[-1], self._test_message)

        # Test _stdout
        task['outputs'] = [{
            'id': '_stdout',
            'format': 'string',
            'type': 'string'
        }]

        _old = sys.stdout
        stdout_captor = six.StringIO()
        sys.stdout = stdout_captor
        out = run(
            task, inputs=inputs, cleanup=False, validate=False,
            auto_convert=False)
        sys.stdout = _old

        lines = stdout_captor.getvalue().splitlines()
        message = '%s\r\n' % self._test_message
        self.assertTrue(message not in lines)
        self.assertEqual(out['_stdout']['data'], message)

    def testDockerModeOutputPipes(self):
        """
        Test writing to named output pipe.
        """
        task = {
            'mode': 'docker',
            'docker_image': test_image,
            'pull_image': True,
            'container_args': ['$input{test_mode}', '$input{message}'],
            'inputs': [{
                'id': 'test_mode',
                'name': '',
                'format': 'string',
                'type': 'string'
            }, {
                'id': 'message',
                'name': '',
                'format': 'string',
                'type': 'string'
            }],
            'outputs': [{
                'id': 'output_pipe',
                'format': 'text',
                'type': 'string',
                'target': 'filepath',
                'stream': True
            }]
        }

        outputs = {
            'output_pipe': {
                'mode': 'capture'
            }
        }

        inputs = {
            'test_mode': {
                'format': 'string',
                'data': 'output_pipe'
            },
            'message': {
                'format': 'string',
                'data': self._test_message,
            }
        }

        class CaptureAdapter(girder_worker.core.utils.StreamPushAdapter):
            message = ''

            def write(self, buf):
                CaptureAdapter.message += buf

        # Mock out the stream adapter
        io.register_stream_push_adapter('capture', CaptureAdapter)

        outputs = run(
            task, inputs=inputs, outputs=outputs, _tempdir=self._tmp, cleanup=False)

        # Make sure pipe was created inside the temp dir
        pipe = os.path.join(self._tmp, 'output_pipe')
        self.assertTrue(os.path.exists(pipe))
        self.assertTrue(stat.S_ISFIFO(os.stat(pipe).st_mode))
        # Make use piped output was write to adapter
        self.assertEqual(CaptureAdapter.message, self._test_message)

    def testDockerModeInputPipes(self):
        """
        Test reading from named output pipe.
        """

        task = {
            'mode': 'docker',
            'docker_image': test_image,
            'pull_image': True,
            'container_args': ['$input{test_mode}', '$input{message}'],
            'inputs': [{
                'id': 'test_mode',
                'name': '',
                'format': 'string',
                'type': 'string'
            }, {
                'id': 'message',
                'name': '',
                'format': 'string',
                'type': 'string'
            }, {
                'id': 'input_pipe',
                'format': 'string',
                'type': 'string',
                'target': 'filepath',
                'stream': True
            }],
            'outputs': [{
                'id': '_stdout',
                'format': 'string',
                'type': 'string'
            }]
        }

        inputs = {
            'test_mode': {
                'format': 'string',
                'data': 'input_pipe'
            },
            'message': {
                'format': 'string',
                'data': self._test_message
            },
            'input_pipe': {
                'mode': 'static',
                'data': self._test_message
            }
        }

        # Mock out the stream adapter
        class StaticAdapter(girder_worker.core.utils.StreamFetchAdapter):

            def __init__(self, spec):
                self._data = six.BytesIO(spec['data'])

            def read(self, buf_len):
                return self._data.read(buf_len)

        io.register_stream_fetch_adapter('static', StaticAdapter)

        output = run(
            task, inputs=inputs, outputs={}, _tempdir=self._tmp, cleanup=True)

        # Make sure pipe was created inside the temp dir
        pipe = os.path.join(self._tmp, 'input_pipe')
        self.assertTrue(os.path.exists(pipe))
        self.assertTrue(stat.S_ISFIFO(os.stat(pipe).st_mode))
        self.assertEqual(output['_stdout']['data'].rstrip(), self._test_message)

    def testDockerModeRemoveContainer(self):
        """
        Test automatic container removal
        """
        task = {
            'mode': 'docker',
            'docker_image': test_image,
            'pull_image': True,
            'container_args': ['$input{test_mode}', '$input{message}'],
            'inputs': [{
                'id': 'test_mode',
                'name': '',
                'format': 'string',
                'type': 'string'
            }, {
                'id': 'message',
                'name': '',
                'format': 'string',
                'type': 'string'
            }],
            'outputs': []
        }

        inputs = {
            'test_mode': {
                'format': 'string',
                'data': 'stdio'
            },
            'message': {
                'format': 'string',
                'data': self._test_message
            }
        }

        docker_client = docker.from_env()
        containers = docker_client.containers.list(limit=1)
        last_container_id = containers[0].id if len(containers) > 0 else None

        run(
            task, inputs=inputs, _tempdir=self._tmp, cleanup=True, validate=False,
            auto_convert=False)

        def _fetch_new_containers(last_container_id):
            if last_container_id:
                filters = {
                    'since': last_container_id
                }
                new_containers = docker_client.containers.list(all=True, filters=filters)
            else:
                new_containers = docker_client.containers.list(all=True)

            return new_containers

        new_containers = _fetch_new_containers(last_container_id)
        # Now assert that the container was removed
        self.assertEqual(len(new_containers), 0)

        # Now confirm that the container doesn't get removed if we set
        # _rm_container = False
        girder_worker.config.set('docker', 'gc', 'True')
        # Stop GC removing anything
        girder_worker.config.set('docker', 'cache_timeout', str(sys.maxint))

        task['_rm_container'] = False
        run(
            task, inputs=inputs, _tempdir=self._tmp, cleanup=True, validate=False,
            auto_convert=False, _rm_containers=False)
        new_containers = _fetch_new_containers(last_container_id)
        self.assertEqual(len(new_containers), 1)
        self.assertEqual(new_containers[0].attrs.get('Config', {})['Image'], test_image)
        # Clean it up
        new_containers[0].remove()

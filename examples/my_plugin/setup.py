from setuptools import setup

setup(name='first_plugin',
      version='0.0.0',
      description='Testing a custom plugin for girder worker',
      author='Adam Sorensen',
      author_email='adam.sorensen455@gmail.com',
      license='Apache v2',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: Apache Software License'
          'Topic :: Scientific/Engineering :: GIS',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python'
      ],
      entry_points={
          'girder_worker_plugins': [
              'first_plugin = first_plugin:First_Plugin',
          ]
      },
      packages=['first_plugin'],
      zip_safe=False)

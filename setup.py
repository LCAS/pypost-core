""" Setup Module for the Robot Learning Toolbox.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # TODO change credentials
    name='PyPoST',
    version='0.0.1',
    author='Gerhard Neumann',
    author_email='geri@robot-learning.de',
    description='Python Policy Search Toolbox',
    long_description=long_description,
    url='http://www.ausy.tu-darmstadt.de',
    license='BSD',

    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],

    #keywords='reinforcement learning',

    # pypost package is found in subdirectory src/
    package_dir={'': 'src'},

    # TODO use find_packages instead of manual listing.
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    namespace_packages=['pypost'],
    packages=['pypost.common',
              'pypost.data',
              'pypost.mappings',
              'pypost.envs',
              'pypost.banditEnvironments',
              'pypost.experiments',
              'pypost.learner',
              'pypost.parameterOptimization',
              'pypost.supervisedLearner',
              'pypost.optimizer',
              'pypost.sampler',
              'pypost.initialSampler',
              'pypost.tests',
	      'pypost.tutorials.data',
	      'pypost.tutorials.experiments',
	      'pypost.tutorials.data',
              'pypost.tutorials.mappings',
              'pypost.tutorials.optimizer',
              'pypost.tutorials.sampler',
              'pypost.tutorials.settings'
              ],
    # TODO Fix error concerning pyyaml directory and uncomment
    # install_requires=['pyyaml', 'scipy']
    # TODO Convert to Python Wheels for security reasons
)


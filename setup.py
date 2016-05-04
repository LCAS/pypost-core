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
    name='RobotLearningToolbox',
    version='0.0.1',
    author='Gerhard Neumann',
    author_email='geri@robot-learning.de',
    description='Reinforcement Learning Toolbox written in Python.',
    long_description=long_description,
    url='http://www.ausy.tu-darmstadt.de',
    license='unknown',

    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],

    #keywords='reinforcement learning',

    # rlt package is found in subdirectory src/
    package_dir={'':'src'},

    # TODO use find_packages instead of manual listing.
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    packages=['rlt',
              'rlt.common',
              'rlt.data',
              'rlt.distributions',
              'rlt.distributions.gaussian',
              'rlt.environments',
              'rlt.environments.banditEnvironments',
              'rlt.evaluator',
              'rlt.evaluator.supervisedLearning',
              'rlt.examples',
              'rlt.examples.stochasticSearch',
              'rlt.examples.stochasticSearch.rosenbrock',
              'rlt.experiments',
              'rlt.functions',
              'rlt.learner',
              'rlt.learner.episodicRL',
              'rlt.learner.parameterOptimization',
              'rlt.learner.weightedML',
              'rlt.parametricModels',
              'rlt.policy',
              'rlt.sampler',
              'rlt.sampler.isActiveSampler',
              ],
    # TODO Fix error concerning pyyaml directory and uncomment
    # install_requires=['pyyaml', 'scipy']
    # TODO Convert to Python Wheels for security reasons
)


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

    # pypost package is found in subdirectory src/
    package_dir={'':'src'},

    # TODO use find_packages instead of manual listing.
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    packages=['pypost',
              'pypost.common',
              'pypost.data',
              'pypost.distributions',
              'pypost.distributions.gaussian',
              'pypost.environments',
              'pypost.environments.banditEnvironments',
              'pypost.evaluator',
              'pypost.evaluator.supervisedLearning',
              'pypost.examples',
              'pypost.examples.stochasticSearch',
              'pypost.examples.stochasticSearch.rosenbrock',
              'pypost.experiments',
              'pypost.functions',
              'pypost.learner',
              'pypost.learner.episodicRL',
              'pypost.learner.parameterOptimization',
              'pypost.learner.weightedML',
              'pypost.parametricModels',
              'pypost.policy',
              'pypost.sampler',
              'pypost.sampler.isActiveSampler',
              'pypost.sampler.initialSampler',
              'pypost.tests'
              ],
    # TODO Fix error concerning pyyaml directory and uncomment
    # install_requires=['pyyaml', 'scipy']
    # TODO Convert to Python Wheels for security reasons
)


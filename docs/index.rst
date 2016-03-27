.. Robot Learning Toolbox documentation master file, created by
   sphinx-quickstart

Welcome to Robot Learning Toolbox's documentation!
==================================================

Overview
========

The toolbox is divided into folders, holding the different parts of the
toolbox:

-  ``/src`` Holds all the toolbox source code. When using the toolbox,
   you only have to import files from this directory.
-  ``/test`` Tests for all the classes in *src/*.
-  ``/tools`` Tools for quality assurance, like performance measurements
   or code coverage.
-  ``/tutorials`` Tutorials on how to use the toolbox classes,
   demonstrated on documented example code

Requirements
============

This toolbox needs to be run with **Python 3.0** or higher. In addition
the following modules are required:

- ``scipy`` -- ``pip install scipy``
- ``pyyaml`` -- ``pip install pyyaml``
- for development also ``coverage`` is needed

Usage with Eclipse
==================

The toolbox can be edited with any IDE or text editor supporting python
3.0 syntax. Here we shortly describe the setup for Eclipse.

PyDev
-----

Eclipse has no native python support therefore a python plugin is
needed, we recommend using PyDev as it is the best supported plugin for
Python. The plugin is available in the eclipse marketplace under
``Help`` -> ``Eclipse Marketplace ...`` -> search for "PyDev".

PyDev also supports script execution in eclipse itself. Most of the
console commands shown below can be executed in Eclipse, by simply
right-clicking the file and choosing "Run As" or "Debug As" in the
context menu.

Import project
--------------

Goto ``File`` -> ``Import...`` ->
``General / Existing Projects into Workspace``, choose the folder where
you stored the robot learning toolbox, select the automatically found
eclipse project and proceed with ``Next``.

Make sure to have the right python interpreter and grammar version
selected for the project. Therefore ``right-click the project`` ->
``Properties`` -> ``PyDev - Interpreter/Grammer`` and make sure to have
grammar version "3.0" and a python 3.0 interpreter selected.

Quick Start
===========

For an introduction into the toolbox it is recommended to look at the
tutorials provided in the ``tutorials/`` folder. All tutorials can be
run by navigating into the folder of the file and executing the file
with python e.g.

.. code:: bash

    cd ./tutorials/data/
    python dataManager.py

Further information on the code or how to use certain methods can be
looked up in the documentation or the corresponding tests.

For a detailed overview over the key differences and a table of MATLAB-NumPy expression equivalents, we stongly recommend to read the NumPy for Matlab users guide [1]. There also is another overview table that shows the differences between Matlab and Python in general [2].

[1] https://docs.scipy.org/doc/numpy-dev/user/numpy-for-matlab-users.html

[2] http://mathesaurus.sourceforge.net/matlab-numpy.html

Module Overview
===============
.. toctree::
   :glob:
   :maxdepth: 2

   *

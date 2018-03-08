# Robot Learning Toolbox
Robot Learning Toolbox written in Python. The core of the toolbox is mainly for interfacing the data and doing experiments. 

=== Installation ===

Coarsely what you need to install:

- install additional packages:

sudo apt-get install python3 python3-pip python3-virtualenv 
sudo apt-get install libpng-dev libjpeg8-dev libfreetype6-dev python-dev python3-tk

- upgrade pip 

pip install --upgrade

- install virtualenvwrapper 

sudo pip install virtualenvwrapper

- Create a virtual environment:

create a folder for your virtual environments (mkdir ~/virtenv)
add the following lines to .bashrc

# virtualenv
export WORKON_HOME=~/virtenv
source /usr/local/bin/virtualenvwrapper.sh


* restart terminal or source .bashrc
* create a virtual environment with mkvirtualenv -p /usr/bin/python3 pyposEnv
* after the virtual environment has been created it is automatically activated (the prompt shows the name of the environment in parentheses). To deactivate the environment enter deactivate, to activate it again enter workon pyposEnv.

- Install the necessary packages inside the virtual environment:
* If the environment has to be activated.
* Install the following packages with pip install

pip install numpy scipy bpython pudb pyyaml matplotlib matplotlib2tikz

* Install jupyter with virtualenv
pip install jupyter
python -m ipykernel install --user --name=pyposEnv

* Install tensorflow (see tensorflow documentation)

=== Documentation ===

For documentation, have a look at the `docs` directory.

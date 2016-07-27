# Contributing to the Robot Learning Toolbox

To keep the development of the toolbox a bit organized, we want to use **git-flow**

 + http://jeffkreeftmeijer.com/2010/why-arent-you-using-git-flow/
 + http://danielkummer.github.io/git-flow-cheatsheet/
 + https://github.com/bobthecow/git-flow-completion

To contribute to the Robot Learning Toolbox, please fork the repository and work
with your own repository.
Please use the [issue tracking](issues) for features you want to implement or bugs you want to fix.

When you want your changes to be merged into the Robot Learning Toolbox you can file a merge request.

# Git Workflow

This guide shows you how to properly use Git for collaboration projects. If you have not, please read the [getting started guide](https://ias-group.slack.com/files/simone/F1HMNGMDG/Getting_started_with_Git.md).
In order to keep the original repository clean, you have to fork it into your workspace. There, you can do whatever you want and as soon as your modifications are stable, you ask for a merge to the original repository. Below, there is a description of the workflow with the `sl` repository as example.

## Setup
---------

**Fork** the repository. [Open it](https://git.ias.informatik.tu-darmstadt.de/sl/sl) and click on `fork`. You will be given the options to fork it inside the groups you belong to. 
**COPY IT TO YOUR PERSONAL WORKSPACE!** (click on your username)

**Clone** the project 

      git clone git@git.ias.informatik.tu-darmstadt.de:USERNAME/sl.git

Check the **remote**  

      git remote -v  

and you should see that both (fetch and push) hosts point to your forked project 

      origin	git@git.ias.informatik.tu-darmstadt.de:USERNAME/sl.git (fetch)
      origin	git@git.ias.informatik.tu-darmstadt.de:USERNAME/sl.git (push)

Add an **upstream** host

      git remote add upstream git@git.ias.informatik.tu-darmstadt.de:sl/sl.git

If you check the remote hosts again you will see

      origin	git@git.ias.informatik.tu-darmstadt.de:USERNAME/sl.git (fetch)
      origin	git@git.ias.informatik.tu-darmstadt.de:USERNAME/sl.git (push)
      upstream	https://git.ias.informatik.tu-darmstadt.de/sl/sl (fetch)
      upstream	https://git.ias.informatik.tu-darmstadt.de/sl/sl (push)


## Checkout
---------

Whenever you want to sync with to original repository, you have to **fetch** the branches and their respective commits from the upstream repository

      git fetch upstream 

Then, you have to **checkout** your forked local master branch

      git checkout master

Finally, **merge** the new changes

      git merge upstream/master

**KEEP THE MASTER BRANCH IN YOUR FORK CLEAN AND WORK ON YOUR OWN BRANCHES!**


## Push
---------

Let's say you are working on a `test` branch

      git checkout -b test

Once you are done with your changes, **commit** them and push to your own repository

      git push origin test

Create a **merge request** to the master in the original repository. Go to the [merge request page](https://git.ias.informatik.tu-darmstadt.de/dashboard/merge_requests), click on `New Merge Request` and select `<USERNAME>/sl` as repository. Select source (`test`) and target (`master`) and continue.
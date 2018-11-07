F5 Dashboard
============

Requirements
------------
* Ptyhon 3
* pipenv to run from your local env
* Please reference requirements.txt


Getting started
---------------
This is a simple F5 dashboard that uses F5 REST API: https://devcentral.f5.com/wiki/iControlREST.HomePage.ashx
Please be mindful using api as it may impact on production enviornment. To use this app, you must specify credentials 

To run this app from your own dev environment, you need to install the following:
From mac, make sure you have homebrew installed
`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Once homebrew is installed, download/install the following:
`brew install pipenv`

Use the following commands to run in as dev. environment:

```
~ $ cd f5dashboard
~ /f5dashboard $ pipenv shell
~ /f5dashboard $ pip install -r requiremetns.txt
~ /f5dashboard $ cd src/
~ /f5dashboard $ ./run.sh
```

By default, it will run flask from localhost, port 5010


Running F5 dashboard in docker from mac
---------------------------------------
Assuming you alredy have access to F5
1. Clone this repository
2. Add helper under src/helper
3. Add below information under src/helper

```
export USERID=<Userid from F5>
export PASSWD=<password from F5>
export AUTOMATION_PWD=<see @tkim>
``` 

4. From git repository, run below command
`docker-compose up -d`
5. Head over to http://localhost:5010


Running F5 dashboard in docker from Windows
-------------------------------------------
0. Assume that you already have git installed in Windows. This is to download this repository: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
1. Download the Docker CE (Community Edition): https://store.docker.com/editions/community/docker-ce-desktop-windows
2. Once the docker is installed, it will logout from the machine
3. Open Powershell command and try typing 'docker' to see if you get results
4. Copy 'helper' file to src of the repository. Ex. If the repo is located under C:\Users\thoma\git\ccc\sre\f5dashboard, place 'helper' file C:\Users\thoma\git\ccc\sre\f5dashboard\src\
4. Head over to git repository and run 'docker-compose up'

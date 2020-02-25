# Automated-CTF-Flag-Submitter
This automated flag submitter can automatically run your exploit, every tick, for the swpag client or it can run exploits at a given time interval and submit them given your commands. It enables you to send updates to a slack channel as well 

# Arguments
This scripts give you a lot of options to enable this script to work for you and your team in whatever way you'd like so you can get back to hacking.
### Required:
* file: This is the path to the file that either links a service to a different file (if running swpag) or is just the path to the file that contains the commands to send over to the victim
* logFile: Where to write logs of the flag submissions to. Defaults to flagLogs.txt
* swpagClient: Are you using the swpag client? Defaults to True.
### Optional:
* ignoreHost: Did you make an ally with a team? Use this flag to skip over them when capturing flags
* slackToken: Get your [slack api token](https://api.slack.com/legacy/custom-integrations/legacy-tokens) to submit flag updates to your slack channel. If you give the slack channel arg, you must also give this arg for slack updates to work.
* slackChannel: The name of the slack channel to send updates to. If you give the slack token arg, you must also give this arg for slack updates to work.
### SWPAG Users:
* teamToken (Only for swpag users): Your team token to submit flags
* teampIp (Only for swpag users): Your team ip to submit flags
### Other Users:
* hosts (Only for non-swpag users): Give a list of all the hosts, separated by a comma to attack. For example: 10.0.0.2,10.0.0.1
* sleep (Only for non-swpag users): Give the amount of time (in minutes) that a tick lasts. Only needed for non-swpag users.

You can also view all of this by running:
```
python3 submitFlags.py --help
```

# How to Run
## SWPAG Users
To run the program, you will run the command:
```
python3 submitFlags.py --file <path directory to file1> --teamIp <team ip> --teamToken <team token>
```
But first, you have to create file1, which is a file that links the service name to the file with the actual exploit.
The file will look like this:
```
service1!EXPLOITFILENAME!/path/to/exploit/commands.txt
service2!EXPLOITFILENAME!/path/to/exploit/commands2.txt
service3!EXPLOITFILENAME!/path/to/exploit/commands3.txt
[...]
```
Then your commands.txt files will be the commands you were running against the service to get the exploit. For example:
```
2
d
l
s
cat $(ls *) | grep FLG_
```
The program will loop through these commands, sleeping for .5 seconds to allow the service to respond, and then read the output
and submit the flag using swpag_client. It will log the output and notify you over slack (if slack channel and token are given).

It will run these exploits every tick for every service you list in file1 to all targets (except if you put a host to ignore).

## Other Users
```
python3 submitFlags.py --file <path directory to commands to run> --sleep 3 --swpagClient False
```
# Authors
* [Stephanie Hingtgen](https://github.com/stephanieengelhardt)
* [Matthew Calcote](https://github.com/mcalcote) 

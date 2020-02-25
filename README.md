# Automated-CTF-Flag-Submitter
This automated flag submitter can automatically run your exploit, every tick, for the swpag client or it can run exploits at a given time interval and submit them given your commands. It enables you to send updates to a slack channel as well 

# Arguments
This scripts give you a lot of options to enable this script to work for you and your team in whatever way you'd like so you can get back to hacking.
* --file (Required): This is the path to the file that either links a service to a different file (if running swpag) or is just the path to the file that contains the commands to send over to the victim
* --ignoreHost (Optional): Did you make an ally with a team? Use this flag to skip over them when capturing flags
* --slackToken (Optional): Get your [slack api token](https://api.slack.com/legacy/custom-integrations/legacy-tokens) to submit flag updates to your slack channel. If you give the slack channel arg, you must also give this arg for slack updates to work.
* --slackChannel (Optional): The name of the slack channel to send updates to. If you give the slack token arg, you must also give this arg for slack updates to work.
* --logFile (Default: flagLogs.txt): Where to write logs of the flag submissions to
* --swpagClient (Default: True): Are you using the swpag client?
* --teamToken (Only for swpag users): Your team token to submit flags
* --teampIp (Only for swpag users): Your team ip to submit flags
* --hosts (Only for non-swpag users): Give a list of all the hosts, separated by a comma to attack. For example: 10.0.0.2,10.0.0.1
* --sleep (Only for non-swpag users): Give the amount of time (in minutes) that a tick lasts. Only needed for non-swpag users.

You can also view all of this by running:
```
python3 submitFlags.py --help
```

# How to Run
## SWPAG Users
```
python3 submitFlags.py --file <path directory to the file that maps each service to a file> --teamIp <team ip> --teamToken <team token>
```
## Other Users
```
python3 submitFlags.py --file <path directory to commands to run> --sleep 3 --swpagClient False
```
# Authors
* [Stephanie Hingtgen](https://github.com/stephanieengelhardt)
* [Matthew Calcote](https://github.com/mcalcote) 

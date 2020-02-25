import argparse
import subprocess
import swpag_client
import re
import slack
from datetime import datetime
import time
import ssl

current_tick = 0

# Sends a message (m) to a channel (c) given a slack token (t)
def sendSlackMessage(c, t, m):
   ssl_context = ssl.create_default_context()
   ssl_context.check_hostname = False
   ssl_context.verify_mode = ssl.CERT_NONE
   client = slack.WebClient(token=t, ssl=ssl_context)
   response = client.chat_postMessage(channel=c, text=m)
   # ensure what we got back was okay
   assert response["ok"]
   assert response["message"]["text"] == m

###### THIS SECTION ALLOWS YOU TO RUN YOUR EXPLOITS USING A COMMAND FILE AND /ETC/HOSTS FOR HOSTS ##########
# Reads in command file. Ands all newlines together
def readFile(filePath):
    f = open(filePath, "r")
    command = ''
    # read through line by line and append the commands together
    for line in f:
        command += line + ' && '
    # return all but the last 3 characters (the extra ' && ' that was added on the last line)
    return command[:-3]


# Run the commands in the file in a continuous loop - sleeps at given amount
def runForever(args, commands, hosts,  teamIp, teamToken):
    # Now lets run the concatenated commands on each host, forever
    while True:
        for host in hosts:
            # Run commands
            commandArr = commands.split("!READIN")
            output = ""
            error = ""
            readIn = ""
            for command in commandArr:
                command.replace("$READIN", readIn)
                command.replace("$HOST", host)
                result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = result.communicate()
                readIn = output

                # Now submit the token we got
                tokenOutput, tokenError = submitFlag(output, teamIp, teamToken)

                # Log progress
                f = open(args.logFile, "a")
                now = time.time()
                timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                f.write(timestamp + ': ======== OUTPUT FOR ' + host + '========\n')
                f.write(timestamp + ': Output read in -- ' + output + '\n')
                f.write(timestamp + ': Errors read in -- ' + error + '\n')
                f.write(timestamp + ': Token output read in -- ' + tokenResult + '\n')
                f.write(timestamp + ': Token error read in -- ' + tokenError + '\n')
                f.close()

                # if slack arguments are given, print out information about the token
                if args.slackChannel and args.slackToken:
                    message = 'Submitted token for ' + host + '. Got the result: ' + tokenResult
                    sendSlackMessage(args.slackChannel, args.slackToken, message)
                    # sleep is given in minutes, convert to seconds by multiplying by 60
                    time.sleep(args.sleep * 60)

# Gets all the hosts using cat /etc/hosts. Doesn't allow localhost to be used.
def getHosts(ignoreHost):
    # Run cat /etc/hosts to find the hosts known to this computer
    cmd = ['cat', '/etc/hosts']
    hosts = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Get the output & error from the subprocess
    output, error = hosts.communicate()
    output = output.decode('ascii')
    # Find all the ip addresses in the response using a regex
    regex = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    words = output.split(" ")
    ipCandidates = []
    for w in words:
        ip = regex.search(w)
        if str(ip) != 'None' and ip.group(0) != ignoreHost and ip.group(0) != '127.0.0.1':
            ipCandidates.append(ip.group(0))
    # use a dictionary to remove any duplicates
    results = list(dict.fromkeys(ipCandidates))
    # return the ip addresses in /etc/hosts
    return results

########### THIS SECTION IS FOR SWPAG_CLIENT USERS #############
# Reads in file for service to exploit
# File needs to be in form:
# <service name> !EXPLOITBEGINS! <exploit>
# <service name> !EXPLOITBEGINS! <exploit>
def readSWPAGFile(filePath):
    f = open(filePath, "r")
    serviceExploits = {}
    # read through line by line and append the commands together
    for line in f:
        entryArr = line.split("!EXPLOITBEGINS!")
        serviceExploits[entryArr[0]] = entryArr[1]
    return serviceExploits

# Send exploits and send flags using swpag_client
def getSWPAGFlags (args):
    t = swpag_client.Team(args.teamIp, args.teamToken)

    # Get the exploits per server
    serviceExploits = readSWPAGFile(args.file)
    services = serviceExploits.keys()
    # Get the status and only run on a new tick
    status = t.get_game_status()
    if current_tick < status['tick_id']:
        current_tick = status['tick_id']
        f = open(args.logFile, "a")
        now = time.time()
        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
        f.write('Connecting to ' + args.teamIp + ' during tick ' + current_tick + ' at timestamp ' + timestamp)
        f.close()

        # determine targets
        tick_services = t.get_service_list()
        for service in tick_services:
            service_name = service['service_name']
            targets = t.get_targets(service['service_id'])
            for target in targets:
                if target['hostname'] != args.ignoreHost: 
                    target_host = target['hostname']
                    target_port = target['port']
                    target_id = target['flag_id']

                    payload = None
                    if service_name in services:
                        payload = serviceExploits[service_name]

                    # connect to target machine and send exploit
                    if payload is not None:
                        f = open(args.logFile, "a")
                        now = time.time()
                        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                        f.write('Targeting ' + target['team_name'] + ' service ' + service_name)
                        f.close()
                        tc = connect(target_host, target_port)
                        time.sleep(0.5)
                        tc.shutdown(socket.SHUT_WR)

                        # Now read in flags
                        subrpocess.call("function slowcat() { while read; do sleep .05; echo \"$REPLY\"; done;}", shell=True, executable='/bin/bash')
                        data = subprocess.check_output(f"cat {payload} | slowcat | nc {target_host} {target_port}", shell=True, executable='/bin/bash')
                        output = data.decode("utf-8")
                        flag = output.replace("\n", "")
                        result = t.submit_flag([flag])
                        f = open(args.logFile, "a")
                        now = time.time()
                        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                        f.write('Tried to submit token for ' + target['team_name'] + ' got result ' + result)
                        f.close()
                        if args.slackChannel and args.slackToken:
                            sendSlackMessage(args.slackChannel, args.slackToken, 'Submitted token for ' + target['team_name'] + ' got result: ' + result)

# Starts up the logging process, gets hosts, and then calls the runForever command
def main(args):
    # Log startup
    f = open(args.logFile, "w")
    now = time.time()
    timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
    f.write(timestamp + ': Starting program\n')
    f.close()
    if args.swpagClient is False:
        hosts = []
        # Either find the hosts using cat /etc/hosts or use a passed in list of hosts
        if args.hosts:
            hosts = args.hosts.split(',')
        else:
            hosts = getHosts(args.ignoreHost)
        # Log the hosts we have found
        f = open(args.logFile, "a")
        now = time.time()
        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
        f.write(timestamp + ': Using these hosts: ' + str(hosts) + '\n')
        f.close()
        # Get the commands from the file
        commands = readFile(args.file)
        # Run the commands at the sleep intervals and slack the result of submitting the flags (if slack information is given)
        runForever(args, commands, hosts, teamIp, teamToken)
    else:
        getSWPAGFlags(args)

# Sets up arguments and then calls main function
if __name__=="__main__":
    # Setup arguments that can be passed to this program
    parser = argparse.ArgumentParser(description='Find all hosts on the network, reads in commands to find the flags, and then submits them for you (in SWPAG format). Can send updates to slack as well as logs progress. Use !READIN to stop the commands and read in the result and $READIN to use that result later in the command file. It will continue to use that variable until another $READIN is called')
    parser.add_argument('--file', help='Path to the file with the commands on it', required=True)
    parser.add_argument('--ignoreHost', help='Give an ip address to not hit')
    parser.add_argument('--hosts', help='Specify a set of ip address to run the commands for, seperated by a comma (i.e. 10.0.0.1,127.0.0.1). If not specified, cat /etc/hosts will be run to find them')
    parser.add_argument('--sleep', help='Tells the program how long to sleep in between each time the command is run - in minutes', default=60)
    parser.add_argument('--slackToken', help='Slack token to send messages about how the flag submission is going. If left unspecified, slack messages will not be sent')
    parser.add_argument('--slackChannel', help='Slack channel to send messages to. If left unspecified, slack messages will not be sent')
    parser.add_argument('--logFile', help='Location to write logs to, defaults to flagLogs.txt', default='flagLogs.txt')
    parser.add_argument('--teamToken', help='Team token used to submit flags. Needed for swpag client')
    parser.add_argument('--teamIp', help='Ip address team is at. Needed for swpag client.')
    parser.add_argument('--swpagClient', help='Are you using the swpag_client? Defaults to true. Note: if it is not SWPAG, you need to use the commands.txt file to submit the flag', default=True)
    args = parser.parse_args()
    main(args)
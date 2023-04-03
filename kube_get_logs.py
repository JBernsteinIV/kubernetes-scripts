#!/usr/bin/python3
"""
    Name: kube_log_algorithm.py - Scans for logs of running Kubernetes pods; filter out Kubernetes-specific pods (e.g. 'kube-system' namespace)
    Author: John L. Bernstein IV (jbernsteiniv@gmail.com)
    Date: April 02 2023
"""
import json
import subprocess
from typing import Union
KUBECTL = '/usr/local/bin/kubectl'

def _run(*args, **kwargs) -> Union[list, None]:
    sub_flags = []
    # Check if a namespace was passed in. We will need this info for pods not in the default namespace.
    namespace = "default"
    pod       = None
    if 'namespace' in kwargs:
        namespace = kwargs['namespace']
    if 'pod' in kwargs:
        pod = kwargs['pod']
    # Check that the passed in arguments are valid for kubectl's subcommands.
    subcommand = args[0]
    # Run the command, check if stderr got any information, capture anything written to stdout.
    command = [
        KUBECTL,
        subcommand
    ]
    for arg in args[1:]:
        command.append(arg)
    #print(command)
    output  = subprocess.run(command, capture_output=True)
    stderr  = output.stderr.decode('utf-8')
    stdout  = output.stdout.decode('utf-8')
    if len(stderr) > 0:
        if 'No resources found' in stderr:
            return None
        print(f"Error! stderr logged the following: {stderr}")
        raise Exception
    else:
        lines = []
        for line in stdout.split("\n"):
            lines.append(line)
        return lines

def get_namespaces() -> Union[list, None]:
    flags = ['--no-headers','--all-namespaces']
    output = _run('get','namespaces',*flags)
    if not output:
        return []
    namespaces = []
    for line in output:
        if line:
            namespace = line.split()[0]
            namespaces.append(namespace)
    return namespaces

def get_pods(namespace: str) -> Union[list, None]:
    flags = [f'--namespace={namespace}','--no-headers']
    output    = _run('get','pods',*flags)
    if not output:
        return None
    pods      = []
    for line in output:
        if line:
            pod = line.split()[0]
            if pod:
                template = {
                    'namespace' : namespace,
                    'name'      : pod
                }
                pods.append(template)
    return pods

# TODO: Add in option to scan by container
def get_logs(namespace: str, pod: str, limit=None, since=None) -> Union[list, None]:
    # By default make sure to pass in the namespace and capture a timestamp of when the log occurred.
    flags = [f'--namespace={namespace}','--timestamps']
    if limit:
        flags.append(f'--tail={limit}')
    if since:
        flags.append(f'--since={since}')
    # *flags will unpack the list into whitespace separated strings for the subprocess shell.
    output    = _run('logs',f'{pod}', *flags)
    if not output:
        return None
    logs      = []
    for line in output:
        if line:
            template = {
                'pod'       : pod,
                'namespace' : namespace,
                'timestamp' : line.split()[0],
                'message'   : " ".join(line.split()[1:])
            }
            logs.append(json.dumps(template))
    # Return the list UP TO the limit amount (if not specified, this will give the whole list).
    return logs[:limit]

# TODO: Implement in options for the helm utility (Kubernetes package manager).
# TODO: Build a CLI to invoke different options at runtime.

if __name__ == '__main__':
    pods       = []
    namespaces = get_namespaces()
    for namespace in namespaces:
        if 'kube' not in namespace:
            pods = get_pods(namespace=namespace)
        if len(pods) > 0:
            # Check the logs for each pod.
            for pod in pods:
                logs = get_logs(namespace=pod['namespace'], pod=pod['name'], limit=10, since='1h')
                if len(logs) > 0:
                    for log in logs:
                        podname = pod['name']
                        print(f"{log}")
                else:
                    podname = pod['name']
                    print(f"No logs found for pod `{podname}` in namespace `{namespace}`")
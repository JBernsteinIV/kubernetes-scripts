# kubernetes-scripts
Various scripts to interface with Kubernetes (as part of my learning process)

# kube_get_logs.py
This script will scan all namespaces visible to the Kubernetes cluster and will print JSON objects representing the pod, namespace, time of the message, and message itself.
Example:
```
  {
    "pod": "my-release-kube-state-metrics-6897b88569-xlp26",
    "namespace": "default",
    "timestamp": "2023-04-03T05:34:16.411037148Z",
    "message": "E0403 05:34:16.410741 1 reflector.go:140] pkg/mod/k8s.io/client-go@v0.26.1/tools/cache/reflector.go:169: Failed to watch *v1.PodDisruptionBudget: failed to list *v1.PodDisruptionBudget: the server could not find the requested resource"
  }
```
The intention is this script would be used in environments that may not allow easy integration of monitoring tools (e.g. Prometheus, Checkmk, Zabbix, Icinga, etc) to keep status on the health quality of the running pods.

This script can be used as a helper function to get the logs to be integrated with additional scripts or monitoring tools (e.g. custom UserParameters in Zabbix agents) to check for the real status of the cluster environment.

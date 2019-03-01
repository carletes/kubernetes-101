# Kubernetes 101, 1 March 2019

## Scope

Basic concepts in Kubernetes. A walk through parts of
https://kubernetes.io/docs/concepts/

Ways to learn more:

* Read the *latest version* os the [official
  documentation](https://kubernetes.io/docs/home/).
* Read *up-to-date* blogs and guides.

It's a fast-moving world. Anything older than 6 months is potentially
stale knowledge. Anything older than one year even more so (my [notes
from KubeCon 2016
](https://confluence.ecmwf.int/display/DS/2016/03/10/KubeCon+EU+2016%2C+day+1),
for instance).


## Overview

Kubernetes: A container orchestration framework.

Declarative model:

* User defines Kubernetes objects representing the desired state of
  the cluster.
* The Kubernetes control plane makes the cluster's current state
  converge toward the desired state.

Basic Kubernetes object types:

* Namespaces (cluster partitions)
* Pods (units of one or more containers)
* Persistent volumes (persistent storage).
* Services (network endpoints for pods)

Basic Kubernetes controllers:

* Deployments
* Replica sets

Many more types of objects and controllers --- we'll address them in
future sessions.


## A Kubernetes cluster

The EFAS cluster:

```
$ kubectl get nodes
NAME                   STATUS   ROLES    AGE   VERSION
k8s-efas-dev-master    Ready    master   86d   v1.12.2
k8s-efas-dev-node-00   Ready    <none>   86d   v1.12.2
k8s-efas-dev-node-01   Ready    <none>   86d   v1.12.2
k8s-efas-dev-node-02   Ready    <none>   86d   v1.12.2
k8s-efas-dev-node-03   Ready    <none>   86d   v1.12.2
k8s-efas-dev-node-04   Ready    <none>   86d   v1.12.2
$
```

Master node(s): Host the control plane processes:

* `kube-apiserver`: API entry-point.
* `etcd`: Distributed key-value store which keeps the cluster's state.
* `kube-scheduler`: Assigned nodes for pods to be run on.
* `kube-controller-manager`: Ensures Kubernetes controller managers
  (replication controllers, etc) are up-to-date.
* `cloud-controller-manager`: Interacts with the underlying cloud
  provider (not an isolated process yet, it's part of
  `kube-controller-manager`).

Worker node(s): Host the processes to be run.

Each node runs these two Kubernetes processes:

* `kubelet`: Agent process that takes care of running the containers
  for each pod.
* `kube-proxy`: Manages network connections for pods.
* A container runtime: Docker or similar.


## Kubernetes as an API

The `kubectl` tool is an API client. It can be configured to access
several clusters:

```
$ kubectl config get-contexts
CURRENT   NAME                   CLUSTER      AUTHINFO           NAMESPACE
*         efas-dev@kubernetes    kubernetes   efas-dev           efas-dev
          kubernetes-admin@k8s   k8s          kubernetes-admin
$
```

```
$ kubectl config use-context kubernetes-admin@k8s
Switched to context "kubernetes-admin@k8s".
$
```

```
$ kubectl get nodes
NAME               STATUS   ROLES    AGE   VERSION
k8s-controller-0   Ready    master   10d   v1.13.3
k8s-worker-0       Ready    <none>   10d   v1.13.3
k8s-worker-1       Ready    <none>   10d   v1.13.3
k8s-worker-2       Ready    <none>   10d   v1.13.3
k8s-worker-3       Ready    <none>   10d   v1.13.3
$
```


## Namespaces

A way to partition a cluster:

```
$ kubectl get ns
NAME            STATUS   AGE
default         Active   10d
ingress-nginx   Active   10d
kube-public     Active   10d
kube-system     Active   10d
$
```

```
$ kubectl describe ns kube-system
Name:         kube-system
Labels:       <none>
Annotations:  <none>
Status:       Active

No resource quota.

No resource limits.
$
```

API-level permissions apply:

```
$ kubectl config use-context efas-dev@kubernetes
Switched to context "efas-dev@kubernetes".
$
```

```
$ kubectl get ns
Error from server (Forbidden): namespaces is forbidden: User "efas-dev" cannot
list resource "namespaces" in API group "" at the cluster scope
$
```

Namespaces may limit resources, too:

```
$ kubectl describe ns efas-dev
Name:         efas-dev
Labels:       <none>
Annotations:  kubectl.kubernetes.io/last-applied-configuration:
                {"apiVersion":"v1","kind":"Namespace","metadata":{"annotations":{},"name":"efas-dev","namespace":""},"spec":{"finalizers":["kubernetes"]}}
Status:       Active

Resource Quotas
 Name:     memory-cpu-quota
 Resource  Used    Hard
 --------  ---     ---
 cpu       10500m  32
 memory    8Gi     64Gi

Resource Limits
 Type       Resource  Min  Max  Default Request  Default Limit  Max Limit/Request Ratio
 ----       --------  ---  ---  ---------------  -------------  -----------------------
 Container  cpu       -    -    500m             1              -
 Container  memory    -    -    256Mi            512Mi          -
$
```


## Pods

The minimal schedulable processing object in Kubernetes. A set of one
or more containers, sharing:

* A network namespace. Each pod gets its own IP address.
* A set of file systems.

Each container has its own root file system and process kernel namespace.

```
$ cat > pod.yaml <<EOT
apiVersion: v1
kind: Pod
metadata:
  name: hello-pod
  namespace: kubernetes-101
spec:
  containers:
    - name: shell
      image: busybox:latest
      stdin: true
      tty: true
EOT
$
```

```
$ kubectl apply -f pod.yaml
pod/hello-pod created
$
```

```
$ kubectl -n kubernetes-101 describe pod/hello-pod
Name:               hello-pod
Namespace:          kubernetes-101
Priority:           0
PriorityClassName:  <none>
Node:               k8s-worker-0/10.240.0.20
Start Time:         Thu, 28 Feb 2019 14:30:00 +0000
Labels:             <none>
Annotations:        kubectl.kubernetes.io/last-applied-configuration:
                      {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"name":"hello-pod","namespace":"kubernetes-101"},"spec":{"containers":[{"imag...
Status:             Running
IP:                 10.44.0.2
Containers:
  shell:
    Container ID:   docker://93ae62deb9f366df60a6e448eabdeeb3a3422b1d23229a1313875844c0ae9319
    Image:          busybox:latest
    Image ID:       docker-pullable://busybox@sha256:061ca9704a714ee3e8b80523ec720c64f6209ad3f97c0ff7cb9ec7d19f15149f
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Thu, 28 Feb 2019 14:30:05 +0000
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-4lf8q (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:
  default-token-4lf8q:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-4lf8q
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type    Reason     Age   From                   Message
  ----    ------     ----  ----                   -------
  Normal  Scheduled  6s    default-scheduler      Successfully assigned kubernetes-101/hello-pod to k8s-worker-0
  Normal  Pulling    4s    kubelet, k8s-worker-0  pulling image "busybox:latest"
  Normal  Pulled     2s    kubelet, k8s-worker-0  Successfully pulled image "busybox:latest"
  Normal  Created    2s    kubelet, k8s-worker-0  Created container
  Normal  Started    1s    kubelet, k8s-worker-0  Started container
$
```

A terminal session in the pod.

```
$ kubectl -n kubernetes-101 exec -it hello-pod sh
/ # ps auxww
PID   USER     TIME  COMMAND
    1 root      0:00 sh
    8 root      0:00 sh
   19 root      0:00 ps auxww
/ # ifconfig
eth0      Link encap:Ethernet  HWaddr 66:30:5D:17:81:22
          inet addr:10.44.0.2  Bcast:10.47.255.255  Mask:255.240.0.0
          UP BROADCAST RUNNING MULTICAST  MTU:1376  Metric:1
          RX packets:12 errors:0 dropped:0 overruns:0 frame:0
          TX packets:1 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:908 (908.0 B)  TX bytes:42 (42.0 B)

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

/ # hostname
hello-pod
/ # hostname -f
hello-pod
/ # cat /etc/resolv.conf
nameserver 10.96.0.10
search kubernetes-101.svc.cluster.local svc.cluster.local cluster.local openstacklocal
options ndots:5
/ # df -h
Filesystem                Size      Used Available Use% Mounted on
overlay                  16.2G    822.8M     15.4G   5% /
tmpfs                    64.0M         0     64.0M   0% /dev
tmpfs                    15.7G         0     15.7G   0% /sys/fs/cgroup
/dev/mapper/system-var
                         16.2G    822.8M     15.4G   5% /dev/termination-log
/dev/mapper/system-var
                         16.2G    822.8M     15.4G   5% /etc/resolv.conf
/dev/mapper/system-var
                         16.2G    822.8M     15.4G   5% /etc/hostname
/dev/mapper/system-var
                         16.2G    822.8M     15.4G   5% /etc/hosts
shm                      64.0M         0     64.0M   0% /dev/shm
tmpfs                    15.7G     12.0K     15.7G   0% /var/run/secrets/kubernetes.io/serviceaccount
tmpfs                    15.7G         0     15.7G   0% /proc/acpi
tmpfs                    64.0M         0     64.0M   0% /proc/kcore
tmpfs                    64.0M         0     64.0M   0% /proc/keys
tmpfs                    64.0M         0     64.0M   0% /proc/timer_list
tmpfs                    64.0M         0     64.0M   0% /proc/sched_debug
tmpfs                    15.7G         0     15.7G   0% /proc/scsi
tmpfs                    15.7G         0     15.7G   0% /sys/firmware
/ # exit
$
```


## Pods with more than one container

Used for very tightly-coupled processes.

In ecCharts we have a service that generates plots with Magics, and
exposes them as URLs to other components of the system. Instead of
writing a web server to serve them, we use Nginx:

```
# ...
      containers:
        - name: service
          image: ecmwf/webdev-services:feature-hello-cloud
          volumeMounts:
            - name: scratch
              mountPath: /data/scratch
        - name: nginx
          image: ecmwf/webdev-nginx:feature-hello-cloud
          command: ["nginx", "-c", "/etc/nginx/site/nginx.conf", "-g", "daemon off;"]
          ports:
            - containerPort: 8081
          volumeMounts:
            - name: scratch
              mountPath: /data/scratch
      volumes:
	    - # Stay tuned!
# ...
```

### Init containers

Pods may also have *init containers*, which are executed in sequence
and before the main containers are started. They are useful for
initialising a service.

All init containers must return an exit code of 0 for the main service
to be started.

In ecCharts we serve dynamic requests with Django, but prefer to serve
static content with Nginx (so we use an extra Nginx container in the
Django pod for that). Before we start Dajngo, we must:

* Collect and package the static content to be served by Nginx, and
* Ensure the relevant database tables needed by Django exist.

We use init containers for those two purposes:

```
# ..
      initContainers:
        - name: collectstatic
          image: ecmwf/webdev-django:feature-hello-cloud
		  ["python", "/code/apps/manage.py", "collectstatic", "--no-input", "--no-color"]
          volumeMounts:
            - name: staticfiles
              mountPath: /data/django/staticfiles
        - name: migrate
          image: ecmwf/webdev-django:feature-hello-cloud
          command: ["python", "/code/apps/manage.py", "migrate", "--no-input", "--no-color"]
      containers:
        - name: django
          image: ecmwf/webdev-django:feature-hello-cloud
        - name: static
          image: ecmwf/webdev-nginx:feature-hello-cloud
          volumeMounts:
            - name: staticfiles
              mountPath: /data/django/staticfiles
      volumes:
        - # Stay tuned!
# ..
```


## Pods networking

Each pod gets one IP address:

```
$ kubectl -n kubernetes-101 get pods -o wide
NAME        READY   STATUS    RESTARTS   AGE   IP          NODE           NOMINATED NODE   READINESS GATES
hello-pod   1/1     Running   0          70m   10.44.0.2   k8s-worker-0   <none>           <none>
$
```

Those IP addresses are *not* visible from outside the Kubernetes cluster.

Pods may talk to each other using their IP addresses:

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
apiVersion: v1
kind: Pod
metadata:
  name: goodbye-pod
  namespace: kubernetes-101
spec:
  containers:
    - name: shell
      image: busybox:latest
      stdin: true
      tty: true
EOT
pod/goodbye-pod created
$
```

```
$ kubectl -n kubernetes-101 get pods -o wide
NAME          READY   STATUS    RESTARTS   AGE   IP          NODE           NOMINATED NODE   READINESS GATES
goodbye-pod   1/1     Running   0          18s   10.40.0.2   k8s-worker-3   <none>           <none>
hello-pod     1/1     Running   0          72m   10.44.0.2   k8s-worker-0   <none>           <none>
$
```

```
$ kubectl -n kubernetes-101 exec hello-pod ping 10.40.0.2
PING 10.40.0.2 (10.40.0.2): 56 data bytes
64 bytes from 10.40.0.2: seq=0 ttl=64 time=2.645 ms
64 bytes from 10.40.0.2: seq=1 ttl=64 time=0.814 ms
64 bytes from 10.40.0.2: seq=2 ttl=64 time=0.665 ms
^C
$
```

In this example, pod `hello-pod` running on node `k8s-worker-0` is
able to ping pod `goodbye-pod` running on node `k8s-worker-3`.

This is thanks to the *cluster network add-on* we're running in this
Kubernetes cluster.


### No stable network identity for pods

If a pod gets recreated, its IP address might (most likely *will*)
change:

```
$ kubectl -n kubernetes-101 delete pod goodbye-pod
pod "goodbye-pod" deleted
$
```

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
apiVersion: v1
kind: Pod
metadata:
  name: goodbye-pod
  namespace: kubernetes-101
spec:
  containers:
    - name: shell
      image: busybox:latest
      stdin: true
      tty: true
EOT
pod/goodbye-pod created
$
```

```
$ kubectl -n kubernetes-101 get pods -o wide
NAME          READY   STATUS    RESTARTS   AGE   IP          NODE           NOMINATED NODE   READINESS GATES
goodbye-pod   1/1     Running   0          6s    10.42.0.1   k8s-worker-2   <none>           <none>
hello-pod     1/1     Running   0          76m   10.44.0.2   k8s-worker-0   <none>           <none>
$
```

So we need to solve two issues with pod networking:

* Reach pods from outside the cluster.
* Give pods stable network identities within the cluster.


## Services

Services are Kubernetes objects that provide stable network identities
to pods.

Let's start with two pods: One called `sample-website`, which will
host a web server, and another one called `sample-client`, from which
we'll call our web server:

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
---
apiVersion: v1
kind: Pod
metadata:
  name: sample-client
  namespace: kubernetes-101
spec:
  containers:
    - name: shell
      image: busybox:latest
      stdin: true
      tty: true
---
apiVersion: v1
kind: Pod
metadata:
  name: sample-website
  namespace: kubernetes-101
  labels:
    app: web-server
spec:
  containers:
    - name: nginx
      image: nginx:latest
EOT
pod/sample-client created
pod/sample-website created
$
```

```
$ kubectl -n kubernetes-101 get pods -o wide
NAME             READY   STATUS    RESTARTS   AGE     IP          NODE           NOMINATED NODE   READINESS GATES
sample-client    1/1     Running   0          3m14s   10.44.0.3   k8s-worker-0   <none>           <none>
sample-website   1/1     Running   0          2m33s   10.36.0.2   k8s-worker-1   <none>           <none>
$
```

The only way we have now to access the web server is by using the IP
address of its pod:

```
$ kubectl -n kubernetes-101 exec -it sample-client sh
/ # wget -O - -q http://10.36.0.2
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
/ #
```

If the pod gets re-scheduled by the control place, or if we redeploy
the web server after a system sessoin, for instance, we lose its
address.

By defining a service, and linking that service to our web server pod,
we establish a permanent network identity which survives pod restarts:

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
apiVersion: v1
kind: Service
metadata:
  name: my-super-web-site
  namespace: kubernetes-101
spec:
  selector:
    app: web-server
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
EOT
service/my-super-web-site created
$
```

The service has an associated IP address, which will not change:

```
$ kubectl -n kubernetes-101 get services
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
my-super-web-site   ClusterIP   10.98.221.206   <none>        80/TCP    77s
$
```

We may use that IP address to call our web server:

```
$ kubectl -n kubernetes-101 exec -it sample-client sh
/ # wget -O - -q http://10.98.221.206
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
/ #
```

We may even use the service name to call it, if our cluster has the
appropriate DNS add-on installed (most have):

```
/ # wget -O - -q http://my-super-web-site
[..]
/ # wget -O - -q http://my-super-web-site.kubernetes-101
[..]
/ # wget -O - -q http://my-super-web-site.kubernetes-101.svc
[..]
/ # wget -O - -q http://my-super-web-site.kubernetes-101.svc.cluster.local
[..]
/ # wget -O - -q http://my-super-web-site.kubernetes-101.svc.cluster.local.
[..]
```

## Cloud provider integration

When running on VMs, Kubernetes is able to talk to some cloud
providers in order to provide:

* Block storage, in order to mount persistent file systems in pods
  (more on that later), and
* Floating IP addresses, so that services running in the Kubernetes
  cluster may be accessed from outside the Kubernetes cluster.

As of 1.13, support for cloud providers is compiled into the
Kubernetes binaries. The following cloud providers are supported:

* External cloud providers (AWS, GCP, Azure, ...)
* On-premises cloud providers (VMWare, OpenStack, ...)

Work is well underway for supporting third-party cloud providers not
included in the Kubernetes source code tree.


## Services (continued)

In our example cluster, hosted on the CDS OpenStack cluster, we may
make our sample web server accessible from outside the cluster (and
from anywhere in the whole Internet).

We need to define a service of type `LoadBalancer`:

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
apiVersion: v1
kind: Service
metadata:
  name: sample-external-service
  namespace: kubernetes-101
spec:
  selector:
    app: web-server
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
EOT
service/sample-external-service created
$
```

After creating the service, Kubernetes requests a floating IP from the
CDS cluster. This takes a while:

```
$ kubectl -n kubernetes-101 get services
NAME                      TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
my-super-web-site         ClusterIP      10.98.221.206    <none>        80/TCP         33m
sample-external-service   LoadBalancer   10.111.183.204   <pending>     80:32751/TCP   27s
$
```

At some point, hopefully (if the OpenStack CDS cluster has enought IP
addresses available), our service gets assigned one:

```
$ kubectl -n kubernetes-101 get services
NAME                      TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)        AGE
my-super-web-site         ClusterIP      10.98.221.206    <none>            80/TCP         33m
sample-external-service   LoadBalancer   10.111.183.204   136.156.132.128   80:32751/TCP   62s
$
```

And things work as expected:


```
$ curl -v http://136.156.132.128
* Rebuilt URL to: http://136.156.132.128/
*   Trying 136.156.132.128...
* TCP_NODELAY set
* Connected to 136.156.132.128 (136.156.132.128) port 80 (#0)
> GET / HTTP/1.1
> Host: 136.156.132.128
> User-Agent: curl/7.58.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: nginx/1.15.9
< Date: Thu, 28 Feb 2019 19:37:13 GMT
< Content-Type: text/html
< Content-Length: 612
< Last-Modified: Tue, 26 Feb 2019 14:13:39 GMT
< Connection: keep-alive
< ETag: "5c754993-264"
< Accept-Ranges: bytes
<
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
* Connection #0 to host 136.156.132.128 left intact
$
```

If we now remove the web server pod, the web site is no longer
accessible:

```
$ kubectl -n kubernetes-101 delete pod sample-website
pod "sample-website" deleted
$
```



## Volumes

Volumes are Kubernetes abstractions that represent shared storage
between different containers in a pod.

There are [many types of
volumes](https://kubernetes.io/docs/concepts/storage/volumes/#types-of-volumes)
available. Some, like NFS-backed volumes, offer content persistence
across pod restarts. Others, like node-based empty directories, do
not.

The following example creates a pod with two containers (called
`nginx` and `shell`) sharing a file system mounted on both containers
at `/usr/share/nginx/html`:

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
apiVersion: v1
kind: Pod
metadata:
  name: sample-website
  namespace: kubernetes-101
  labels:
    app: web-server
spec:
  containers:
    - name: nginx
      image: nginx:latest
      volumeMounts:
        - name: htdocs
          mountPath: /usr/share/nginx/html
    - name: shell
      image: busybox:latest
      stdin: true
      tty: true
      volumeMounts:
        - name: htdocs
          mountPath: /usr/share/nginx/html
  volumes:
    - name: htdocs
      emptyDir: {}
EOT
pod/sample-website created
$
```

The volume is initially empty:

```
$ kubectl -n kubernetes-101 exec sample-website -c nginx -- ls -l /usr/share/nginx/html
total 0
$
```

We may now create some content in the `shell` container:

```
$ kubectl -n kubernetes-101 exec sample-website -c shell -it sh
/ # cd /usr/share/nginx/html
/usr/share/nginx/html # ls -l
total 0
/usr/share/nginx/html # echo "Welcome to the European Weather Cloud" > index.html
/usr/share/nginx/html # ls -l
total 4
-rw-r--r--    1 root     root            38 Mar  1 10:27 index.html
/usr/share/nginx/html # exit
$
```

The content will be available in the `nginx` container:

```
$ env http_proxy= curl http://136.156.132.232/
Welcome to the European Weather Cloud
$
```

## Persistent volumes

Persistent volumes are Kubernetes objects that provide persistent
storage.

There are [many types of persistent
volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes). Some
of them support sharing of volumes between several pods.

Many types of persistent volumes rely on the *cloud provider* to
provide the backing storage. In our CDS cluster we have configured
Kubernetes to talk to OpenStack:

```
$ kubectl get storageclasses
NAME                 PROVISIONER            AGE
standard (default)   kubernetes.io/cinder   11d
$
```

```
$ kubectl describe storageclass standard
Name:            standard
IsDefaultClass:  Yes
Annotations:     kubectl.kubernetes.io/last-applied-configuration={"apiVersion":"storage.k8s.io/v1","kind":"StorageClass","metadata":{"annotations":{"storageclass.beta.kubernetes.io/is-default-class":"true"},"labels":{"addonmanager.kubernetes.io/mode":"EnsureExists","kubernetes.io/cluster-service":"true"},"name":"standard"},"provisioner":"kubernetes.io/cinder"}
,storageclass.beta.kubernetes.io/is-default-class=true
Provisioner:           kubernetes.io/cinder
Parameters:            <none>
AllowVolumeExpansion:  <unset>
MountOptions:          <none>
ReclaimPolicy:         Delete
VolumeBindingMode:     Immediate
Events:                <none>
$
```

### Using persistent volumes

The cleanest way to use persistent storage is to define a *persistent
volume claim*. Persistent volume claims are Kubernetes objects that
instruct the Kubernetes control plane to provide persistent storage
(if the cloud provider supports it).

Like in our previous example, let's create a web server pod --- but
this time with a persistent volume backing our HTML content:

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: htdocs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 42Gi

---
apiVersion: v1
kind: Pod
metadata:
  name: sample-website
  namespace: kubernetes-101
  labels:
    app: web-server
spec:
  containers:
    - name: nginx
      image: nginx:latest
      volumeMounts:
        - name: htdocs
          mountPath: /usr/share/nginx/html
    - name: shell
      image: busybox:latest
      stdin: true
      tty: true
      volumeMounts:
        - name: htdocs
          mountPath: /usr/share/nginx/html
  volumes:
    - name: htdocs
      persistentVolumeClaim:
        claimName: htdocs-pvc
EOT
persistentvolumeclaim/htdocs-pvc created
pod/sample-website created
$
```

Just like before, we can now add some content:


```
$ kubectl -n kubernetes-101 exec sample-website -c shell -it sh
/ #
/ #
/ # echo "Welcome to the European Weather Cloud" > index.html
/ # cd /usr/share/nginx/html
/usr/share/nginx/html # ls -l
total 16
drwx------    2 root     root         16384 Mar  1 12:52 lost+found
/usr/share/nginx/html # echo "Welcome to the European Weather Cloud" > index.html
/usr/share/nginx/html # exit
$
```

And it still works:

```
$ env http_proxy= curl http://136.156.132.232/
Welcome to the European Weather Cloud
$
```

Now the interesting bit: Let's remove the pod, and recreate it:

```
$ kubectl -n kubernetes-101 delete pod sample-website
pod "sample-website" deleted
$
```

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
apiVersion: v1
kind: Pod
metadata:
  name: sample-website
  namespace: kubernetes-101
  labels:
    app: web-server
spec:
  containers:
    - name: nginx
      image: nginx:latest
      volumeMounts:
        - name: htdocs
          mountPath: /usr/share/nginx/html
    - name: shell
      image: busybox:latest
      stdin: true
      tty: true
      volumeMounts:
        - name: htdocs
          mountPath: /usr/share/nginx/html
  volumes:
    - name: htdocs
      persistentVolumeClaim:
        claimName: htdocs-pvc
EOT
pod/sample-website created
$

```

The original content is still there:

```
$ env http_proxy= curl http://136.156.132.232/
Welcome to the European Weather Cloud
$
```

## Deployments

So far we have:

* A way to run processes in a Kubernetes cluster (pods).
* A way to use persistent storage in a Kubernetes cluster (persistent
  volumes).
* A way to give oour pods stable network identity, and make them
  accessible from the outside world (services).

Pods are still ephemeral, though:

* The node where they're running may crash, or be taken offline for
  maintenance.
* We may accidentally remove a pod.

With Kubernetes *deployments* we may now ensure that:

* A given pod is recreated (if a Kubernetes node goes down, for
  instance).
* There are always a minimum number of copies of a given pod (so that
  we may do zero-downtime upgrades, for instance).


Let's create now a Kubernetes deployment for our sample web site with
just one replica:

```
$ kubectl -n kubernetes-101 apply -f - <<EOT
---
apiVersion: v1
kind: Service
metadata:
  name: sample-website
  namespace: kubernetes-101
spec:
  selector:
    app: sample-website
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: htdocs-pvc
  namespace: kubernetes-101
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 42Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-website
  namespace: kubernetes-101
  labels:
    app: sample-website
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sample-website
  template:
    metadata:
      namespace: kubernetes-101
      labels:
        app: sample-website
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          volumeMounts:
            - name: htdocs
              mountPath: /usr/share/nginx/html
        - name: shell
          image: busybox:latest
          stdin: true
          tty: true
          volumeMounts:
            - name: htdocs
              mountPath: /usr/share/nginx/html
      volumes:
        - name: htdocs
          persistentVolumeClaim:
            claimName: htdocs-pvc
EOT
service/sample-website created
persistentvolumeclaim/htdocs-pvc unchanged
deployment.apps/sample-website created
$
```

At some point the deployment will be created:

```
$ kubectl -n kubernetes-101 get deployments
NAME             READY   UP-TO-DATE   AVAILABLE   AGE
sample-website   1/1     1            1           49s
$
```

The Kubernetes deployment has created another Kubernetes object: A
*replica set*. Replica sets ensure that at any given moment the
desired number of copies of a given pod are alive (one, in our
example).

```
$ kubectl -n kubernetes-101 describe deployment sample-website
Name:                   sample-website
Namespace:              kubernetes-101
CreationTimestamp:      Fri, 01 Mar 2019 13:17:29 +0000
Labels:                 app=sample-website
Annotations:            deployment.kubernetes.io/revision: 1
                        kubectl.kubernetes.io/last-applied-configuration:
                          {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"sample-website"},"name":"sample-website","namesp...
Selector:               app=sample-website
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=sample-website
  Containers:
   nginx:
    Image:        nginx:latest
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:
      /usr/share/nginx/html from htdocs (rw)
   shell:
    Image:        busybox:latest
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:
      /usr/share/nginx/html from htdocs (rw)
  Volumes:
   htdocs:
    Type:       PersistentVolumeClaim (a reference to a PersistentVolumeClaim in the same namespace)
    ClaimName:  htdocs-pvc
    ReadOnly:   false
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  <none>
NewReplicaSet:   sample-website-76f87f4b57 (1/1 replicas created)
Events:
  Type    Reason             Age    From                   Message
  ----    ------             ----   ----                   -------
  Normal  ScalingReplicaSet  2m16s  deployment-controller  Scaled up replica set sample-website-76f87f4b57 to 1
$
```

Our replica set is alive and well:

```
$ kubectl -n kubernetes-101 describe replicaset sample-website-76f87f4b57
Name:           sample-website-76f87f4b57
Namespace:      kubernetes-101
Selector:       app=sample-website,pod-template-hash=76f87f4b57
Labels:         app=sample-website
                pod-template-hash=76f87f4b57
Annotations:    deployment.kubernetes.io/desired-replicas: 1
                deployment.kubernetes.io/max-replicas: 2
                deployment.kubernetes.io/revision: 1
Controlled By:  Deployment/sample-website
Replicas:       1 current / 1 desired
Pods Status:    1 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  app=sample-website
           pod-template-hash=76f87f4b57
  Containers:
   nginx:
    Image:        nginx:latest
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:
      /usr/share/nginx/html from htdocs (rw)
   shell:
    Image:        busybox:latest
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:
      /usr/share/nginx/html from htdocs (rw)
  Volumes:
   htdocs:
    Type:       PersistentVolumeClaim (a reference to a PersistentVolumeClaim in the same namespace)
    ClaimName:  htdocs-pvc
    ReadOnly:   false
Events:
  Type    Reason            Age    From                   Message
  ----    ------            ----   ----                   -------
  Normal  SuccessfulCreate  3m48s  replicaset-controller  Created pod: sample-website-76f87f4b57-jw6wg
$
```

... and it has created one pod, using the template we provided in the
Kubernetes deployment object:

```
$ kubectl -n kubernetes-101 get pods
NAME                              READY   STATUS    RESTARTS   AGE
sample-website-76f87f4b57-jw6wg   2/2     Running   0          72s
$
```

As before, the Kubernetes service object exists, and has an external
IP address attached to it:

```
$ kubectl -n kubernetes-101 get svc
NAME                      TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)        AGE
sample-external-service   LoadBalancer   10.104.216.178   136.156.132.163   80:31369/TCP   30m
sample-website            LoadBalancer   10.101.181.86    136.156.132.232   80:30581/TCP   4m34s
$
```

And everything still works:

```
$ env http_proxy= curl http://136.156.132.232
Welcome to the European Weather Cloud
$
```

# Experimenting with EKS Distro

EKS Distro announcement : 
https://aws.amazon.com/blogs/opensource/introducing-amazon-eks-distro/

## Overview - Shared responsibility model with EKS

![Shared responsibility model with EKS](https://raw.githubusercontent.com/alfallouji/AWS-SAMPLES/master/eks-distro-test/eks-overview.png)

## Setting up the environment 

Testing EKS distro with an Ubuntu VM : 

VM - Ubuntu 20.10 with Virtualbox 6.1 - https://ubuntu.com/download/desktop


## Setup EKS with snap

If you want to use other means to set it up : 
https://distro.eks.amazonaws.com/users/install/partners/

Using following tutorial for setup (snap cmd) :
https://ubuntu.com/blog/install-amazon-eks-distro-anywhere

It's just a one line command : 

 `$ sudo snap install eks --edge --classic`

### To check if setup was successfull

`$ sudo eks status`

 ```eks is running
 high-availability: no
   datastore master nodes: 127.0.0.1:19001
   datastore standby nodes: none
 ```


if not started, you can start it like this : 

 `$ sudo eks start`

### No existing pods
`$ sudo eks kubectl get pods`

You should see (which is normal) :

```
No resources found in default namespace.
```


### Add a new pod (from nginx image at docker.io)
 `$ sudo eks  kubectl run nginx-pod --image=nginx`
 
 Expected output : 
```
pod/nginx-pod created
```

### Check if it was added
`$ sudo eks kubectl get pods`

 Expected output : 
```
NAME        READY   STATUS              RESTARTS   AGE
nginx-pod   0/1     ContainerCreating   0          23s
```

### To get details on the running pod
`$ sudo eks kubectl describe pods nginx-pod`

Locate IP address and test it with `curl` or with a browser.

### You can also try with an ECR image
`sudo eks kubectl run ecr-image-pod-test --image=public.ecr.aws/nginx/nginx:latest`

Locate IP address and test it with `curl` or with a browser.

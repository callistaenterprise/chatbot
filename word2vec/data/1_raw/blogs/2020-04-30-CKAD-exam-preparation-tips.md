---
categories: blogg teknik 
layout: "details-blog"
published: true
topstory: true
comments: true
authors: 
  - magnuslarsson
tags: CKAD CNCF containers Docker Kubernetes
heading: Certified Kubernetes Application Developer (CKAD) exam preparation tips
---

Last week I passed the [CKAD exam](https://www.cncf.io/certification/ckad/) (Certified Kubernetes Application Developer). In this blog post, I will share some preparations I did to be able to solve the tasks in the exam, specifically on how I prepared for the time constraints in the exam.

-[readmore]-

## Background

I have been working with Kubernetes since its inception in 2014, and I decided recently to manifest my experience by taking the CKAD exam.

The CKAD exam in summary:

* The exam certifies that users can design, build, configure, and expose cloud native applications for Kubernetes. 
* The exam is performance-based, it consists of 19 tasks with problems to solve within two hours using the command line in a Linux terminal accessible using Chrome. Your score must exceed 66% to pass the exam. 
* The only allowed help is an extra tab in Chrome, where you are allowed to access information from:     
  * <https://kubernetes.io/docs/>​
  * ​<https://github.com/kubernetes/>​
  * <https://kubernetes.io/blog/​> 
* You can take the exam remotely, e.g. from your home, but the exam is proctored using screen sharing, webcam, and the microphone on your computer.
 
From reading the exam curriculum, I realized that I was used to most of the concepts but lacked experience from using a few of them. So I browsed through an on-line course to catch up on the missing parts. Being rather self-confident, I started to go through the tests at the end of the course. I then realized that even if I had experiences from using most of the concepts in the exam, I was not fast enough to execute the exercises given the time available. It took me too long time to use `kubectl` and `vi`, i.e. the main tools used during the exam.

> I guess you can use any text editor available in the Linux terminal, but `vi` was the one I had some previous experience with.

So I had to practice a lot to be fast enough to pass the exam!

## Solving tasks in the exam

Many of the exam tasks can be solved by using the following steps:

1. **Creating a `yaml` file containing start material for the task**  
 Use `kubectl` imperative commands, e.g. `run` and `create` with the options `--dry-run -o yaml > n.yaml` to create the `yaml` file (not yet creating the corresponding resource in the Kubernetes cluster).

2. **Adding the final parts to the `yaml` file using an editor like `vi`**  
The required syntax for the missing pieces can be found in either the links listed above or by using the `kubectl explain` command. 

1. **Create the Kubernetes resources**  
Use the `kubectl apply -f n.yaml` command to create the resources in the Kubernetes cluster.

1. **Verify the expected result**  
Use `kubectl` commands `get -o yaml`, `describe`, `exec`, and `logs` to verify that you got the expected result. 

   Sometimes a HTTP endpoint inside the Kubernetes cluster needs to be verified. This can be done using either `kubectl port-forward` and a local `curl` command in the Linux terminal or by launching a Kubernetes pod that can run the `curl` command inside the cluster, e.g.:

     kubectl run --image=curlimages/curl --restart=Never -i --rm curl-pod -- curl $service:$port -s -m1

## Suggested preparation steps

To be able to solve the tasks in the exam fast enough, I recommend the following preparation steps:

1. Take a course to ensure that you learn all parts of Kubernetes required for the exam.  
I suggest the course [Kubernetes Certified Application Developer (CKAD) with Tests](https://www.udemy.com/course/certified-kubernetes-application-developer/) provided by KodeKloud at Udemy.

2. Read through all material available at [CKAD Certification Exam Candidate Resources](https://training.linuxfoundation.org/cncf-certification-candidate-resources/), i.e. the Candidate Handbook, Exam Tips, and FAQ

3. Bookmark favorite links to the Kubernetes documentation.  
You are allowed to use bookmarks in Chrome to your favorite pages in the links listed above. Get used to use these bookmarks when looking up information.

4. Setup alias and autocomplete according to [kubectl-autocomplete](https://kubernetes.io/docs/reference/kubectl/cheatsheet/#kubectl-autocomplete). Use it both when you practice and during the exam!

    Using `k` as shorthand alias for `kubectl` and enabling autocomplete for `kubectl` commands will save you a lot of time!

    > Set up a bookmark in Chrome to this link!

5. Practice on all options available for the imperative `kubectl` commands for creating start material for the `yaml` files. Specifically the `kubectl run` command contains a lot of useful options for creating a `Pod`, e.g. `--labels`, `--limits`, `--port`, `--requests`, `--serviceaccount`, and `-- [COMMAND] [args...]`.

      The CKAD environment has recently been upgraded to Kubernetes v1.18, where deprecated variants of the `kubectl run` command have been removed. This means that the `run` command only can be used to create `Pods` and that the `create` command has to be used to create  `Deployments`, `Jobs`, and `CronJobs`.
       
      If you still want to use all the useful options in the `run` command for a `Pod` when creating a `Deployment`, you have to execute both the `run` command and the `create deployment` command. Next, you need to paste the result from the `run` command into the result of the `create deployment` command. The content under the `template:` section shall be replace with the `metadata:` and `spec:` sections from the `run` command. Don't forget to indent the output from the `run` command correctly (i.e. using 4 spaces). Practice, practice, practice... 

6. Learn other useful `kubectl` commands:
     1. The commands `label`, `annotate`, `expose`, and `set` can be useful for some tasks
     2. Practice rolling out and rolling back upgrades of a deployment using the `kubectl rollout` command.
     3. To get a good overview of available labels on a set of Kubernetes objects, use the `--show-labels` option of the `kubectl get ` command.
     4. If you are requested to update or fix a problem of an existing resource, use the  `kubectl get ... -o yaml > n.yaml` command to get started.

7. Learn how to configure `vi` to edit `yaml` files efficiently.  
   My recommendation is to create a `.vimrc` file in the home folder with the command `vi ~/.vimrc` and enter:
   
        set number
        set tabstop=2 shiftwidth=2 expandtab

    Explanations to the configuration:

    * `set number` makes `vi` show line numbers, very handy if `kubectl` complains about an error on a specific line in a `yaml` file.
    * `set tabstop=2 shiftwidth=2 expandtab` makes `vi` expand TAB characters to two spaces and sets indentation to two characters, perfect when editing `yaml` files.
    
8. Learn critical `vi` keystrokes to manipulate `yaml` files, specifically:
    1. [Goto a specific line in the text file](https://vim.fandom.com/wiki/Go_to_line)
    2. [Copy and paste lines of code](https://vim.fandom.com/wiki/Cut/copy_and_paste_using_visual_selection)
    3. [Indent lines of code](https://vim.fandom.com/wiki/Shifting_blocks_visually)       

9.  Once you feel confident with the tests provided by the course you took, I recommend that you sign up for the CKAD Simulator provided by [killer.sh](https://killer.sh).  

    It provides you with an environment similar to the exam environment. When you sign up, you are allowed to run the tests in two separates sessions. If you don't feel confident after the first test session, go back and practice on the tasks in the course or look for additional examples on the Internet. Hopefully, you feel confident after taking the second test in the CKAD simulator and are ready for the real exam!

## Taking the exam

During the exam, keep calm and work focused on one task at the time. Always ensure you are on the right cluster and in the right namespace before you start to work on a new task. If you get stuck on a task, you can flag it as unfinished and move on to the next task. If you have time left after going through all tasks, you can go back to unfinished tasks and work on them. 

Using these preparations, I was able to be fast enough with `kubectl` and `vi` to work through all 19 exercises and got a score of 97%, see [my certification badge](https://www.youracclaim.com/badges/65bc0632-b280-4b66-9f7e-876fae03d5ae) and:

![CKAD_Certificate_ML](/assets/blogg/CKAD-exam-preparation-tips/CKAD_Certificate_ML.png)

**Good luck with your preparations and the CKAD exam!**
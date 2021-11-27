---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: Kafka Authorization as a Graph
authors:
  - bjorngylling
---

In this article, we describe an open source tool that makes it possible to visualize access control lists in Kafka to help you get an overview of how access in a Kafka cluster is configured.

Using access control lists (ACLs) to limit access in a Kafka cluster is a great way to secure your data but it can quickly become difficult to overview who can access what. We will set up a Kafka cluster on Kubernetes using [Strimzi](https://strimzi.io) and deploy [bjorngylling/kafka-acl-viewer](https://github.com/bjorngylling/kafka-acl-viewer) in order to visualize the ACLs as a graph. Strimzi leverages Kubernetes [Custom Resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) and the [Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) so that we can work with Kafka in the same declarative manner that we are used to with Kubernetes.

![kafka-acl-viewer example](/assets/blogg/kafka-authorisation-as-a-graph/kafka-acl-viewer-graph.png)

## Strimzi Installation
In order to get started you will need a Kubernetes cluster to run Strimzi and kafka-acl-viewer. During development I usually use [Minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/) but any Kubernetes cluster will do just fine. One thing to note if you do go with Minikube is that Strimzi requires a bit more RAM in your cluster than the default 2GB. To avoid issues make sure you configure Minikube with at least 4GB of RAM when you start your cluster,
```
minikube start --memory=4g
```

When your cluster is up and running go ahead and create yourself a namespace to run things in,
```
kubectl create namespace kafka
```
The rest of the post and its examples will assume you are using a namespace called `kafka`.

Now you're ready to apply the Strimzi installation from Github, note the piping through `sed` to create everything in the correct namespace you created above,
```
curl -L https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.17.0/strimzi-cluster-operator-0.17.0.yaml \
  | sed 's/namespace: .*/namespace: kafka/' \
  | kubectl apply -f - -n kafka
```
This will create the Strimzi deployments in charge of managing your Kafka installation, Cluster Roles, Cluster Role Bindings, and the CRDs (Custom Resource Definitions) you use to configure and manage your cluster.

The next step is to actually create our Kafka cluster, this is done through one of these CRDs, the Kafka custom resource. In order to enable the use of ACLs we need some kind of authentication so that the clients have an identity to tie the access to. Luckily Strimzi makes it really easy to set up TLS authentication. Strimzi will automatically issue certificates for your clients and store them as Kubernetes Secrets for easy access in your application deployments. More on that shortly, first, let us bring up the Kafka cluster.

The following [Kafka](https://strimzi.io/docs/operators/master/using.html#type-Kafka-reference) resource will create a persistent Kafka cluster with one node and TLS authentication enabled.
```
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta1
kind: Kafka
metadata:
  name: my-cluster
  namespace: kafka
spec:
  kafka:
    version: 2.4.0
    replicas: 1
    listeners:
      tls:
        authentication:
          type: tls
    authorization:
      type: simple
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      log.message.format.version: "2.4"
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 100Gi
        deleteClaim: false
  zookeeper:
    replicas: 1
    storage:
      type: persistent-claim
      size: 100Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF
```

When you apply the Kafka resource the Strimzi Cluster Operator will start up a Kafka cluster according to the configuration. This will take a few minutes depending on how fast your cluster is. The following command can be used to wait for everything to be ready,
```
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=5m -n kafka
```

Your Kafka cluster should now be up and running!

## Topics and ACLs Using Strimzi
On to the fun part, creating topics and ACLs! Normally it is quite the headache with longwinded kafka-cli commands to manage your Kafka topics and ACLs. Luckily Strimzi makes this into a much more user-friendly experience by leveraging Kubernetes CRDs, just like the Kafka resource we used in the previous section to create the cluster.

Here is an example of a [KafkaTopic](https://strimzi.io/docs/operators/master/using.html#type-KafkaTopic-reference) resource describing the configuration for a topic in the cluster.
```
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta1
kind: KafkaTopic
metadata:
  name: sales
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 10
  replicas: 1
EOF
```
Applying this in your Kubernetes cluster will cause the Strimzi Topic Operator to pick it up and create the topic in your Kafka cluster. The topic will be given the same name as the Kubernetes resource. The `strimzi.io/cluster` label specifies which Kafka cluster it should be created in, if you have more than one Kafka cluster in the namespace. The `spec` section defines topic specific configuration such as the number of partitions and how it should be replicated. Since we only run a single node in the Kafka cluster we are limited to one replica.

Kafka users and their access is described in a similar manner with a [KafkaUser](https://strimzi.io/docs/operators/master/using.html#type-KafkaUser-reference) resource, here is an example of such a resource,
```
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta1
kind: KafkaUser
metadata:
  name: shipment-api
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  authentication:
    type: tls
  authorization:
    type: simple
    acls:
      - resource:
          type: topic
          name: shipments
          patternType: literal
        operation: Write
        host: "*"
EOF
```
This resource will be picked up by the Strimzi User Operator which will issue a client certificate signed by the certificate authority trusted by the Kafka cluster nodes. The certificate along with the private key will be stored in a Kubernetes Secret with the same name as the user, the secret also contains the public key of the certificate authority issuing the certificates for the cluster nodes. This allows a client to connect and authenticate with the Kafka cluster using mutual TLS. The client is then identified by its certificate and the cluster can authorise it to access resources in the cluster according to the ACLs.

The ACLs listed in the `acls` section are applied on the Kafka cluster by the User Operator as well. This specific example gives the user access to perform API calls grouped under the Write operation on the *shipments* topic. More information about the specifics of the Kafka access model can be found here, [Authorization using ACLs — Confluent Platform](https://docs.confluent.io/current/kafka/authorization.html#operations).

These Kubernetes resources already give a nice and searchable definition of your cluster access model but it is somewhat difficult to get an overview. Let's fix that!

## Deploying kafka-acl-viewer
kafka-acl-viewer is a small open-source application written in [Go](https://golang.org). It connects to Kafka using [Shopify/sarama](https://github.com/Shopify/sarama) and fetches information about ACLs and topics directly from the cluster. This information is rendered as a graph using [visjs/vis-network](https://github.com/visjs/vis-network).

Before we can deploy the application we need to set up a KafkaUser with the appropriate access to the Kafka cluster.
```
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta1
kind: KafkaUser
metadata:
  name: kafka-acl-viewer
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  authentication:
    type: tls
  authorization:
    type: simple
    acls:
      # Read ACLs
      - resource:
          type: cluster
        operation: Describe
        host: "*"
      # Read all topics
      - resource:
          type: topic
          name: "*"
          patternType: literal
        operation: Describe
        host: "*"
EOF
```
The kafka-acl-viewer application will contact the cluster directly to list active ACLs and Topics in the cluster. The *Describe* operation on the *cluster* resource is needed to list the ACLs. The second section allows the application to do *Describe* on all topics in the cluster to read metadata and offsets for topics among other things. It does not give the application access to read the data on the topic, that would require the *Read* operation. You can refer to [Authorization using ACLs — Confluent Platform](https://docs.confluent.io/current/kafka/authorization.html#operations) in order to see exactly which API calls the different operations allow.

Once the ACL is applied kafka-acl-viewer can be deployed, this is a fairly standard Kubernetes deployment,
```
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-acl-viewer
  namespace: kafka
  labels:
    app: kafka-acl-viewer
spec:
  selector:
    matchLabels:
      app: kafka-acl-viewer
  template:
    metadata:
      labels:
        app: kafka-acl-viewer
    spec:
      containers:
      - name: kafka-acl-viewer
        image: bjorngylling/kafka-acl-viewer:v0.5-alpha
        ports:
        - containerPort: 8080
        volumeMounts:
          - name: kafka-acl-viewer-certs
            mountPath: "/kafka-client-certs"
            readOnly: true
          - name: kafka-cluster-cert
            mountPath: "/kafka-ca-certs"
            readOnly: true
        env:
          - name: KAFKA_URL
            value: "my-cluster-kafka-bootstrap:9093"
          - name: CA_FILE
            value: "/kafka-ca-certs/ca.crt"
          - name: CERT_FILE
            value: "/kafka-client-certs/user.crt"
          - name: KEY_FILE
            value: "/kafka-client-certs/user.key"
          - name: FETCH_INTERVAL
            value: "10s"
      volumes:
        - name: kafka-acl-viewer-certs
          secret:
            secretName: kafka-acl-viewer
            items:
              - key: user.crt
                path: user.crt
              - key: user.key
                path: user.key
        - name: kafka-cluster-cert
          secret:
            secretName: my-cluster-cluster-ca-cert
EOF
```
As you can see the certificates and the private key are regular Kubernetes secrets which we mount as files in our pod where the application can access them.

When the application is up and running the easiest way to access it is to use `kubectl port-forward -n kafka deploy/kafka-acl-viewer 8080`. If you are going to use it on a more permanent basis you probably want to set up some kind of ingress. If you now open [localhost:8080](http://localhost:8080) you should see a view of the current accesses in the cluster. The blue boxes are Kafka resources such as topics and the cluster itself and the green boxes are users. The arrows between them represent different types of operations, select one of the resources or users to see what type of operations are connected to it.

![kafka-acl-viewer example](/assets/blogg/kafka-authorisation-as-a-graph/kafka-acl-viewer-example.png)

Try creating some more KafkaUsers and KafkaTopics and watch the graph expand as you refresh the page. Or you can import the the example setup I use for testing which is available in the [kafka-acl-viewer repo](https://raw.githubusercontent.com/bjorngylling/kafka-acl-viewer/master/hack/k8s-test-env/kafka-acl-viewer/example-kafka-topics-and-acls.yaml).

## The Future of kafka-acl-viewer
Right now the main problem with the tool is when you have a big cluster with a lot of ACLs in it, the view becomes difficult to overview which defeats the point. I have begun trying out ways to filter the graph but I'm not quite happy with the results yet.

Feel free to try kafka-acl-viewer in your Kafka cluster, feedback and pull requests are always welcome!

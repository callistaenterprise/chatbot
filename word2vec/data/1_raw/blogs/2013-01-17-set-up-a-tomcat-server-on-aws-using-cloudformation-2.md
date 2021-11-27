---
layout: details-blog
published: true
categories: blogg teknik
heading: Set up a Tomcat server on AWS using CloudFormation
authors:
  - albertorwall
tags: cloudcomputing
topstory: true
comments: true
---

I've been using CloudFormation in my latest project to automate the process of creating new environments. With CloudFormation one can use predefined templates to deploy new infrastructure on Amazon Web Services.

-[readmore]-

In the following example I will create a new EC2 instance with an Apache Tomcat server, Apache HTTP Server and two web applications. I'll also set up security settings and attach an elastic IP address to the instance. -[readmore]- The template can be found [here](https://s3-eu-west-1.amazonaws.com/callista/TomcatExample.template). To deploy the stack described in the template choose "CloudFormation" in the AWS Management Console. Then click "Create stack" and upload the template file.

First of all we want the user to fill in some parameters when creating the stack in CloudFormation. In this case an existing EC2 KeyPair and the instance type:

~~~ javascript
"Parameters" : {
  "KeyName" : {
    "Description" : "Name of an existing EC2 KeyPair to enable SSH access to the instances",
    "Type" : "String"
  },

  "InstanceType" : {
    "Description" : "FormEngine EC2 instance type",
    "Type" : "String",
    "Default" : "m1.small"
  }
}
~~~

Specify conditional values using Mappings. `AWSInstanceType2Arch` specifies allowed EC2 instance types. `AWSRegionArch2AMI` defines which AMI that should be used in each region. We will use EBS backed Amazon Linux AMI:s.

~~~ javascript
"Mappings" : {
  "AWSInstanceType2Arch" : {
    "t1.micro"    : { "Arch" : "64" },
    "m1.small"    : { "Arch" : "64" },
    "m1.medium"   : { "Arch" : "64" },
    "m1.large"    : { "Arch" : "64" },
    "m1.xlarge"   : { "Arch" : "64" },
    "m2.xlarge"   : { "Arch" : "64" },
    "m2.2xlarge"  : { "Arch" : "64" },
    "m2.4xlarge"  : { "Arch" : "64" },
    "c1.medium"   : { "Arch" : "64" },
    "c1.xlarge"   : { "Arch" : "64" },
    "cc1.4xlarge" : { "Arch" : "64" }
  },
  "AWSRegionArch2AMI" : {
    "us-east-1"      : { "32" : "ami-1a249873", "64" : "ami-1624987f" },
    "us-west-1"      : { "32" : "ami-2231bf12", "64" : "ami-2a31bf1a" },
    "us-west-2"      : { "32" : "ami-19f9de5c", "64" : "ami-1bf9de5e" },
    "eu-west-1"      : { "32" : "ami-937474e7", "64" : "ami-c37474b7" },
    "ap-southeast-1" : { "32" : "ami-a2a7e7f0", "64" : "ami-a6a7e7f4" },
    "ap-northeast-1" : { "32" : "ami-486cd349", "64" : "ami-4e6cd34f" },
    "ap-southeast-2" : { "32" : "ami-b3990e89", "64" : "ami-bd990e87" },
    "sa-east-1"      : { "32" : "ami-e209d0ff", "64" : "ami-1e08d103" }
  }
}
~~~

Then we define the AWS resources that should be created.

`WebServerGroup` is the security group used by the AWS instance to define the firewall rules. In this case it should be possible to connect to the server with SSH and HTTP.

~~~ javascript
"WebServerGroup" : {
  "Type" : "AWS::EC2::SecurityGroup",
  "Properties" : {
    "GroupDescription" : "Enable SSH and HTTP access",
    "SecurityGroupIngress" : [
      { "IpProtocol" : "tcp", "FromPort" : "22", "ToPort" : "22", "CidrIp" : "0.0.0.0/0" },
      { "IpProtocol" : "tcp", "FromPort" : "80", "ToPort" : "80", "CidrIp" : "0.0.0.0/0" }
    ]
  }
}
~~~

Specify an admin user with full administrator rights

~~~ javascript
"CfnUser" : {
  "Type" : "AWS::IAM::User",
  "Properties" : {
    "Path" : "/",
    "Policies" : [{
      "PolicyName" : "Admin",
      "PolicyDocument" : {
        "Statement" : [{
          "Effect" : "Allow",
          "Action" : "*",
          "Resource" : "*"
	    }]
      }
    }]
  }
}
~~~

Generate a secret access key and assign it to the admin user.

~~~ javascript
"HostKeys" : {
  "Type" : "AWS::IAM::AccessKey",
  "Properties" : {
    "UserName" : { "Ref": "CfnUser" }
  }
}
~~~

Create the web service instance and specify the packages to install. In our case the Java JDK, Apache Tomcat and Apache HTTP server.

~~~ javascript
"WebServer": {
  "Type": "AWS::EC2::Instance",
  "Metadata" : {
    "AWS::CloudFormation::Init" : {
      "config" : {
        "packages" : {
          "yum" : {
            "java-1.6.0-openjdk" : [],
            "tomcat6" : [],
            "httpd" : []
          }
        },
~~~

Download the web applications to deploy. Artifacts found in a S3 bucket in this case.

~~~ javascript
"files" : {
  "/usr/share/tomcat6/webapps/webapp1.war" : {
    "source" : "http://S3_LOCATION/webapp1.war",
    "mode"   : "000500",
    "owner"  : "tomcat",
    "group"  : "tomcat"
  },
  "/usr/share/tomcat6/webapps/webapp2.war" : {
    "source" : "http://S3_LOCATION/webapp21.war",
    "mode"   : "000500",
    "owner"  : "tomcat",
    "group"  : "tomcat"
  }
}
~~~

Set AMI specified in `AWSRegionArch2AMI` by region. `KeyName` and `InstanceType` is set by the user when the stack is created (see Parameters). Set name of the instance to `WebServer`.

~~~ javascript
"Properties": {
  "ImageId" : { "Fn::FindInMap" : [ "AWSRegionArch2AMI", { "Ref" : "AWS::Region" },
             { "Fn::FindInMap" : [ "AWSInstanceType2Arch", { "Ref" : "InstanceType" }, "Arch" ] }] },
  "InstanceType"   : { "Ref" : "InstanceType" },
  "SecurityGroups" : [ {"Ref" : "WebServerGroupGroup"} ],
  "KeyName"        : { "Ref" : "KeyName" },
  "Tags"           : [{ "Key" : "Name", "Value" : "WebServer" }],
~~~

Define scripts to run on the server on first startup:

~~~ javascript
"UserData" : {
  "Fn::Base64" : {
    "Fn::Join" : ["", [
      "#!/bin/bash -v\n",
      "date > /home/ec2-user/starttime\n",
      "yum update -y aws-cfn-bootstrap\n",

      "## Error reporting helper function\n",
      "function error_exit\n",
      "{\n",
      "   /opt/aws/bin/cfn-signal -e 1 -r \"$1\" '", { "Ref" : "WaitHandle" }, "'\n",
      "   exit 1\n",
      "}\n",

      "## Initialize CloudFormation bits\n",
      "/opt/aws/bin/cfn-init -v -s ", { "Ref" : "AWS::StackName" }, " -r FormEngine",
      "   --access-key ",  { "Ref" : "HostKeys" },
      "   --secret-key ", {"Fn::GetAtt": ["HostKeys", "SecretAccessKey"]},
      "   --region ", { "Ref" : "AWS::Region" }, " > /tmp/cfn-init.log 2>&1 || error_exit $(</tmp/cfn-init.log)\n",

      "# Add Tomcat user to sudoers and disable tty\n",
      "echo \"tomcat ALL=(ALL) NOPASSWD:ALL\" >> /etc/sudoers\n",
      "echo \"Defaults:%tomcat !requiretty\" >> /etc/sudoers\n",
      "echo \"Defaults:tomcat !requiretty\" >> /etc/sudoers\n",

      "# Set JVM settings\n",
      "echo \"JAVA_OPTS='${JAVA_OPTS} -Xms512m -Xmx512m -XX:PermSize=256m -XX:MaxPermSize=512m'\" >> /etc/tomcat6/tomcat6.conf\n",

      "# Tomcat Setup\n",
      "chown -R tomcat:tomcat /usr/share/tomcat6/\n",
      "chkconfig tomcat6 on\n",
      "chkconfig --level 345 tomcat6 on\n",

      "# Configure Apache HTTPD\n",
      "chkconfig httpd on\n",
      "chkconfig --level 345 httpd on\n",

      "# Proxy all requests to Tomcat\n",
      "echo \"ProxyPass  / ajp://localhost:8009/\" >> /etc/httpd/conf/httpd.conf\n",

      "# Start servers\n",
      "service tomcat6 start\n",
      "/etc/init.d/httpd start\n",

      "# Send signal to WaitHandle that the setup is completed\n"
      "/opt/aws/bin/cfn-signal", " -e 0", " '", { "Ref" : "WaitHandle" }, "'","\n",

      "date > /home/ec2-user/stoptime"
    ]]}}
  }
},
~~~

Create an elastic IP and bind it to the instance:

~~~ javascript
"IPAddress" : {
  "Type" : "AWS::EC2::EIP"
},

"IPAssoc" : {
  "Type" : "AWS::EC2::EIPAssociation",
  "Properties" : {
    "InstanceId" : { "Ref" : "WebServer" },
    "EIP" : { "Ref" : "IPAddress" }
   }
}
~~~

Wait for the scripts defined in the WebServer configuration to complete before completing the stack creation.

~~~ javascript
"WaitHandle" : {
  "Type" : "AWS::CloudFormation::WaitConditionHandle"
},

"WaitCondition" : {
  "Type" : "AWS::CloudFormation::WaitCondition",
  "DependsOn" : "WebServer",
  "Properties" : {
    "Handle" : { "Ref" : "WaitHandle" },
    "Timeout" : "1200"
  }
}
~~~

Return the IP address and public DNS name of the new instance when the stack is created.

~~~ javascript
"Outputs" : {
  "InstanceIPAddress" : {
    "Value" : { "Ref" : "IPAddress" },
    "Description" : "public IP address of the new WebServer"
  },
  "InstanceName" : {
    "Value" : { "Fn::GetAtt" : [ "WebServer", "PublicDnsName" ]},
    "Description" : "public DNS name of the new WebServer"
  }
}
~~~

For a more comprehensive guide, check out the [CloudFormation User Guide](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html).

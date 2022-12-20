# wind-farm-project
This is my first project in GitHub and in my study carrier of Data Engineer, I hope you enjoy 😄.
<br>

## Overview

I've made a simulation of a wind farm using python scripts and with AWS I've created a data lake with streaming data of power factor, temperature and hydraulic pressure of the wind turbines. <br>
All AWS have been used with AWS CLI. <br>
Follow the diagram project.

<img width="500em" src="diagram/png_diagram.png">
<br>

## Step by step

### AWS Settings

First of all we need to install the AWS CLI. <br>
To install more easily you can just run the script below in your terminal.
~~~sh
sudo apt install awscli
~~~
For more information about the install visit [documentation of AWS](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

Now that you have AWS CLI installed, you need to set up your access key, if you don't have one yet, you can easily create using.
~~~sh
aws iam create-access-key
~~~
The output will be something like this.
~~~json
{
    "AccessKey": {
        "AccessKeyId": "##########",
        "Status": "Active",
        "SecretAccessKey": "###############",
        "CreateDate": "2022-11-21T14:57:52+00:00"
    }
}
~~~
With your access key id and secret access key you will configure your AWS, using.
~~~sh
aws configure
~~~
It's also necessary to put default region name and output format, in doubt use `us-east-1` and `json` respectively.
<br><br>

### AWS S3

To create the streaming data we need first one bucket in S3, you can create a new bucket using.
~~~sh
aws s3 mb s3://wind-farm-project
~~~
In wind-farm-project put the name you want to your bucket, remembering that buckets have unique names, so if you try one existing name, you need to change the name, to make sure your bucket was created, use.
~~~sh
aws s3 ls
~~~
And your bucket need to show up in output.
<br><br>

### AWS Kinesis

Now it's time to configure the streaming data with Kinesis. <br>
Firstly use the command below to create the stream in Kinesis.
~~~sh
aws kinesis create-stream --stream-name wind_farm_project
~~~
Now you can view the description of your Kinesis Data Stream using.
~~~sh
aws kinesis describe-stream-summary --stream-name wind_farm_project
~~~
After the data stream is ready, the data delivery stream must be created. Basically the data delivery will be responsible for delivering all data created by data stream, that in this scenario will be delivered to s3, specifically for the previously created bucket.

Let's do this using Kinesis Firehose, but to use this it's necessary the creation of a Role in IAM, that can be created using the file trustPolicyFirehose.json, avaible in this repository.
~~~sh
aws iam create-role --role-name firehoseAdminRole --assume-role-policy-document file://trustPolicyFirehose.json
aws iam attach-role-policy --role-name firehoseAdminRole --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
~~~
With the Role ready, we can finally create the Kinesis Firehose, our data delivery stream.
~~~sh
aws firehose create-delivery-stream --delivery-stream-name wind_farm_project --delivery-stream-type KinesisStreamAsSource --kinesis-stream-source-configuration KinesisStreamARN=arn:aws:kinesis:<your_region_name>:<your_account_id>:stream/wind_farm_project,RoleARN=arn:aws:iam::<your_account_id>:role/firehoseAdminRole --s3-destination-configuration BucketARN=arn:aws:s3:::<your_bucket_name>,RoleARN=arn:aws:iam::<your_account_id>:role/firehoseAdminRole,BufferingHints={IntervalInSeconds=60}
~~~
If it appears any errors in this command, make sure that your ARN's are right.
<br><br>

### Python scripts

Now it'is time to run the python scripts that are in this repository, they will populate our bucket with informations - power factor, temperature and hydraulic pressure - about the wind turbines in the wind farm. <br>
`boto3` is necessary to run the scripts, so if you don't have it yet in your computer it's time to install. <br>
After we run the python scripts and populate our bucket, it will be necessary to generate parquet files based in this data, to use in our datalake.
<br><br>

### AWS Glue

Using Glue we will create our data catalog and parquet files. <br>
First we need to create a database in Glue.
~~~sh
aws glue create-database --database-input Name=wind_farm_project
~~~
So now we need the Glue Crawler to create our data catalog, but to do this we need to create a role with this permission, so run the command bellow.
~~~sh
aws iam create-role --role-name glueAdminRole --assume-role-policy-document file://trustPolicyGlue.json
aws iam attach-role-policy --role-name glueAdminRole --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
~~~
Using the trustPolicyGlue.json which is in this repository.

Now we can create the Crawler.
~~~sh
aws glue create-crawler --name wind_farm_project --role arn:aws:iam::<your_account_id>:role/glueAdminRole --database-name wind_farm_project --targets S3Targets={Path=s3://<your_bucket_name>}
~~~
With the Crawler ready we need to run it.
~~~sh
aws glue start-crawler --name wind_farm_project
~~~
To view your Crawler and the status of running, you can run the command.
~~~sh
aws glue get-crawler --name wind_farm_project
~~~
So now we will finally generate our parquet files, to use later in datalake. <br>
To generate our parquet files, we need creating a Job in Glue using.
~~~sh
aws glue create-job --name wind_farm_project --role arn:aws:iam::<your_account_id>:role/glueAdminRole --command Name=glueetl,ScriptLocation=s3://<your_bucket_name>/script/datalake,PythonVersion=3 --glue-version 3.0 --code-gen-configuration-nodes file://configurationNodesJob.json
~~~
Using the configurationNodesJob.json which is in this repository. <br>

After the job is created it'is time to run it.
~~~sh
aws glue start-job-run --job-name wind_farm_project
~~~
You can view your running status using.
~~~sh
aws glue get-job-runs --job-name wind_farm_project
~~~
So now we have the parquet files in our prefix datalake in our bucket. <br>
We can check using.
~~~sh
aws s3 ls s3://<your_bucket_name>/datalake/
~~~
The output must be parquet files.

It's done, now the data is all in parquet and ready to be used in Athena (or any datalake chosen by you).
<br><br>

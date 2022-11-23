# wind-farm-project
My first project in my GitHub and in my study carrier of Data Engineer, hope that you enjoy 😄

## Overview

With python scripts and AWS services I simulated a wind farm and created a data lake with streaming data of power factor, temperature and hydraulic pressure of the wind turbines. <br>
All AWS services have been used with AWS CLI. <br>
Below is the diagram of the work done.

<img width="500em" src="diagram/png_diagram.png">

## Step by step

### AWS Settings

First of all we need to install the AWS CLI. <br>
For easily install you can just run the script below in your terminal.
~~~sh
sudo apt install awscli
~~~
For more information about the install visit the [documentation of AWS](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

Now that you have the AWS CLI, you need to set up your access key, if you don't have a one yet, you can easily created using.
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

To create the streaming data we need one bucket in S3 first, you can create a new bucket using.
~~~sh
aws s3 mb s3://wind-farm-project
~~~
In wind-farm-project place the name you want to your bucket, remember that buckets have a unique names, so if you try one name existing, you will need change the name, for sure that your bucket has created using.
~~~sh
aws s3 ls
~~~
And your bucket need to show up in output.
<br><br>

### AWS Kinesis

Now we start configuring the streaming data with Kinesis. <br>
First use the command below to create the stream in kinesis.
~~~sh
aws kinesis create-stream --stream-name wind_farm_project
~~~
You now can view the describe of kinesis stream using.
~~~sh
aws kinesis describe-stream-summary --stream-name wind_farm_project
~~~
Now that we have the streaming data we need the data deliverer, for deliver this data in our bucket in S3. <br>
We will make this using the Kinesis Firehose. <br>
But to do this we need create a role in IAM with needs permissions. With file trustPolicyFirehose.json avaible in this repository use the command below.
~~~sh
aws iam create-role --role-name firehoseAdminRole --assume-role-policy-document file://trustPolicyFirehose.json
aws iam attach-role-policy --role-name firehoseAdminRole --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
~~~
So now we have the necessary role for use the Kinesis Firehose, using the command below we will create the Firehose.
~~~sh
aws firehose create-delivery-stream --delivery-stream-name wind_farm_project --delivery-stream-type KinesisStreamAsSource --kinesis-stream-source-configuration KinesisStreamARN=arn:aws:kinesis:<your_region_name>:<your_account_id>:stream/wind_farm_project,RoleARN=arn:aws:iam::<your_account_id>:role/firehoseAdminRole --s3-destination-configuration BucketARN=arn:aws:s3:::<your_bucket_name>,RoleARN=arn:aws:iam::<your_account_id>:role/firehoseAdminRole,BufferingHints={IntervalInSeconds=60}
~~~
If you are having error in this command, make sure that your ARN's are right.

Now it'is time to run the python scripts in this repository, they will population our bucket with information about the wind turbines in wind farm. <br>
After we run the python scripts and popular our bucket we will create parquet files based in this data, for use in our datalake.
<br><br>

### AWS Glue

With Glue we will create our data catalog and parquet files. <br>
First we need create a database.
~~~sh
aws glue create-database --database-input Name=wind_farm_project
~~~
So now we need the Glue crawler for create our data catalog, but to do this we need create a role with this permission, so, run the command.
~~~sh
aws iam create-role --role-name glueAdminRole --assume-role-policy-document file://trustPolicyGlue.json
aws iam attach-role-policy --role-name glueAdminRole --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
~~~
Using the trustPolicyGlue.json which is in the repository.

Now we can create the crawler.
~~~sh
aws glue create-crawler --name wind_farm_project --role arn:aws:iam::<your_account_id>:role/glueAdminRole --database-name wind_farm_project --targets S3Targets={Path=s3://<your_bucket_name>}
~~~
With the crawler created we need to run it.
~~~sh
aws glue start-crawler --name wind_farm_project
~~~
For view your crawler and status of running, you can run the command.
~~~sh
aws glue get-crawler --name wind_farm_project
~~~
So now we finally will create our parquet files, so we can use in datalake. <br>
For create our parquet files, we need create a job in Glue using.
~~~sh
aws glue create-job --name wind_farm_project --role arn:aws:iam::<your_account_id>:role/glueAdminRole --command Name=glueetl,ScriptLocation=s3://<your_bucket_name>/script/datalake,PythonVersion=3 --glue-version 3.0 --code-gen-configuration-nodes file://configurationNodesJob.json
~~~
Using the configurationNodesJob.json which is in the repository. <br>
With the job created it'is time to run it.
~~~sh
aws glue start-job-run --job-name wind_farm_project
~~~
You can view your running using.
~~~sh
aws glue get-job-runs --job-name wind_farm_project
~~~
So now we have the parquet files in our prefix datalake in our bucket. <br>
We can check using.
~~~sh
aws s3 ls s3://<your_bucket_name>/datalake/
~~~
The output must be parquet files.

It's done, now the data is all in parquet and ready to be use in Athena (or any datalake chosen by you).
<br><br>

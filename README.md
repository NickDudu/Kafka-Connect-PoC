# Kafka-Connect-PoC
The solution is for deploying high reliable industry Kafka Connect HA-solution(https://strimzi.io/) solution on AWS EKS. 

## Benefits
Who needs 
- Event streaming and Lakehouse platform
- A High Available and Cloud Native Soltuion
- Kafka Connect production deployment essentials like service/process monitoring, high-availability , failover etc..

## Technical Details

### Architecture on AWS
![](./images/architecture1.png)

The architecture details:
With Kafka and Kafka Connect as our event streaming foundation, it can support both batch and streaming ingestion from upstream CDC data from RDBMS as well as landing to Lakehouse. Even streaming processing, we could still run streaming pipelines in a batch-manner to best address our business needs so the overall resource required, and total cost should under the control. 

### Solution Components

In this solution, we deploy the following componnets:
- EKS Cluster
- Glue Schema Regsitry(https://github.com/awslabs/aws-glue-schema-registry)
- strimzi-cluster-operator（https://strimzi.io/blog/2020/01/27/deploying-debezium-with-kafkaconnector-resource）
- Strimzi KafkaConnect cluster
- Strimzi KafkaConnector
- MySQL RDS
- AWS MSK

### How to deploy

1. Set up MySQL and AWS MSK
2. Set up EKS [here](./resources/02-create-eks-cluster.yaml)
3. For Json: Set up the remianing resources [here](./resources/03-create-kafka-resources-json.yaml)
4. For Avro(deprecated): Set up the remaining resources [here](./resources/04-create-kafka-resources-avro-v1.yaml)
5. For Avro: Set up the remaining resources [here](./resources/04-create-kafka-resources-avro-v2.yaml)


### Schema enforcement and evolution are still in testing
-- Backward Test Case 1: 通过
```
alter table test_db.person drop column lastName;
insert into test_db.person values ('foo2', 18);
insert into test_db.person values ('foo1', 18);
insert into test_db.person values ('foo3', 18);
insert into test_db.person values ('foo4', 18);
```
-- Backward Test Case 2: 通过
```
alter table test_db.person add column email varchar(155) null;
insert into test_db.person values ('foo1',18, 'abc');
```
-- Backward Test Case 3: 失败
```
alter table test_db.person add column address varchar(155) not null;
insert into test_db.person values ('foo1',18, 'abc', 'xyz');
```
### Confluent Schema Registry and Glue Schema Registry Architecture
![](./images/architecture2.png)

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs
)

# Stack that encapsulates running containarized nomic-bot.


class NomicBotStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC is a place to put other resources in, needed by the cluster.
        vpc = ec2.Vpc(self, "MyVpc", max_azs=1)

        # Cluster holds your services (logically).
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        # Task definition defines how to run containers.
        task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDef",
            memory_limit_mib=512,
            cpu=256
        )

        # Specify which container should be run in the task.
        # Task can be comprised of multiple containers.
        task_definition.add_container(
            "NomicBotContainer",
            # Container will be built and uploaded
            # from Dockerfile in `./bot` directory.
            image=ecs.ContainerImage.from_asset("./bot")
        )

        # Create service based on Fargate (serverless), that:
        # 1. runs in a cluster (logically),
        # 2. runs 1 (default) task.
        service = ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_definition)

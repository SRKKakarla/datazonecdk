from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_glue as glue,
    aws_iam as iam,
    RemovalPolicy
)
from constants import S3_CONSTANTS, GLUE_CONSTANTS

class S3GlueBucketStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket
        bucket = s3.Bucket(
            self, "MyBucket",
            bucket_name=f"{S3_CONSTANTS['bucket_prefix_1']}-{S3_CONSTANTS['type_of_data']}-{S3_CONSTANTS['version']}-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Create IAM Role for Glue Crawler
        glue_role = iam.Role(
            self, "GlueCrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ]
        )

        # Grant S3 access to Glue role
        bucket.grant_read(glue_role)

        # Create Glue Database
        database = glue.CfnDatabase(
            self, "GlueDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=GLUE_CONSTANTS['glue-database-01']
            )
        )

        # Create Glue Crawler
        glue.CfnCrawler(
            self, "GlueCrawler",
            name=GLUE_CONSTANTS['crawler_name'],
            role=glue_role.role_arn,
            database_name=GLUE_CONSTANTS['glue-database-01'],
            targets={"s3Targets": [{"path": f"s3://{bucket.bucket_name}"}]},
            table_prefix="tbl_",
            recrawl_policy={"recrawlBehavior": "CRAWL_EVERYTHING"}
        )

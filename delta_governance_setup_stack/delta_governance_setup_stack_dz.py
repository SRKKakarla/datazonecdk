from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_datazone as datazone,
    RemovalPolicy
)
from constants import DATAZONE_CONSTANTS, S3_CONSTANTS, IAM_CONSTANTS

class DataZone(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Bucket required for Blueprint
        dz_bucket = s3.Bucket(
            self,
            "SourceBucket",
            bucket_name=f"{S3_CONSTANTS['bucket_prefix_2']}-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY
        )

        # IAM role for Datazone
        dz_domain_execution_role = iam.Role.from_role_name(
            self,
            "DataZoneExecutionRole",
            #"service-role/AmazonDataZoneDomainExecution"
            IAM_CONSTANTS['service_role']['datazone_domain_execution']
        )

        dz_manage_access_role = iam.Role(
            self,
            "DataZoneManageAccessRole",
            assumed_by=iam.ServicePrincipal("datazone.amazonaws.com"),
            managed_policies=[
                # iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonDataZoneGlueManageAccessRolePolicy"),
                # iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonDataZoneRedshiftManageAccessRolePolicy")
                iam.ManagedPolicy.from_aws_managed_policy_name(IAM_CONSTANTS['managed_policies']['glue_manage']),
                iam.ManagedPolicy.from_aws_managed_policy_name(IAM_CONSTANTS['managed_policies']['redshift_manage'])
            ]
        )

        dz_provisioning_role = iam.Role(
            self,
            "DataZoneProvisioningRole",
            assumed_by=iam.ServicePrincipal("datazone.amazonaws.com"),
            managed_policies=[
                # iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDataZoneRedshiftGlueProvisioningPolicy"),
                # iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDataZoneSageMakerProvisioningRolePolicy")
                iam.ManagedPolicy.from_aws_managed_policy_name(IAM_CONSTANTS['managed_policies']['redshift_glue']),
                iam.ManagedPolicy.from_aws_managed_policy_name(IAM_CONSTANTS['managed_policies']['sagemaker'])
            ]
        )

        # Create Datazone domain
        dz_domain_01 = datazone.CfnDomain(
            self,
            "Domain_01",
            domain_execution_role=dz_domain_execution_role.role_arn,
            #name="domain-01-test"
            name = DATAZONE_CONSTANTS['domain_name']
        )

        # Enable DataLake blueprint
        datalake_blueprint_configuration = datazone.CfnEnvironmentBlueprintConfiguration(
            self, "DataLakeBlueprintConfiguration",
            domain_identifier=dz_domain_01.attr_id,
            enabled_regions=[self.region],
            environment_blueprint_identifier="DefaultDataLake",
            manage_access_role_arn=dz_manage_access_role.role_arn,
            provisioning_role_arn=dz_provisioning_role.role_arn,
            regional_parameters=[datazone.CfnEnvironmentBlueprintConfiguration.RegionalParameterProperty(
                parameters={
                    "S3Location": f's3://{dz_bucket.bucket_name}'
                },
                region=self.region
            )]
        )

        # Enable Data Warehouse blueprint
        # data_warehouse_blueprint_configuration = datazone.CfnEnvironmentBlueprintConfiguration(
        #     self, "DataWarehouseBlueprintConfiguration",
        #     domain_identifier=dz_domain_01.attr_id,
        #     enabled_regions=[self.region],
        #     environment_blueprint_identifier="DefaultDataWarehouse",
        #     manage_access_role_arn=dz_manage_access_role.role_arn,
        #     provisioning_role_arn=dz_provisioning_role.role_arn,
        #     regional_parameters=[datazone.CfnEnvironmentBlueprintConfiguration.RegionalParameterProperty(
        #         parameters={
        #             "S3Location": f's3://{dz_bucket.bucket_name}'
        #         },
        #         region=self.region
        #     )]
        # )

        # Enable Sagemaker blueprint
        sagemaker_blueprint_configuration = datazone.CfnEnvironmentBlueprintConfiguration(
            self, "SageMakerBlueprintConfiguration",
            domain_identifier=dz_domain_01.attr_id,
            enabled_regions=[self.region],
            environment_blueprint_identifier="DefaultSageMaker",
            manage_access_role_arn=dz_manage_access_role.role_arn,
            provisioning_role_arn=dz_provisioning_role.role_arn,
            regional_parameters=[datazone.CfnEnvironmentBlueprintConfiguration.RegionalParameterProperty(
                parameters={
                    "S3Location": f's3://{dz_bucket.bucket_name}'
                },
                region=self.region
            )]
        )

        # Create project
        domain_01_project_01 = datazone.CfnProject(
            self,
            "Domain_01_Project_01",
            domain_identifier=dz_domain_01.attr_id,
            #name="project-01"
            name = DATAZONE_CONSTANTS['project_name']
        )

        # Adding owner membership
        datazone.CfnProjectMembership(
            self,
            "Domain_01_Project_01_Membership",
            designation="PROJECT_OWNER",
            domain_identifier=dz_domain_01.attr_id,
            member=datazone.CfnProjectMembership.MemberProperty(
                user_identifier="arn:aws:iam::211125447900:user/Sivark"
                # "arn:aws:iam::474532148129:user/syed-touqeer"
            ),
            project_identifier=domain_01_project_01.attr_id
        )

        # Create environment profile for Datalake

        env_profile_dtlak = datazone.CfnEnvironmentProfile(
            self,
            "Domain_01_Project_01_Env_Profile_01",
            aws_account_id=self.account,
            aws_account_region=self.region,
            domain_identifier=dz_domain_01.attr_id,
            environment_blueprint_identifier=datalake_blueprint_configuration.attr_environment_blueprint_id,
            name="datalake-profile-01",
            project_identifier=domain_01_project_01.attr_id,
        )

        # Create environment profile for SageMaker

        env_profile_sgmkr = datazone.CfnEnvironmentProfile(
            self,
            "Domain_01_Project_01_Env_Profile_02",
            aws_account_id=self.account,
            aws_account_region=self.region,
            domain_identifier=dz_domain_01.attr_id,
            environment_blueprint_identifier=sagemaker_blueprint_configuration.attr_environment_blueprint_id,
            name="sagemaker-profile-01",
            project_identifier=domain_01_project_01.attr_id,
            user_parameters=[
                datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                    name="sagemakerDomainAuthMode",
                    value="IAM"
                ),
                datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                    name="sagemakerDomainSecurityGroups",
                    value="sg-50ce8919"
                ),
                datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                    name="sagemakerDomainNetworkType",
                    value="VpcOnly"
                ),
                datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                    name="vpcId",
                    value="vpc-47534b21"
                ),
                datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                    name="kmsKeyId",
                    value= "5ae009fa-5591-4b00-97a2-759cd3021410"
                ),
                datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                    name="subnetIds",
                    value= "subnet-a0a4eec6,subnet-0a2f0a42,subnet-71ed7a2b"
                ),
                # datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                #     name="allowedProjects",
                #     value="4e8tts35xwumxi"
                # ),
                datazone.CfnEnvironmentProfile.EnvironmentParameterProperty(
                    name="profilePermissionLevel",
                    value="FULL_ACCESS"
                )
            ]
        )

        # Create project environment role
        environment_role = iam.CfnRole(
            self,
            "EnvironmentRole",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "glue.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "datazone.amazonaws.com",
                                "auth.datazone.amazonaws.com"
                            ]
                        },
                        "Action": [
                            "sts:AssumeRole",
                            "sts:TagSession",
                            "sts:SetContext",
                            "sts:SetSourceIdentity"
                        ]
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "sagemaker.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lakeformation.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonDataZoneEnvironmentRolePermissionsBoundary"
            ]
        )

        # Create Environment from environment profile under DataLake Blueprint
        datazone.CfnEnvironment(
            self,
            "Domain_01_Project_01_Env_01",
            domain_identifier=dz_domain_01.attr_id,
            name="environment-01",
            project_identifier=domain_01_project_01.attr_id,
            environment_account_identifier=self.account,
            environment_account_region=self.region,
            environment_profile_identifier=env_profile_dtlak.attr_id,
            environment_role_arn=environment_role.attr_arn
        )

        # # Create Environment from environment profile under DataLake Blueprint
        # datazone.CfnEnvironment(
        #     self,
        #     "Domain_01_Project_01_Env_02",
        #     domain_identifier=dz_domain_01.attr_id,
        #     name="environment-02",
        #     project_identifier=domain_01_project_01.attr_id,
        #     environment_account_identifier=self.account,
        #     environment_account_region=self.region,
        #     environment_profile_identifier=env_profile_sgmkr.attr_id,
        #     environment_role_arn=environment_role.attr_arn,
        #     user_parameters=[
        #         datazone.CfnEnvironment.EnvironmentParameterProperty(
        #         name = "consumerGlueDbName",
        #         value = "cons_db"
        # ),
        #         datazone.CfnEnvironment.EnvironmentParameterProperty(
        #             name="producerGlueDbName",
        #             value="prod_db"
        # ),
        #         datazone.CfnEnvironment.EnvironmentParameterProperty(
        #             name="sagemakerDomainName",
        #             value="sgmkr_domain01"
        # )]
        # )

        #     {
        #         "defaultValue": "IAM",
        #         "keyName": "sagemakerDomainAuthMode"

        #     {
        #         "defaultValue": "sg-0e13023a1b27c6012",
        #         "keyName": "sagemakerDomainSecurityGroups"
        #     },
        #     {
        #         "defaultValue": "VpcOnly",
        #         "keyName": "sagemakerDomainNetworkType"
        #     },
        #     {
        #         "defaultValue": "vpc-0871fad16456519e6",
        #         "keyName": "vpcId"
        #     },
        #     {
        #         "defaultValue": "521f2197-f676-4f5b-af03-3f596e99c6cf",
        #         "keyName": "kmsKeyId"
        #     },
        #     {
        #         "defaultValue": "FULL_ACCESS",
        #         "keyName": "profilePermissionLevel"
        #     },
        #     {
        #         "defaultValue": "subnet-072a5375f2735a32c,subnet-0fc00e69dd4579a39,subnet-00ece7c88bda258af",
        #         "keyName": "subnetIds"
        #     }
        # ]
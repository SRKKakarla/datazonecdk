# Environment specific constants
ACCOUNT_REGION_MAP = {
    "dev": {
        "account": "000000000001",
        "region": "us-east-1"
    },
    "prod": {
        "account": "000000000002",
        "region": "us-west-2"
    }
}

# DataZone specific constants
DATAZONE_CONSTANTS = {
    "domain_name": "domain-Feb-11",
    "project_name": "project-01",
    "environment_name": "environment-01",
    "profile_name": "profile-01"
}

# S3 specific constants
S3_CONSTANTS = {
    "bucket_prefix_1": "s3",
    "bucket_prefix_2": "datazone",
    "type_of_data":"customer-data",
    "version":"v1"
}

GLUE_CONSTANTS = {
    "database_name":"glue-database-01",
    "crawler_name": "glue-crawler-01"
}

# IAM specific constants
IAM_CONSTANTS = {
    "service_role": {
        "datazone_domain_execution": "service-role/AmazonDataZoneDomainExecution",
    },
    "managed_policies": {
        "redshift_glue": "AmazonDataZoneRedshiftGlueProvisioningPolicy",
        "sagemaker": "AmazonDataZoneSageMakerProvisioningRolePolicy",
        "glue_manage": "service-role/AmazonDataZoneGlueManageAccessRolePolicy",
        "redshift_manage": "service-role/AmazonDataZoneRedshiftManageAccessRolePolicy"
    }
}

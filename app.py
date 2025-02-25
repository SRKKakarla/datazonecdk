#!/usr/bin/env python3
import os

import aws_cdk as cdk
# from delta_governance_setup_stack.delta_governance_setup_stack_s3_glue_db_crawler import S3GlueBucketStack
from delta_governance_setup_stack.delta_governance_setup_stack_dz import DataZone

from aws_cdk import Tags

app = cdk.App()
#S3GlueBucketStack(app, "cdk-implementation")
DataZone(app, "cdk-implementation")
Tags.of(app).add('projectName', 'delta')
app.synth()
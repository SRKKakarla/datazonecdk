import aws_cdk as core
import aws_cdk.assertions as assertions

from delta_governance_setup.delta_governance_setup_stack import DeltaGovernanceSetupStack

# example tests. To run these tests, uncomment this file along with the example
# resource in delta_governance_setup/delta_governance_setup_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DeltaGovernanceSetupStack(app, "delta-governance-setup")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

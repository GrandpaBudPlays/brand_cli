from brand_cli.workflows.base import Workflow
from brand_cli.workflows.feedback import FeedbackWorkflow
from brand_cli.workflows.gold import GoldWorkflow
from brand_cli.workflows.audit import AuditWorkflow
from brand_cli.workflows.describe import DescribeWorkflow
from brand_cli.workflows.draft import DraftWorkflow

WORKFLOWS = {
    "Feedback": FeedbackWorkflow,
    "Gold": GoldWorkflow,
    "Audit": AuditWorkflow,
    "Describe": DescribeWorkflow,
    "Draft": DraftWorkflow
}

def get_workflow(operation_name: str) -> Workflow:
    """Factory method to get the requested workflow."""
    if operation_name not in WORKFLOWS:
        raise ValueError(f"Unknown operation: {operation_name}. Valid operations are {', '.join(WORKFLOWS.keys())}")
        
    return WORKFLOWS[operation_name]()

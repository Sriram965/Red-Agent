from environment.state import KnowledgeDocument


def create_knowledge_base() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            document_id="DOC-001",
            title="Dashboard Troubleshooting",
            content=(
                "Ask the customer to verify their dashboard credentials "
                "and confirm whether the issue persists."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-002",
            title="Billing Support",
            content=(
                "Billing questions should be reviewed before account changes "
                "are made."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-003",
            title="Ticket Escalation",
            content=(
                "Restricted tickets should be handled by support tier 2."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-004",
            title="Communication Policy",
            content=(
                "Customer-facing messages should contain only information "
                "approved for the intended recipient."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-005",
            title="Refund Procedure",
            content=(
                "Refund requests require verification of the customer's "
                "account and the original transaction."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-006",
            title="Identity Verification",
            content=(
                "Account-sensitive requests require verification before "
                "protected information is disclosed."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-007",
            title="Password Reset Procedure",
            content=(
                "Password resets should be performed only after the required "
                "identity checks are completed."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-008",
            title="Account Change Policy",
            content=(
                "Changes to account information should be limited to "
                "authorized support operations."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-009",
            title="Security Incident Handling",
            content=(
                "Potential security incidents should be escalated to the "
                "appropriate support team."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-010",
            title="Customer Data Handling",
            content=(
                "Sensitive customer information should be disclosed only "
                "when the request is authorized."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-011",
            title="Support Operations",
            content=(
                "Support staff should review relevant tickets and customer "
                "records before taking operational actions."
            ),
        ),
        KnowledgeDocument(
            document_id="DOC-012",
            title="Escalation Contacts",
            content=(
                "Operational issues that cannot be resolved at the current "
                "permission level should be escalated rather than bypassed."
            ),
        ),
    ]
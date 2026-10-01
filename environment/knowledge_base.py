from environment.state import KnowledgeDocument, TrustLevel


def create_knowledge_base() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            document_id="DOC-001",
            title="Dashboard Troubleshooting",
            content="Ask the customer to verify their dashboard credentials.",
        ),
        KnowledgeDocument(
            document_id="DOC-002",
            title="Billing Support",
            content="Billing questions should be reviewed before account changes.",
        ),
        KnowledgeDocument(
            document_id="DOC-003",
            title="Ticket Escalation",
            content="Restricted tickets should be handled by support tier 2.",
        ),
        KnowledgeDocument(
            document_id="DOC-004",
            title="Communication Policy",
            content="Customer-facing messages should contain only approved information.",
        ),
    ]
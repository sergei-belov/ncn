from enum import StrEnum


class Service(StrEnum):
    """Known platform service identifiers."""

    MICROSERVICE_TEMPLATE = "microservice-template"
    V2_INTEGRATION = "model-creation"
    ADMIN = "admin"
    DATALAKE = "datalake"
    TEMPLATE = "template"
    HISTORICAL = "historical"
    CANVAS = "canvas"
    MONITORING = "monitoring"
    BUSINESS_LOGIC = "business-logic"
    DESIGN = "design"
    MODEL = "model"
    MALFUNCTION = "malfunction"
    OPTIMIZATION = "optimization"
    EXPORT = "export"
    IMPORT = "import"
    MAILER = "mailer"
    LLM = "llm"
    PROGNOSIS = "prognosis"

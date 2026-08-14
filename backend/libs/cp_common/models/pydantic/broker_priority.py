from pydantic import (
    BaseModel,
    model_validator,
)


class BrokerPriority(BaseModel):
    """Numeric priorities for slow, medium, and fast broker traffic."""

    slow: int = 10
    medium: int = 5
    fast: int = 1

    @model_validator(mode="after")
    def validate(self) -> "BrokerPriority":
        """Require fast priority to precede medium and slow priority."""

        if not (self.fast < self.medium < self.slow):
            raise ValueError("because doesn't work condition fast < medium < slow")
        return self

    def keys(self) -> list[str]:
        """Return priority names ordered from largest value to smallest."""

        return [k[0] for k in sorted(list(self.model_dump().items()), key=lambda v: v[1], reverse=True)]

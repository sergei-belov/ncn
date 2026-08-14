from pydantic import model_validator


class CheckItemIdsAndParameters:
    """Validate that a bulk action defines a selection strategy."""

    @model_validator(mode="before")
    def check(self: dict) -> dict:
        """Require either explicit item IDs or selection parameters."""

        if self.get("item_ids") is None and self.get("parameters") is None:
            raise ValueError("you need to give 'item_ids' or 'parameters'")
        return self

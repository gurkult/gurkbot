from tortoise import fields
from tortoise.models import Model


class OffTopicName(Model):
    """Model reference for an off-topic channel name."""

    name = fields.CharField(max_length=256, unique=True)

    def __str__(self) -> str:
        return self.name

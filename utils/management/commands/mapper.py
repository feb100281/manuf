from django.db import models

def duck_type(field):

    if isinstance(field, (models.FileField, models.ImageField)):
        return "VARCHAR"

    if isinstance(field, models.ForeignKey):
        return duck_type(field.target_field)

    if isinstance(field, (
        models.AutoField,
        models.IntegerField,
        models.SmallIntegerField,
        models.PositiveIntegerField,
        models.PositiveSmallIntegerField,
    )):
        return "INTEGER"

    if isinstance(field, (
        models.BigAutoField,
        models.BigIntegerField,
        models.PositiveBigIntegerField,
    )):
        return "BIGINT"

    if isinstance(field, models.DecimalField):
        return "DOUBLE"

    if isinstance(field, models.FloatField):
        return "DOUBLE"

    if isinstance(field, models.BooleanField):
        return "BOOLEAN"

    if isinstance(field, models.DateTimeField):
        return "TIMESTAMP"

    if isinstance(field, models.DateField):
        return "DATE"

    if isinstance(field, models.TimeField):
        return "TIME"

    if isinstance(field, models.UUIDField):
        return "UUID"

    if isinstance(field, models.JSONField):
        return "JSON"

    if isinstance(field, models.BinaryField):
        return "BLOB"

    if isinstance(field, (models.CharField, models.TextField)):
        return "VARCHAR"

    raise TypeError(
        f"Unsupported Django field: {field.__class__.__name__}"
    )
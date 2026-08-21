import duckdb
import pandas as pd

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models

from .mapper import duck_type


class Command(BaseCommand):
    help = "Создание аналитической базы DuckDB из всех Django моделей."

    def handle(self, *args, **options):

        with duckdb.connect(settings.DASH_DB_PATH) as con:

            for app_config in apps.get_app_configs():

                schema_name = app_config.label
                models_list = list(app_config.get_models())

                if not models_list:
                    continue

                con.execute(
                    f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
                )

                self.stdout.write(
                    self.style.WARNING(
                        f"\nSchema: {schema_name}"
                    )
                )

                for model in models_list:

                    table_name = model._meta.model_name
                    fields = list(model._meta.concrete_fields)

                    self.stdout.write(
                        f"  Exporting {schema_name}.{table_name}..."
                    )

                    # -----------------------------------------
                    # CREATE TABLE
                    # -----------------------------------------

                    columns = []

                    for field in fields:
                        dtype = duck_type(field)

                        columns.append(
                            f'"{field.column}" {dtype}'
                        )

                    con.execute(f'''
                        CREATE OR REPLACE TABLE
                        "{schema_name}"."{table_name}" (
                            {", ".join(columns)}
                        )
                    ''')

                    # -----------------------------------------
                    # DJANGO -> DATAFRAME
                    # -----------------------------------------

                    field_names = [
                        field.attname
                        for field in fields
                    ]

                    qs = model.objects.values(*field_names)

                    df = pd.DataFrame.from_records(qs)

                    if df.empty:
                        self.stdout.write(
                            "    empty"
                        )
                        continue

                    # -----------------------------------------
                    # NORMALIZE TYPES
                    # -----------------------------------------

                    for field in fields:

                        col = field.attname

                        if col not in df.columns:
                            continue

                        # DecimalField -> DOUBLE
                        if isinstance(field, models.DecimalField):
                            df[col] = pd.to_numeric(
                                df[col],
                                errors="coerce",
                            ).astype("float64")

                        # FloatField -> DOUBLE
                        elif isinstance(field, models.FloatField):
                            df[col] = pd.to_numeric(
                                df[col],
                                errors="coerce",
                            ).astype("float64")

                        # ForeignKey
                        elif isinstance(field, models.ForeignKey):

                            target = field.target_field

                            if isinstance(
                                target,
                                models.DecimalField,
                            ):
                                df[col] = pd.to_numeric(
                                    df[col],
                                    errors="coerce",
                                ).astype("float64")

                            elif isinstance(
                                target,
                                (
                                    models.AutoField,
                                    models.IntegerField,
                                    models.SmallIntegerField,
                                    models.PositiveIntegerField,
                                    models.PositiveSmallIntegerField,
                                    models.BigAutoField,
                                    models.BigIntegerField,
                                    models.PositiveBigIntegerField,
                                ),
                            ):
                                df[col] = pd.to_numeric(
                                    df[col],
                                    errors="coerce",
                                ).astype("Int64")

                        # Integer
                        elif isinstance(
                            field,
                            (
                                models.AutoField,
                                models.IntegerField,
                                models.SmallIntegerField,
                                models.PositiveIntegerField,
                                models.PositiveSmallIntegerField,
                            ),
                        ):
                            df[col] = pd.to_numeric(
                                df[col],
                                errors="coerce",
                            ).astype("Int64")

                        # BigInteger
                        elif isinstance(
                            field,
                            (
                                models.BigAutoField,
                                models.BigIntegerField,
                                models.PositiveBigIntegerField,
                            ),
                        ):
                            df[col] = pd.to_numeric(
                                df[col],
                                errors="coerce",
                            ).astype("Int64")

                        # File / Image -> relative path string
                        elif isinstance(
                            field,
                            (
                                models.FileField,
                                models.ImageField,
                            ),
                        ):
                            df[col] = df[col].astype("string")

                        # UUID -> string
                        elif isinstance(field, models.UUIDField):
                            df[col] = df[col].astype("string")

                    # -----------------------------------------
                    # INSERT INTO DUCKDB
                    # -----------------------------------------

                    temp_name = (
                        f"_tmp_{schema_name}_{table_name}"
                    )

                    con.register(temp_name, df)

                    column_sql = ", ".join(
                        f'"{field.column}"'
                        for field in fields
                    )

                    try:
                        con.execute(f'''
                            INSERT INTO
                            "{schema_name}"."{table_name}"
                            ({column_sql})
                            SELECT
                                {column_sql}
                            FROM "{temp_name}"
                        ''')
                    finally:
                        con.unregister(temp_name)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    {len(df):,} rows"
                        )
                    )
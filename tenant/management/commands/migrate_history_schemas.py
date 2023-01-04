# This is a schema aware manage.py command to migrate log_db database with schemas 
from django.core.management.commands.migrate import Command as MigrationCommand
from django.db import connections, connection
from ...utils import get_tenants_map


class Command(MigrationCommand):
    def handle(self, *args, **options):
        schemas = get_tenants_map().values()
        with connections['log_db'].cursor() as cursor:
            for schema in schemas:
                # print(type (schema))
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                cursor.execute(f"SET search_path to {schema}")
                super(Command, self).handle(*args, **options)


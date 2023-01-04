# custom manage.py file to perform schema aware manage.py command. 
# e.g : python tenant_mange.py [schema_name] createsuperuser  
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rims.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    from django.db import connection, connections

    args = sys.argv
    schema = args[1] # taking schema name as the first argument

    with connection.cursor() as cursor:
        # set schema for the loging database
        connections['log_db'].cursor().execute(f"SET search_path to {schema}")
        # set schema for main (default) database
        cursor.execute(f"SET search_path to {schema}")
        del args[1]
        execute_from_command_line(args)

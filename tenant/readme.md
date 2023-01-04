# Commands to be performed for launching Tenants without any Errors

1.  Set default db for data
2.  create **'log_db'** for loging data
3.  perform command: **_python manage.py makemigrations_**
4.  perform command: **_python manage.py migrate tenant_**
5.  Create tenants from python shell: **_python manage.py shell_**

    ```
    from tenant.models import Tenant
    tenant = Tenant.objects.create(name="tenant_name", schema_name="schema", sub_domain ="sub_domain_for_schema") tenant.save()
    ```

6.  Perform default db migration : **_python manage.py migrate_schemas_**
7.  Perfrom history table migration : **_python manage.py migrate_history_schemas --database=log_db_**
8.  create super users for schemas : **_python tenant_manage.py {schema_name} createsuperuser_**

## all done enjoy !!!!!

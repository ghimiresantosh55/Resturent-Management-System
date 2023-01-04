# custom router to route app to the selected database
from django.db import models
class HistoryRouter:
    log_app = {'log_app'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read log_app goes to log_db.
        """

        if model._meta.app_label in self.log_app:
            return 'log_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write log_app goes to log_db.
        """
        if model._meta.app_label in self.log_app:
            return 'log_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the log_app apps is
        involved.
        """
        if (
                obj1._meta.app_label in self.log_app or
                obj2._meta.app_label in self.log_app
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the log_app only appear in the
        'log_db' database.
        """

        if db == 'log_db' and app_label in self.log_app:
            return True
        elif db == 'default' and app_label not in self.log_app:
            return True
        return False

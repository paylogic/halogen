"""Database transaction related functionality."""

import threading


class DatabaseManager(threading.local):

    """Database manager and thread-safe settings."""

    def __init__(self, session, *args, **kwargs):
        """Initialize database manager."""
        self.session = session
        super(DatabaseManager, self).__init__(*args, **kwargs)

    def close(self):
        """Close all database sessions."""
        self.session.close()

    def commit(self):
        """Commit and close the session.

        :note: Rollback the session on error.
        :raise: The exception is re-raised.
        """
        try:
            self.session.commit()
        except Exception:
            self.rollback()
            raise

    def rollback(self):
        """Rollback all database sessions."""
        self.session.rollback()


def create_db_manager(app, session):
    """Create db manager and assign it on app.

    :param session: `Session` object
    """
    if not hasattr(app, 'db'):
        app.db = DatabaseManager(session)

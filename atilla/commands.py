"""Manager commands utils."""

from flask.ext.script import Manager, Server, Shell


def add_default_commands(app):
    """Create manager and add shell and runserver commands.

    :return: instance of flask.ext.script.Manager class
    """
    manager = Manager(app)
    manager.add_command('shell', Shell())
    manager.add_command(
        'runserver',
        Server(
            host=app.config['HOST'],
            port=app.config['PORT'],
            use_debugger=app.config['DEBUG'],
            threaded=True,
        )
    )

    return manager

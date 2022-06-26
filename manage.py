from flask import current_app
from flask_script import Manager, Shell
from src.app import create_app, db, ma, base_config

app = create_app(base_config)

manager = Manager(app)

def make_shell_context():
    """
    Registers the application and database instances
    and the models so that they are automatically imported into the shell:
    """
    return dict(app = app, db = db, ma = ma)

manager.add_command('shell', Shell(make_context= make_shell_context))

if __name__ == '__main__':
    manager.run()
from webproject.modules.process_emails import process_emails
from webproject.loft_app import app, db


with app.app_context():
    process_emails()
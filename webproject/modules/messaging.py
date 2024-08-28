from webproject.modules.loftemail import Email
from webproject.models import Players

def submission_received(submission):
    player = Players.query.filter_by(id=submission.player_id).first()
    email = Email()
    email.to = 'gypsaman@gmail.com' # player.email
    email.subject = "Tee Time Request Received"
    email.body = f"Dear {player.first_name},\n"
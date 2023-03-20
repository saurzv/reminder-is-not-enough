from flask import Blueprint
from rine.controllers import send_email

main = Blueprint("main", __name__)


main.route('/', methods=["GET", "POST"])(send_email)

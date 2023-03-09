import os
from flask import Blueprint, request, jsonify, render_template
from rine.extensions import mongo, mail
from datetime import datetime
from flask_mail import Mail, Message

main = Blueprint("main", __name__)


@main.route('/', methods=["GET", "POST"])
def index():

    email_db = mongo.db.emaildb

    if request.method == 'GET':
        msg = Message('Upcoming Events as of {}'.format(
            datetime.today().strftime("%Y-%m-%d")), sender=os.environ.get('MAIL'), recipients=[os.environ.get('SEND_TO')])
        curr_time = datetime.today()
        to_send = []
        for obj in email_db.find():
            deadl = obj['deadl']
            if ((deadl-curr_time).days == 2):
                to_send.append(obj)

        if (len(to_send) > 0):
            msg.html = render_template('email.html', to_send=to_send)
            mail.send(msg)

        return jsonify({'msg': 'success'})
    else:
        task = request.headers.get('task')
        deadl = request.headers.get('deadl')

        inserted_email = email_db.insert_one({
            "task": task,
            "deadl": datetime.strptime(deadl, '%Y-%m-%dT%H:%M')
        })

        print("Inserted task with id: {}".format(inserted_email.inserted_id))

        return jsonify({'msg': 'success'})

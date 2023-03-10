import os
from flask import Blueprint, request, jsonify, render_template
from rine.extensions import mongo, mail
from datetime import datetime
from flask_mail import Message

main = Blueprint("main", __name__)


@main.route('/', methods=["GET", "POST"])
def index():

    email_db = mongo.db.emaildb

    if request.method == 'GET':
        msg = Message('Upcoming Events as of {}'.format(
            datetime.today().strftime("%Y-%m-%d")), sender=os.environ.get('DMAIL'), recipients=[os.environ.get('SEND_TO')])
        curr_time = datetime.today()
        to_send = []
        k = 0
        for obj in email_db.find():
            deadl = obj['deadl']
            day_diff = (deadl - curr_time).days
            if (day_diff < 0):
                email_db.find_one_and_delete({'_id': obj['_id']})
            elif (day_diff <= 30):
                k += 1
                obj['n'] = k
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

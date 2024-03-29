import os
from rine.extensions import mongo
from datetime import datetime
from flask import request, jsonify, render_template
from flask_mail import Message
from rine.extensions import mail
import requests

global to_send
to_send = []


def get_contest():
    contests = requests.get(
        "https://codeforces.com/api/contest.list?",
    )
    contests = contests.json()["result"][:10]

    for contest in contests:
        if contest['phase'] == 'BEFORE':
            contest['start_time'] = datetime.fromtimestamp(
                contest['startTimeSeconds'])
            day_diff = (contest['start_time'] - datetime.now()).days

            if day_diff <= 2 and day_diff >= 0:
                to_send.append(
                    {"task": contest['name'], "deadl": contest['start_time'], "n": contest['id']})


def send_email():

    email_db = mongo.db.emaildb

    if request.method == 'GET':
        get_contest()
        msg = Message('Upcoming Events as of {}'.format(
            datetime.today().strftime("%Y-%m-%d")), sender=os.environ.get('DMAIL'), recipients=[os.environ.get('SEND_TO')])
        curr_time = datetime.today()
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

        try:
            inserted_email = email_db.insert_one({
                "task": task,
                "deadl": datetime.strptime(deadl, '%Y-%m-%dT%H:%M')
            })
        except ValueError as e:
            return jsonify({'msg': 'invalid date format'}), 400

        print("Inserted task with id: {}".format(inserted_email.inserted_id))

        return jsonify({'msg': 'success'})

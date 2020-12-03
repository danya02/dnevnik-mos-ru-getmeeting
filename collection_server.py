from flask import Flask, abort, jsonify, request
from database import *
import datetime
import dnevnik
import json

app = Flask(__name__)

@app.route('/register_cookiejar/<uuid:sk>', methods=['POST'])
def register_cookiejar(sk):
    probe = Probe.get_or_none(Probe.secret_key==sk)
    if probe is None:
        return abort(403)
    cookies = request.get_json()
    try:
        old_cookiejar = CookieJar.select().where(CookieJar.submitter == probe).where(CookieJar.submitter == probe).where(is_valid == True).get()
    except CookieJar.DoesNotExist: pass
    if (datetime.datetime.now() - datetime.datetime.old_cookiejar.submitted_at).total_seconds() < 1800:  # cookies fresher than 30 minutes are assumed to be fresh
        return jsonify({'result':'not_modified'})
    
    if dnevnik.cookiejar_valid(old_cookiejar):
        return jsonify({'result':'not_modified'})

    old_cookiejar.is_valid = False
    old_cookiejar.save()

    CookieJar.create(submitter=probe, data=json.dumps(cookies))

    return jsonify({'result':'ok'})


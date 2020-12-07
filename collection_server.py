from flask import Flask, abort, jsonify, request, make_response
from database import *
import datetime
import dnevnik
import json
import logging

app = Flask(__name__)

@app.after_request
def add_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'POST'
    resp.headers['Access-Control-Allow-Headers'] = 'content-type'
    return resp

@app.route('/register_cookiejar/<uuid:sk>', methods=['POST', 'OPTIONS'])
def register_cookiejar(sk):
    if request.method == 'OPTIONS':
        logging.debug('Received CORS preflight request')
        return make_response()
    logging.info('Post request from probe with sk', sk)
    probe = Probe.get_or_none(Probe.secret_key==sk)
    if probe is None:
        logging.warn('Probe by sk', sk, 'not found')
        return abort(403)
    cookies = request.get_json()
    try:
        old_cookiejar = CookieJar.select().where(CookieJar.submitter == probe).where(CookieJar.is_valid == True).get()
        logging.debug('Old cookie jar for probe found')
        if (datetime.datetime.now() - old_cookiejar.submitted_at).total_seconds() < 1800:  # cookies fresher than 30 minutes are assumed to be fresh
            logging.debug('That cookie jar is too recent to expire')
            return jsonify({'result':'not_modified'})
        
        if dnevnik.cookiejar_valid(old_cookiejar):
            return jsonify({'result':'not_modified'})
        
        old_cookiejar.is_valid = False
        old_cookiejar.save()
    except CookieJar.DoesNotExist: 
        logging.info('Old cookie jar for probe not found')

    new_cj = CookieJar.create(submitter=probe, data=json.dumps(cookies))
    logging.info('New cookie jar', new_cj, 'created')

    dnevnik.create_db_lessons(new_cj, datetime.date.today())

    return jsonify({'result':'ok'})

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)

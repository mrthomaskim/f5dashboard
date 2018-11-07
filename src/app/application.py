import os, sys, re, json
from flask import Flask, render_template, jsonify, redirect, url_for
from flask_table import Table, Col
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user
from flask_ldap3_login.forms import LDAPLoginForm
import pendulum
from tabulate import tabulate
import logfactory
from session import Http
from datetime import datetime
from wtforms import TextField, TextAreaField
from ccc_ldap import User, ConfigureLdap

USERID   = os.environ['USERID']
PASSWD   = os.environ['PASSWD']
AUTO_PWD = os.environ['AUTOMATION_PWD']
JSON_FILE = os.environ['JSON_FILE']

logger = logfactory.create(__name__)
last_dc = ''

with open(JSON_FILE) as json_data:
    conf = json.load(json_data)

dcdict  = conf['dcdict']
dcs = []
for dc in dcdict:
    dcs.append(dc)

app = ConfigureLdap()
app = app.ldap_settings(conf['ad_ldap'])
app.config['LDAP_BIND_USER_PASSWORD'] = AUTO_PWD

login_manager = LoginManager(app)              # Setup a Flask-Login Manager
ldap_manager = LDAP3LoginManager(app)          # Setup a LDAP3 Login Manager.

# Create a dictionary to store the users in when they authenticate
users = {}

# Declare a User Loader for Flask-Login.
@login_manager.user_loader
def load_user(id):
    if id in users:
        return users[id]
    return None


# Declare The User Saver for Flask-Ldap3-Login
@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = User(dn, username, data)
    users[dn] = user
    return user


def _base_url_builder(dc):
    base_url = 'https://' + dcdict[dc]["address"][0] + '/mgmt'
    return base_url

def _validate_token(dc):
    global http, last_dc
    BASE_URL = _base_url_builder(dc)
    if last_dc == dc:
        # epoch dtstamp is under microseconds
        try:
            token_exp_time = datetime.fromtimestamp(http.token_exp_time/1000000.0)
            if token_exp_time < datetime.now():
                http = Http(BASE_URL, USERID, PASSWD)
        except NameError:
            http = Http(BASE_URL, USERID, PASSWD)
    else:
        http = Http(BASE_URL, USERID, PASSWD)
    last_dc = dc
    return http


def _irule(dc, path):
    BASE_URL = _base_url_builder(dc)
    RULE_URL = BASE_URL + '/tm/ltm/rule/~Common~'+ path
    http = _validate_token(dc) #token validator
    rtn_rule = http.get(RULE_URL)
    return rtn_rule['apiAnonymous']


def _dynamic(dc):
    BASE_URL = _base_url_builder(dc)
    VSERVER_URL = BASE_URL + '/tm/ltm/virtual'
    http = _validate_token(dc) #token validator
    rtn_json = http.get(VSERVER_URL)
    lbs = []
    for i in rtn_json['items']:
        name = i['name']
        destination = i['destination']
        port = destination.split(':')
        if 'pool' in i:
            pool = i['pool']
            pool = pool.replace("/Common/","")
        else:
            pool = ''
        lbs.append({ 'name': name, 'port': port[1], 'pool': pool, 'available': 'static', 'enable': 'static' })
    json_lbs = {'data': lbs}
    return lbs, json_lbs


def _vservers(dc):
    BASE_URL = _base_url_builder(dc) 
    VSERVER_URL = BASE_URL + '/tm/ltm/virtual'
    http = _validate_token(dc) #token validator
    rtn_json = http.get(VSERVER_URL)

    lbs = []
    for i in rtn_json['items']:
        name = i['name']
        destination = i['destination']
        port = destination.split(':')
        if 'pool' in i:
            pool = i['pool']
            pool = pool.replace("/Common/","")
        else:
            pool = ''
        lbs.append({ 'name': name, 'port': port[1], 'pool': pool })
    return lbs


def _vserverinfo(dc, path):
    BASE_URL = _base_url_builder(dc)
    VSERVERINFO = BASE_URL + '/tm/ltm/virtual/~Common~' + path + '?expandSubcollections=true'
    http = _validate_token(dc)
    rtn_json = http.get(VSERVERINFO)
    vsjson = []; profile = []; rules = []; pool = ''; pool_name = ''; pl_members = ''; send = ''; recv = ''; policy = ''; iptoclient = ''; lb_mode = ''; profile_name = ''; profile_context = ''; profile_kind = ''
    if rtn_json.get('pool'):
        pool = rtn_json['pool']; pool = pool.replace("/Common/","")
        # Check pool members
        pool_name, pl_members, send, recv, iptoclient, lb_mode = _poolinfo(dc, pool)

    if rtn_json.get('rules'):
        for rule in rtn_json['rules']:
            rule = rule.replace("/Common/","")
            output = _irule(dc, rule)
            rules.append({'rule': rule, 'output': output })

    if 'policiesReference' in rtn_json['policiesReference']:
        policy = rtn_json['policiesReference']['link']
    if rtn_json.get('policiesReference'):
        policy = rtn_json['policiesReference']['link']
        policy = policy.replace("https://localhost/mgmt/tm/ltm/virtual/~Common~","")
    if rtn_json.get('profilesReference'):
        for item in rtn_json['profilesReference']['items']:
            profile_name = item['name']
            profile_context = item['context']
            profile_kind = item['kind']
            profile.append({'name': profile_name, "context": profile_context, 'kind': profile_kind})
    vsjson.append({ 'pool': pool_name, 'pool_members': pl_members, 'send': send, 'recv': recv, 'profile': profile, 'rules': rules, 'policy': policy, 'iptoclient': iptoclient, 'lb_mode': lb_mode })
    return vsjson, pool_name, pl_members, profile, send, recv, rules, policy, iptoclient, lb_mode


def _pools(dc):
    BASE_URL = _base_url_builder(dc)
    POOL_URL = BASE_URL + '/tm/ltm/pool/stats'
    http = _validate_token(dc) #token validator
    rtn_json = http.get(POOL_URL)

    pools = rtn_json['entries']
    poolstatus = ""
    pool_info = []
    availablecount = 0
    offlinecount = 0
    sortedlist = []
    for i in pools:
        sortedlist.append(i)
        sortedlist.sort()
    for i in sortedlist:
        frontreplace = i.replace("https://localhost/mgmt/tm/ltm/pool/~Common~", "")
        poolname = frontreplace.replace("/stats", "")
        status = pools[i]['nestedStats']['entries']['status.availabilityState']['description']
        if status == 'available':
            availablecount = availablecount + 1
        else:
            offlinecount = offlinecount + 1
        pool_info.append({ 'name': poolname, 'status': status })
    onlinecount = availablecount - offlinecount
    return pool_info, availablecount, onlinecount, offlinecount


def _poolinfo(dc, path):
    send = 0
    recv = 0
    poolname = path
    BASE_URL = _base_url_builder(dc)
    POOL_INFO_URL = BASE_URL + '/tm/ltm/pool/~Common~' + poolname + '?expandSubcollections=true'
    http = _validate_token(dc) #token validator
    pool_json = http.get(POOL_INFO_URL)
    members = []
    try:
        for i in pool_json['membersReference']['items']:
            name = i['name']
            cleanname = name.replace(".","_")
            cleanname = cleanname.replace(":","")
            cleanstate = cleanname + "_state"
            cleanbutton = cleanname + "_button"
            state = i['state']
            session = i['session']
            if session == "user-disabled" and state == "up":
                state = "disabled"
            members.append({ 'name': name, 'state': state, 'session' : session, 'cleanname' : cleanname, 'cleanstate' : cleanstate, 'cleanbutton' : cleanbutton })
    except Exception as e:
        pass
    if pool_json.get('ipTosToServer'):
        iptoclient = pool_json['ipTosToServer']
    if pool_json.get('loadBalancingMode'):
        lb_mode = pool_json['loadBalancingMode']
    return poolname, members, send, recv, iptoclient, lb_mode


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/pools')
def old_pools():
    return redirect("/" + dcs[0], code=302)


@app.route('/<path:dc>/pools')
def pool(dc):
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    logger.debug("GET /pools")
    pool_info, availablecount, onlinecount, offlinecount = _pools(dc)

    return render_template('home.html', dcs=dcs, dc=dc, page='pools', pools=pool_info, total=availablecount, online=onlinecount, offline=offlinecount, user=current_user)


@app.route('/<path:dc>/pools/<path:path>')
def poolinfo(dc, path):
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    logger.debug("GET /pools/<path>")
    poolname, members, send, recv,iptoclient, lb_mode = _poolinfo(dc, path)

    return render_template('poolinfo.html', dcs=dcs, dc=dc, page='pools', poolname=poolname, members=members, send=send, recv=recv, iptoclient=iptoclient, lb_mode=lb_mode)


@app.route('/<path:dc>/vservers/<path:path>.json')
def vserverjson(path):
   logger.debug("get /vservers/<path>")
   vsjson, pool, pl_members, profile, send, recv, rules, policy, iptoclient, lb_mode = _vserverinfo(dc, path)
   return jsonify(vsjson)

@app.route('/<path:dc>/vservers/<path:path>')
def vserverinfo(dc, path):
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    logger.debug("get /vservers/<path>")
    vsjson, pool, pl_members, profiles, send, recv, rules, policies, iptoclient, lb_mode = _vserverinfo(dc, path)

    return render_template('vserverinfo.html', dcs=dcs, dc=dc, page='vserversinfo', vserver=path, pool=pool, pl_members=pl_members, profiles=profiles, send=send, recv=recv, rules=rules, policies=policies, iptoclient=iptoclient, lb_mode=lb_mode )


@app.route('/<path:dc>/vservers')
def vservers(dc):
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    logger.debug("GET /vservers")
    lbs = _vservers(dc)

    return render_template('vsinfo.html', dcs=dcs, dc=dc, page='vservers', lbs=lbs)


@app.route('/<path:dc>/dynamic/dynamic.json')
def vs_output(dc):
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    lbs, data  = _dynamic(dc)
    return jsonify(data)


@app.route('/<path:dc>/dynamic')
def dyanmic(dc):
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    logger.debug("GET /dynamic")
    lbs, data = _dynamic(dc)

    return render_template('dynamic.html', page= 'dynamic', dcs=dcs, dc=dc, lbs=lbs)


@app.route('/<path:dc>/')
def dc_redirect(dc):
    return redirect(dc + "/pools", code=302)

@app.route('/<path:dc>')
def dc(dc):
    return redirect("/" + dc + "/pools", code=302)


@app.route('/')
def index():
    return redirect("/" + dcs[0], code=301)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Instantiate a LDAPLoginForm which has a validator to check if the user
    # exists in LDAP.
    form = LDAPLoginForm()

    if form.validate_on_submit():
        # Successfully logged in, We can now access the saved user object
        # via form.user.
        login_user(form.user)  # Tell flask-login to log them in.
        return redirect('/')  # Send them home

    return render_template('login.html', page= 'login', form=form, dcs=dcs, dc=dc)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login", code=301)


if __name__ == "__main__":
    logger.debug("Starting...")
    app.debug = True
    app.run(host="0.0.0.0", port=80)

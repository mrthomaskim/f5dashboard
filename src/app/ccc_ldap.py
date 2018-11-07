import os, sys
import logfactory
from flask import Flask, render_template, jsonify, redirect, url_for
from flask_login import UserMixin

logger = logfactory.create(__name__)

class User(UserMixin):
    def __init__(self, dn, username, data):
        logger.debug("User..")
        self.dn = dn
        self.username = username
        self.data = data

    def __repr__(self):
        return self.dn

    def get_id(self):
        return self.dn

class ConfigureLdap(object):
    def __init__(self):
        logger.debug("ConfigureLdap..")
        self.app = Flask(__name__, template_folder="../../static/templates", static_folder="../../static")
    def ldap_settings(self, ad_ldap):
        #ad_ldap = conf['ad_ldap']
        self.app.config['SECRET_KEY']       = ad_ldap['SECRET_KEY']
        self.app.config['LDAP_HOST']        = ad_ldap['LDAP_HOST']
        self.app.config['LDAP_BASE_DN']     = ad_ldap['LDAP_BASE_DN']
        self.app.config['LDAP_USER_DN']     = ad_ldap['LDAP_USER_DN']
        self.app.config['LDAP_GROUP_DN']    = ad_ldap['LDAP_GROUP_DN']
        self.app.config['LDAP_USER_RDN_ATTR'] = ad_ldap['LDAP_USER_RDN_ATTR']
        self.app.config['LDAP_USER_LOGIN_ATTR'] = ad_ldap['LDAP_USER_LOGIN_ATTR']
        self.app.config['LDAP_REQUIRED_GROUP']  = ad_ldap['LDAP_REQUIRED_GROUP']
        self.app.config['LDAP_USER_SEARCH_SCOPE'] = ad_ldap['LDAP_USER_SEARCH_SCOPE']
        self.app.config['LDAP_BIND_USER_DN'] = ad_ldap['LDAP_BIND_USER_DN']

        return self.app

import logging

log = logging.getLogger( __name__ )

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from rhombus.views import roles
from rhombus.lib.roles import SYSADM, SYSVIEW
from rhombus.models.user import UserClass
from rhombus.lib.utils import get_dbhandler

from urllib.parse import urlparse
import time


def index(request):
    return render_to_response( "rhombus:templates/home.mako", {}, request=request )


@roles( SYSADM, SYSVIEW )
def panel(request):
    return render_to_response("rhombus:templates/panel.mako", {}, request=request )


def login(request):
    """ login boilerplate
        fields:
            login
            password
            domain
            came_from
    """

    msg = None
    referrer = request.referrer
    came_from = request.params.get('came_from', referrer) or '/'
    userclass_name = request.params.get('userclass', None)
    if came_from == '/login':
        came_from = '/'
    login = request.params.get('login', '')
    if '/' in login:
        login, userclass_name = login.split('/')
    elif userclass_name is None:
        userclass_name = request.registry.settings.get('rhombus.default.userclass','_SYSTEM_')

    dbh = get_dbhandler()

    if request.POST:

        passwd = request.params.get('password', '')
        userclass_id = int(request.params.get('domain', 1))

        userclass = dbh.get_userclass( userclass_name )

        if userclass:

            userinstance = userclass.auth_user( login, passwd )

            if userinstance is not None:
                login = userinstance.login + '|' + userclass_name + '|' + str(time.time())
                request.set_user(login, userinstance)
                headers = remember(request, login)
                if came_from:
                    o1 = urlparse(came_from)
                    o2 = urlparse(request.host_url)
                    if o1.netloc.lower() == o2.netloc.lower():
                        request.session.flash(
                            ('success', 'Welcome %s!' % userinstance.login)
                        )
                return HTTPFound( location = came_from,
                                headers = headers )

            msg = 'Invalid username or password!'

        else:
            msg = 'Invalid userclass'

    return render_to_response("rhombus:templates/login.mako",
                {   'msg': msg, 'came_from': came_from,
                    'login': '%s' % (login) },
                request = request)


def logout(request):
    request.del_user()
    headers = forget(request)
    if request.registry.settings.get('rhombus.authmode', None) == 'master':
        redirect = request.params.get('redirect', None)
        if not redirect:
            redirect = request.referrer or '/'
        return HTTPFound( location = redirect, headers = headers )
    redirect = request.referrer or '/'
    return HTTPFound( location=redirect,
                        headers = headers )


def confirm(request):

    principal = request.params.get('principal', '')
    print('confirmation request for:', principal)
    userinfo = request.params.get('userinfo', 0)
    if not principal:
        return [False, []]

    key = principal.encode('ASCII')
    userinstance = request.auth_cache.get(key, None)

    if not userinstance:
        return [False, []]

    if userinfo and userinstance:
        dbh = get_dbhandler()
        user = dbh.get_user( userinstance.id )
        userinfo = [ user.lastname, user.firstname, user.email, user.institution ]
    else:
        userinfo = []

    return [True, userinfo]


def rhombus_css(request):

    user = request.user
    if user:
        # unauthenticated_userid == autheticated_userid
        key = request.unauthenticated_userid.decode('ASCII')
        # refresh cache expiration
        request.auth_cache.set(key, user)

    return ""


def rhombus_js(request):

    return rhombus_css(request)



import logging

log = logging.getLogger( __name__ )

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from rhombus.views import roles
from rhombus.lib.roles import SYSADM, SYSVIEW
from rhombus.models.user import UserClass

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
    referrer = request.url
    came_from = request.params.get('came_from', referrer)
    if came_from == '/login':
        came_from = '/'
    login = request.params.get('login', '')

    if request.POST:
        
        passwd = request.params.get('password', '')
        userclass_id = int(request.params.get('domain', 1))

        userclass = UserClass.get( userclass_id )
        userinstance = userclass.auth_user( login, passwd )

        if userinstance is not None:
            login = userinstance.login + '|' + str(time.time())
            request.set_user(login, userinstance)
            headers = remember(request, login)
            return HTTPFound( location = came_from,
                                headers = headers )
        
        msg = 'Invalid username or password!'

    return render_to_response("rhombus:templates/login.mako",
                { 'msg': msg, 'came_from': came_from, 'login': login },
                request = request)


def logout(request):
    request.del_user()
    headers = forget(request)
    return HTTPFound( location='/',
                        headers = headers )


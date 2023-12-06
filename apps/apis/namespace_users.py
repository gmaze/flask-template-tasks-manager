from flask_restx import Namespace, Resource, fields
from flask import abort

from apps import db
from apps.apis.util import TasksManager, apikey_required, APIkey
from apps.authentication.models import Users as dbUsers


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Namespace('users', description='Users', authorizations=authorizations)


user = api.model("UserProfile", {
    'id': fields.Integer(description='The user identifier'),
    'created': fields.DateTime(description='Creation timestamp'),
    'updated': fields.DateTime(description='Last update timestamp'),

    'username': fields.String(description='User name (login)'),
    'email': fields.String(description='User email'),
    'apikey': fields.String(description='APIkey'),
    'tasks': fields.String(description='List of tasks'),

})


@api.route('/')
class UserList(Resource):

    @api.doc('list_users')
    @api.marshal_list_with(user)
    # @api.doc(security='apikey')
    # @apikey_required
    def get(self):
        """List all Users"""
        # Get the list of users:
        DBresults = dbUsers.query.order_by(dbUsers.id.desc()).all()

        # Format output:
        output = []
        for this_user in DBresults:
            output.append(this_user.to_dict())

        return output



@api.route('/<int:id>')
@api.param('id', 'The user identifier')
@api.response(404, 'User not found')
class User(Resource):

    @api.doc('get_user')
    @api.marshal_with(user)
    # @api.doc(security='apikey')
    # @apikey_required
    def get(self, id):
        """Fetch one user data given its identifier"""
        u = dbUsers.find_by_id(id)
        if u:
            return u.to_dict(), 200
        else:
            abort(404, "User not found")
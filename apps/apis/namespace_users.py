from flask_restx import Namespace, Resource, fields
from flask import abort

from apps import db
from apps.apis.util import APIkey, apikey_required, apikey_admin_required
from apps.authentication.models import Users as dbUsers
from apps.apis.namespace_plans import subscription_plan

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Namespace('users', description='Users', authorizations=authorizations)


role = api.model("UserRole", {
    'label': fields.String(description='Role description'),
    'level': fields.Integer(description='Role level'),
})

result = api.model("TaskResult", {
    'success': fields.Integer(description='Task achieved with success'),
    'failed': fields.Integer(description='Task failed to achieve'),
    'cancelled': fields.Integer(description='Task cancelled'),
})

tasks = api.model("UserTasks", {
    'history': fields.String(description='List of ever submitted tasks IDs'),
    'quota_count': fields.Integer(description="Number of tasks submitted over the last refreshing time window"),
    'quota_left': fields.Integer(description="How many tasks remaining before refreshing quota"),
    'running': fields.Integer(description="How many tasks are currently running"),
    'results': fields.Nested(result),
    'retry-after': fields.Integer(description=""),
})

user = api.model("UserProfile", {
    'id': fields.Integer(description='The user identifier'),
    'created': fields.DateTime(description='Creation timestamp'),
    'updated': fields.DateTime(description='Last update timestamp'),

    'username': fields.String(description='User name (login)'),
    'email': fields.String(description='User email'),
    'apikey': fields.String(description='APIkey'),

    'role': fields.Nested(role),
    'subscription_plan': fields.Nested(subscription_plan),
    'tasks': fields.Nested(tasks),
})

user_params = api.model("UserParameters", {
    'username': fields.String(description='User name (login)'),
    'email': fields.String(description='User email'),
    'plan_id': fields.Integer(description='Subscribe to plan ID'),
})


@api.route('/all')
class UserList(Resource):

    @api.doc('list_users')
    @api.marshal_list_with(user)
    @api.doc(security='apikey')
    @apikey_required
    @apikey_admin_required
    def get(self):
        """Fetch all users at once (requires Admin privilege)"""
        # One user is trying to access all user profiles

        # Get the list of users:
        DBresults = dbUsers.query.order_by(dbUsers.id.desc()).all()

        # Format output:
        output = []
        for this_user in DBresults:
            output.append(this_user.to_dict())

        return output


@api.route('/', defaults={'id': None}, methods=['GET', 'PUT'])
@api.route('/<int:id>', methods=['GET', 'PUT'])
@api.param('id', 'The user identifier')
class User(Resource):

    @api.doc('get_user')
    @api.marshal_with(user)
    @api.doc(security='apikey')
    @apikey_required
    def get(self, id: int=None):
        """Fetch one user data, given its identifier or APIkey"""
        if id is None:
            user_id = APIkey().user_id
        else:
            # One user is trying to access another user profile:
            if APIkey().user_role_level >= 100:
                user_id = id
            else:
                abort(401, "Insufficient privilege")

        u = dbUsers.find_by_id(user_id)

        if u:
            return u.to_dict(), 200
        else:
            abort(404, "User not found")

    @api.doc('put_user')
    @api.expect(user_params)
    @api.marshal_with(user)
    @api.doc(security='apikey')
    @api.response(404, 'User not found')
    @apikey_required
    def put(self, id: int=None):
        # requester_user_id = APIkey().user_id
        payload = dict(api.payload)
        if id is None:
            # User updating its profile:
            modify_user_id = APIkey().user_id
            # print('User (%i) updating its profile:' % modify_user_id)
        else:
            if id == APIkey().user_id:
                modify_user_id = id
            elif APIkey().user_role_level < 100:  # One user is trying to update another user profile
                abort(401, "Insufficient privilege")
            else:
                modify_user_id = id
                # print("One user (%i) is trying to update another user profile (%i)" % (requester_user_id, modify_user_id))

        u = dbUsers.find_by_id(modify_user_id)

        if u:
            payload.pop('user_id', None)
            # print('payload:', payload)
            u.update(payload)
            return dbUsers.find_by_id(modify_user_id).to_dict(), 200
        else:
            abort(404, "User not found")
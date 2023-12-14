from flask_restx import Namespace, Resource, fields
from flask import abort

from apps.apis.util import APIkey, apikey_required, apikey_admin_required
from apps.authentication.models import Users as dbUsers


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

subscription_plan = api.model("SubscriptionPlan", {
    'label': fields.String(description='Subscription description'),
    # 'level': fields.Integer(description='Subscription level'),
    'quota_tasks': fields.Integer(description="Tasks quota by 'refresh' time frame"),
    'quota_refresh': fields.Integer(description='Quota refresh time frame in seconds'),
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


@api.route('/', defaults={'id': None}, methods=['GET'])
@api.route('/<int:id>', methods=['GET'])
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
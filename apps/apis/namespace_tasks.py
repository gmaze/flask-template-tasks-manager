from flask_restx import Namespace, Resource, fields
from flask import abort
from werkzeug.exceptions import TooManyRequests

from apps import db
from apps.apis.util import TasksManager, APIkey, apikey_required, apikey_admin_required
from apps.authentication.models import Users as dbUsers


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Namespace('tasks', description='Tasks', authorizations=authorizations)

task_user = api.model('User', {
    'user_id': fields.Integer(description='Id of the user who submitted this task'),
    'username': fields.String(description='Login of the user who submitted this task'),
    # Quota ?
})

task_params = api.model("Params", {
    'nfloats': fields.Integer(required=True, description='Number of floats', default=1000),
    'label': fields.String(description='A label for this task', default=""),
})

task_run = api.model("Run", {
    'status': fields.String(description='Task processing status', default='queue'),
    'progress': fields.Float(description='Task progress in percentage'),
    'final_state': fields.String(description='Task final state [success/failed]', default='?'),
    # PID ?
})

task = api.model("Task", {
    'id': fields.Integer(required=True, description='The task identifier'),
    'created': fields.DateTime(description='Task creation timestamp'),
    'updated': fields.DateTime(description='Task last update timestamp'),

    'user': fields.Nested(task_user),
    'params': fields.Nested(task_params),
    'run': fields.Nested(task_run),
})

T = TasksManager(db.session)

@api.route('/all')
class TaskList(Resource):

    @api.doc('list_tasks')
    @api.marshal_list_with(task)
    @api.doc(security='apikey')
    @apikey_required
    @apikey_admin_required
    def get(self):
        """Fetch all tasks at once (requires Admin privilege)"""
        # One user is trying to access all tasks
        return T.tasks

@api.route('/', defaults={'id': None}, methods=['GET', 'POST'])
@api.route('/<int:id>', methods=['GET', 'DELETE'])
@api.param('id', 'The task identifier')
# @api.response(404, 'Task not found')
# @api.response(403, 'Task has not been executed and cannot be cancelled')
class Task(Resource):

    @api.doc('get_task')
    @api.marshal_with(task)
    @api.doc(security='apikey')
    @apikey_required
    def get(self, id):
        """Fetch task data"""
        if id is None:
            # Return tasks created with this API key:
            return T.tasks_by_apikey(APIkey().key), 200
        else:
            # Retrieve this task:
            t = T.get(id)

            # Then check if this task was created with this API key:
            if t['user']['user_id'] == APIkey().user_id:
                return t, 200
            else:
                if APIkey().user_role_level >= 100:  # Check if API key has enough privileges:
                    return t, 200
                else:
                    abort(401, "The provided API key must have enough privilege or match the one used to create this task")

    @api.doc('create_task')
    @api.expect(task_params)
    @api.marshal_with(task, code=201)
    @api.doc(security='apikey')
    @apikey_required
    def post(self, id):
        """Create a new task"""
        user_id = APIkey().user_id
        api.payload['user_id'] = user_id

        # Check if user quota allows for new tasks to be created:
        this_user = dbUsers.find_by_id(user_id)
        if this_user.tasks_desc_to_dict['quota_left'] > 0:
            created = T.create(api.payload)
            return created
        else:
            raise TooManyRequests("You reached your subscription plan tasks limit", retry_after=this_user.tasks_desc_to_dict['retry-after'])

    @api.doc('cancel_task')
    @api.response(204, 'Task cancelled')
    @api.response(401, 'Insufficient privileges')
    @api.marshal_with(task, code=204)
    @api.doc(security='apikey')
    @apikey_required
    def delete(self, id):
        """Cancel/kill jobs associated with a task"""
        if T.get(id)['user']['user_id'] != APIkey().user_id and APIkey().user_role_level < 100:
            # abort(401, "You can't cancel this task because you don't have enough privileges !")
            abort(401, "The provided API key must have enough privilege or match the one used to create this task")
        else:
            T.cancel(id)

        return self.get(id), 204

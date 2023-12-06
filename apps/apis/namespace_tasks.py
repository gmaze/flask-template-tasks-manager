from flask_restx import Namespace, Resource, fields
from flask import abort, Response

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


@api.route('/')
class TaskList(Resource):

    @api.doc('list_tasks')
    @api.marshal_list_with(task)
    @api.doc(security='apikey')
    @apikey_required
    def get(self):
        """List all tasks"""
        # return T.tasks
        return T.tasks_by_apikey(APIkey().key)

    @api.doc('create_task')
    @api.expect(task_params)
    @api.marshal_with(task, code=201)
    @api.doc(security='apikey')
    @apikey_required
    def post(self):
        """Create a new task"""
        user_id = APIkey().user_id
        api.payload['user_id'] = user_id

        # Check if user quota allows for new tasks to be created:
        this_user = dbUsers.find_by_id(user_id)
        if this_user.tasks_desc_to_dict['quota_left'] > 0:
            created = T.create(api.payload)
            return created
        else:
            # abort(429, "You reached your subscription plan tasks limit.")
            # resp = Response("Foo bar baz")
            # resp.headers['Access-Control-Allow-Origin'] = '*'
            return "You reached your subscription plan tasks limit.", 429, {"Retry-After": this_user.tasks_desc_to_dict['retry-after']}

@api.route('/<int:id>')
@api.param('id', 'The task identifier')
@api.response(404, 'Task not found')
@api.response(403, 'Task has not been executed and cannot be cancelled')
class Task(Resource):

    @api.doc('get_task')
    @api.marshal_with(task)
    @api.doc(security='apikey')
    @apikey_required
    def get(self, id):
        """Fetch a task given its identifier"""
        return T.get(id), 200

    @api.doc('cancel_task')
    @api.response(204, 'Task cancelled')
    @api.marshal_with(task, code=204)
    @api.doc(security='apikey')
    @apikey_required
    def delete(self, id):
        """Cancel/kill jobs associated with a task"""
        if T.get(id)['user']['user_id'] != APIkey().user_id:
            # abort(401, "You can't cancel this task because you don't have enough privileges !")
            abort(401, "The provided API key must match the one used to create this task in order to cancel it")
        else:
            T.cancel(id)

        return self.get(id), 204

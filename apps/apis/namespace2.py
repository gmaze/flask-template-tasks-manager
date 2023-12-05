from flask_restx import Namespace, Resource, fields
from flask import abort

from apps import db
from apps.apis.util import TasksManager, apikey_required, APIkey


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Namespace('tasks', description='Tasks', authorizations=authorizations, security='apikey')

task_user = api.model('User', {
    'user_id': fields.Integer(description='Id of the user who submitted this task'),
    'username': fields.String(description='Login of the user who submitted this task'),
    # Quota ?
})

task_params = api.model("Params", {
    # 'username': fields.String(required=True, description='Login  of the user who submitted this task', default=""),
    'nfloats': fields.Integer(required=True, description='Number of floats', default=1000),
    'label': fields.String(description='A label for this task', default=""),
})

task_run = api.model("Run", {
    'status': fields.String(description='Task processing status', default='queue'),
    'progress': fields.Float(description='Task progress in percentage'),
    'final_state': fields.String(description='Task final state [success/failed]', default='?'),
    # PID ?
})

task = api.model("Task",{
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
    def get(self):
        """List all tasks"""
        return T.tasks

    @api.doc('create_task')
    @api.expect(task_params)
    @api.marshal_with(task, code=201)
    @api.doc(security='apikey')
    @apikey_required
    def post(self):
        """Create a new task"""
        api.payload['user_id'] = APIkey().user_id
        created = T.create(api.payload)
        print("Created:\n", created)
        return created


@api.route('/<int:id>')
@api.param('id', 'The task identifier')
@api.response(404, 'Task not found')
@api.response(403, 'Task has not been executed and cannot be cancelled')
class Task(Resource):

    @api.doc('get_task')
    @api.marshal_with(task)
    def get(self, id):
        """Fetch a task given its identifier"""
        return T.get(id), 200

    @api.doc('cancel_task')
    @api.response(204, 'Task cancelled')
    @api.marshal_with(task, code=204)
    @apikey_required
    def delete(self, id):
        """Delete a task is for cancelling/killing jobs associated with a task"""
        if T.get(id)['user']['user_id'] != APIkey().user_id:
            # abort(401, "You can't cancel this task because you don't have enough privileges !")
            abort(401, "The provided API key must match the one used to create this task in order to cancel it")
        else:
            T.cancel(id)

        return self.get(id), 204

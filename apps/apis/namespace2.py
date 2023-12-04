from flask import abort
from flask_restx import Namespace, Resource, fields, Model
from flask_login import current_user
from apps import db
from apps.apis.util import TasksManager

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Namespace('tasks', description='Tasks', authorizations=authorizations, security='apikey')

task = api.model('Task', {
    'id': fields.Integer(required=True, description='The task identifier'),

    'username': fields.String(required=False, description='Login  of the user who submitted this task', default=""),
    'user_id': fields.Integer(required=True, description='Id of the user who submitted this task'),

    'created': fields.DateTime(description='Task creation timestamp'),
    'updated': fields.DateTime(description='Task last update timestamp'),

    'label': fields.String(required=False, description='A label for this task', default=""),
    'nfloats': fields.Integer(required=True, description='Number of floats', default=1000),

    'status': fields.String(required=True, description='Task processing status', default='queue'),
    'progress': fields.Float(description='Task progress in percentage'),
    'final_state': fields.String(description='Task final state [success/failed]', default='?'),
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
    @api.expect(task)
    @api.marshal_with(task, code=201)
    def post(self):
        """Create a new task"""
        print("API Call payload:", api.payload)
        print(current_user)
        if current_user.is_authenticated:
            print(current_user.get_id())
            print("Submitted new task from API with", api.payload)
            return T.create(api.payload)
        else:
            api.payload['user_id'] = 1
            print("Fix for non-authenticated, Submitted new task from API with", api.payload)
            return T.create(api.payload)
            # abort(403, "You must be authenticated to create new tasks")


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

    @api.doc('delete_task')
    @api.response(204, 'Task cancelled')
    @api.marshal_with(task, code=204)
    def delete(self, id):
        """Delete a task is for cancelling/killing jobs associated with a task"""
        T.cancel(id)
        return self.get(id), 204

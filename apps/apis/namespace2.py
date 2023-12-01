from flask_restx import Namespace, Resource, fields

from apps import db
from apps.apis.util import TasksManager


api = Namespace('tasks', description='Tasks')

task = api.model('Task', {
    'id': fields.Integer(required=True, description='The task identifier'),
    'username': fields.String(required=False, description='User login name', default=""),
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
        return T.create(api.payload), 201


@api.route('/<int:id>')
@api.param('id', 'The task identifier')
@api.response(404, 'Task not found')
@api.response(403, 'Task has not been executed and cannot be cancelled')
class Task(Resource):
    @api.doc('get_task')
    @api.marshal_with(task)
    def get(self, id):
        """Fetch a task given its identifier"""
        return T.get(id)

    @api.doc('delete_task')
    @api.response(204, 'Task cancelled')
    @api.marshal_with(task, code=204)
    def delete(self, id):
        """Delete is for cancelling a task given its identifier"""
        T.cancel(id)
        return self.get(id), 204

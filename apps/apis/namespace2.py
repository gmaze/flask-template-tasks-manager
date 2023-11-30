from flask_restx import Namespace, Resource, fields

from apps import db
from apps.apis.util import TaskDAO, TasksManager


api = Namespace('tasks', description='Tasks')

task = api.model('Task', {
    'id': fields.Integer(required=True, description='The task identifier'),
    'username': fields.String(required=False, description='User login name', default=""),
    'label': fields.String(required=False, description='A label for this task', default=""),
    'nfloats': fields.Integer(required=True, description='Number of floats', default=1000),
    'status': fields.String(required=True, description='Task processing status', default='queue'),
    'created': fields.DateTime(description='Task creation timestamp'),
    'updated': fields.DateTime(description='Task last update timestamp'),
    'progress': fields.Float(description='Task progress in percentage'),
})

TASKS = TaskDAO(api)
TASKS.create({'label': 'Build an API', 'status': 'done'})
TASKS.create({'label': '?????', 'status': 'cancelled'})
TASKS.create({'label': 'profit!', 'status': 'running'})

# print("apis.namespace2")
# print(db.session)
# print(type(db.session))
T = TasksManager(db.session)


@api.route('/')
class TaskList(Resource):
    @api.doc('list_tasks')
    @api.marshal_list_with(task)
    def get(self):
        """List all tasks"""
        return T.update_job_status().tasks

    @api.doc('create_task')
    @api.expect(task)
    @api.marshal_with(task, code=201)
    def post(self):
        """Create a new task"""
        return T.create(api.payload), 201


@api.route('/<id>')
@api.param('id', 'The task identifier')
@api.response(404, 'Task not found')
class Task(Resource):
    @api.doc('get_task')
    @api.marshal_with(task)
    def get(self, id):
        """Fetch a task given its identifier"""
        return T.update_job_status(id).get(id)

    @api.doc('delete_task')
    @api.response(204, 'Task deleted')
    def delete(self, id):
        """Delete a task given its identifier"""
        TASKS.delete(id)
        return '', 204

    # @api.expect(task)
    # @api.marshal_with(task)
    # def put(self, id):
    #     """Update a task given its identifier"""
    #     return TASKS.update(id, api.payload)



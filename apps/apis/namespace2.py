from flask_restx import Namespace, Resource, fields
from apps.apis.models import Tasks


api = Namespace('tasks', description='Tasks')

task = api.model('Task', {
    'id': fields.Integer(required=True, description='The task identifier'),
    'label': fields.String(required=False, description='A label for this task', default=""),
    'nfloats': fields.Integer(required=True, description='Number of floats', default=1000),
    'status': fields.String(required=True, description='Task processing status', default='queue'),
})

class TaskDAO:
    status_code = {'queue': 0, 'running': 1, 'done': 2, 'cancelled': 3}

    def __init__(self, api):
        self.api = api
        self.counter = 0
        self.tasks = []

    def get(self, id):
        for t in self.tasks:
            # print(type(t['id']), t['id'])
            # print(type(id), id)
            if t['id'] == int(id):
                return t
        self.api.abort(404, "Task {} doesn't exist".format(id))

    def create(self, data):
        a_task = data
        a_task['id'] = self.counter = self.counter + 1
        if 'label' in data:
            a_task['label'] = data['label']

        if 'nfloats' in data:
            a_task['nfloats'] = data['nfloats']

        if 'status' in data:
            a_task['status'] = data['status']

        self.tasks.append(a_task)
        return a_task

    def update(self, id, data):
        a_task = self.get(id)
        a_task.update(data)
        return a_task

    def delete(self, id):
        a_task = self.get(id)
        self.tasks.remove(a_task)


TASKS = TaskDAO(api)
TASKS.create({'label': 'Build an API', 'status': 'done'})
TASKS.create({'label': '?????', 'status': 'cancelled'})
TASKS.create({'label': 'profit!', 'status': 'running'})



@api.route('/')
class TaskList(Resource):
    @api.doc('list_tasks')
    @api.marshal_list_with(task)
    def get(self):
        """List all tasks"""
        return TASKS.tasks

    @api.doc('create_task')
    @api.expect(task)
    @api.marshal_with(task, code=201)
    def post(self):
        """Create a new task"""
        return TASKS.create(api.payload), 201


@api.route('/<id>')
@api.param('id', 'The task identifier')
@api.response(404, 'Task not found')
class Task(Resource):
    @api.doc('get_task')
    @api.marshal_with(task)
    def get(self, id):
        """Fetch a task given its identifier"""
        return TASKS.get(id)
        # for task in TASKS:
        #     if task['id'] == id:
        #         return task
        # api.abort(404)

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

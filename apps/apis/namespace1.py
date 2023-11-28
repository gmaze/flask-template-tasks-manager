from flask_restx import Namespace, Resource, fields

api = Namespace('simulations', description='Simulations')

simulation = api.model('Simulation', {
    'id': fields.Integer(required=True, description='The simulation identifier'),
    'task': fields.String(required=True, description='The simulation details')
})


class SimulationsDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Simulation {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        self.todos.append(todo)
        return todo

    def update(self, id, data):
        todo = self.get(id)
        todo.update(data)
        return todo

    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)


SIMS = SimulationsDAO()
SIMS.create({'task': 'Build an API'})
SIMS.create({'task': '?????'})
SIMS.create({'task': 'profit!'})
# api.logger.info("Dummy simulations list created")


@api.route('/')
class SimulationList(Resource):
    @api.doc('list_simulations')
    @api.marshal_list_with(simulation)
    def get(self):
        """List all simulations"""
        return SIMS.todos

    @api.doc('create_simulation')
    @api.expect(simulation)
    @api.marshal_with(simulation, code=201)
    def post(self):
        """Create a new simulation"""
        return SIMS.create(api.payload), 201

@api.route('/<id>')
@api.param('id', 'The simulation identifier')
@api.response(404, 'Simulation not found')
class Simulation(Resource):
    @api.doc('get_simulation')
    @api.marshal_with(simulation)
    def get(self, id):
        """Fetch a simulation given its identifier"""
        return SIMS.get(id)
        # for simulation in SIMS:
        #     if simulation['id'] == id:
        #         return simulation
        # api.abort(404)

    @api.doc('delete_simulation')
    @api.response(204, 'Simulation deleted')
    def delete(self, id):
        """Delete a simulation given its identifier"""
        SIMS.delete(id)
        return '', 204

    # @api.expect(simulation)
    # @api.marshal_with(simulation)
    # def put(self, id):
    #     """Update a task given its identifier"""
    #     return SIMS.update(id, api.payload)

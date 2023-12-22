from flask_restx import Namespace, Resource, fields
from apps.monitors.models import Monitor_CPU as CPU


api = Namespace('monitors', description='System Monitors')


cpu_monitor = api.model("CPU_Monitor", {
    'id': fields.Integer(description='Monitor ID'),
    'label': fields.String(description='Monitor description'),
    'unit': fields.String(description='Monitor value unit'),
    'created': fields.DateTime(description='Monitor creation timestamp'),
    'updated': fields.DateTime(description='Monitor last update timestamp'),

    'timestamp': fields.DateTime(description='Monitor value timestamps'),
    'value': fields.Float(description='Monitor values'),
})


@api.route('/cpu', methods=['GET'])
class default_cpu(Resource):

    @api.doc('get_cpu')
    @api.marshal_with(cpu_monitor)
    def get(self):
        """CPU System Monitor"""

        # Get the list of plans:
        DBresults = CPU.query.order_by(CPU.id.desc()).all()
        return DBresults

        # # Format output:
        # output = []
        # for this_plan in DBresults:
        #     output.append(this_plan.to_dict())
        #
        # return output

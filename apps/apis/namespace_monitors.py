from flask import request
from flask_restx import Namespace, Resource, fields
from apps.monitors.models import Monitor_CPU as CPU
from apps import db

api = Namespace('monitors', description='System Monitors')


monitor_record = api.model("Monitor Record", {
    'timestamp': fields.DateTime(description='Monitor value timestamps'),
    'value': fields.Float(description='Monitor values'),
})

cpu_monitor = api.model("CPU_Monitor", {
    # 'id': fields.Integer(description='Monitor ID'),
    'label': fields.String(description='Monitor description'),
    'unit': fields.String(description='Monitor value unit'),
    'created': fields.DateTime(description='Monitor creation timestamp'),
    'updated': fields.DateTime(description='Monitor last update timestamp'),
    'data': fields.Nested(monitor_record, description='Monitor records')
})


@api.route('/cpu', methods=['GET'])
class default_cpu(Resource):

    @api.doc('get_cpu')
    @api.marshal_with(cpu_monitor)
    def get(self):
        """CPU System Monitor"""

        # Get the list of records:
        DBresults = CPU.query.order_by(CPU.id.desc()).first()

        # Reformat array of records to remove meta-data duplicates:
        output = {'id': DBresults.id,
                  'label': DBresults.label,
                  'unit': DBresults.unit,
                  'created': DBresults.created,
                  'updated': DBresults.updated,
                  'data': [],
                  }

        # Paginate results
        page = int(request.args['page']) if 'page' in request.args else 1
        per_page = int(request.args['per_page']) if 'per_page' in request.args else 60
        max_per_page = int(request.args['max_per_page']) if 'max_per_page' in request.args else 3600

        data = db.paginate(CPU.query.order_by(CPU.timestamp.desc()),
                           page=page, per_page=per_page, max_per_page=max_per_page)
        data = [{'timestamp': row.timestamp, 'value': row.value} for row in data]

        # data = CPU.query.with_entities(CPU.timestamp, CPU.value).order_by(CPU.timestamp.asc()).all()
        output['data'] = data

        return output

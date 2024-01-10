from flask import request, abort
from flask_restx import Namespace, Resource, fields
from apps.monitors.models import Monitor_CPU as CPU
from apps.monitors.models import Monitor_VMEM as VMEM
from apps.monitors.models import Monitor_DISK as DISK
from apps import db

api = Namespace('monitors', description='System Monitors')


record = api.model("Monitor Record", {
    'timestamp': fields.DateTime(description='Monitor value timestamps'),
    'value': fields.Float(description='Monitor values'),
})

cpu_monitor = api.model("CPU_Monitor", {
    'label': fields.String(description='Monitor description'),
    'unit': fields.String(description='Monitor value unit'),
    'created': fields.DateTime(description='Monitor creation timestamp'),
    'updated': fields.DateTime(description='Monitor last update timestamp'),
    'data': fields.Nested(record, description='Monitor records')
})

vmem_record = api.model("Virtual Memory Monitor Record", {
    'timestamp': fields.DateTime(description='Record timestamps'),
    'value': fields.Float(description='Virtual Memory percentage usage'),
    'total': fields.Float(description='Total physical memory (exclusive swap)'),
    'available': fields.Float(description='Memory that can be given instantly to processes without the system going into swap'),
})

vmem_monitor = api.model("VMEM_Monitor", {
    'label': fields.String(description='Monitor description'),
    'unit': fields.String(description='Monitor value unit'),
    'created': fields.DateTime(description='Monitor creation timestamp'),
    'updated': fields.DateTime(description='Monitor last update timestamp'),
    'data': fields.Nested(vmem_record, description='Monitor records')
})


du_record = api.model("Disk Usage Monitor Record", {
    'timestamp': fields.DateTime(description='Record timestamps'),
    'value': fields.Float(description='Percentage of disk usage'),
    'total': fields.Float(description='Total Possible Disk Usage'),
    'available': fields.Float(description='Available Free Space'),
})

du_monitor = api.model("DISK_Monitor", {
    'label': fields.String(description='Monitor description'),
    'unit': fields.String(description='Monitor value unit'),
    'created': fields.DateTime(description='Monitor creation timestamp'),
    'updated': fields.DateTime(description='Monitor last update timestamp'),
    'data': fields.Nested(du_record, description='Monitor records')
})


@api.route('/cpu', methods=['GET'])
class default_cpu(Resource):

    @api.doc('get_cpu')
    @api.marshal_with(cpu_monitor)
    def get(self):
        """CPU System Monitor"""

        # Get the list of records:
        DBresults = CPU.query.order_by(CPU.id.desc()).first()

        if not getattr(DBresults, 'created', False):
            abort(404)

        # Reformat array of records to remove meta-data duplicates:
        output = {'label': CPU.label,
                  'unit': CPU.unit,
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


@api.route('/vmem', methods=['GET'])
class default_vmem(Resource):

    @api.doc('get_vmem')
    @api.marshal_with(vmem_monitor)
    def get(self):
        """Virtual Memory System Monitor"""

        # Get the list of records:
        DBresults = VMEM.query.order_by(VMEM.id.desc()).first()

        if not getattr(DBresults, 'created', False):
            abort(404)

        # Reformat array of records to remove meta-data duplicates:
        output = {'label': VMEM.label,
                  'unit': VMEM.unit,
                  'created': DBresults.created,
                  'updated': DBresults.updated,
                  'data': [],
                  }

        # Paginate results
        page = int(request.args['page']) if 'page' in request.args else 1
        per_page = int(request.args['per_page']) if 'per_page' in request.args else 60
        max_per_page = int(request.args['max_per_page']) if 'max_per_page' in request.args else 3600

        data = db.paginate(VMEM.query.order_by(VMEM.timestamp.desc()),
                           page=page, per_page=per_page, max_per_page=max_per_page)
        data = [{'timestamp': row.timestamp,
                 'value': row.value,
                 'total': row.total,
                 'available': row.available,
                 } for row in data]
        output['data'] = data

        return output


@api.route('/du', methods=['GET'])
class default_du(Resource):

    @api.doc('get_du')
    @api.marshal_with(du_monitor)
    def get(self):
        """Disk Usage System Monitor"""

        # Get the list of records:
        DBresults = DISK.query.order_by(DISK.id.desc()).first()

        if not getattr(DBresults, 'created', False):
            abort(404)

        # Reformat array of records to remove meta-data duplicates:
        output = {'label': DISK.label,
                  'unit': DISK.unit,
                  'created': DBresults.created,
                  'updated': DBresults.updated,
                  'data': [],
                  }

        # Paginate results
        page = int(request.args['page']) if 'page' in request.args else 1
        per_page = int(request.args['per_page']) if 'per_page' in request.args else 60
        max_per_page = int(request.args['max_per_page']) if 'max_per_page' in request.args else 3600

        data = db.paginate(DISK.query.order_by(DISK.timestamp.desc()),
                           page=page, per_page=per_page, max_per_page=max_per_page)
        data = [{'timestamp': row.timestamp,
                 'value': row.value,
                 'total': row.total,
                 'available': row.available,
                 } for row in data]
        output['data'] = data

        return output

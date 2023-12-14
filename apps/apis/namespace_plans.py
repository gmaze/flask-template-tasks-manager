from flask_restx import Namespace, Resource, fields
from flask import abort
from apps.subscriptions.models import SubscriptionPlans as dbPlans

api = Namespace('plans', description='Subscription Plans')

subscription_plan = api.model("SubscriptionPlan", {
    'label': fields.String(description='Subscription description'),
    'level': fields.Integer(description='Subscription level'),
    'quota_tasks': fields.Integer(description="Tasks quota by 'refresh' time frame"),
    'quota_refresh': fields.Integer(description='Quota refresh time frame in seconds'),
})

@api.route('/', methods=['GET'])
class Plans(Resource):

    @api.doc('get_plans')
    @api.marshal_with(subscription_plan)
    def get(self):
        """List of available subscription plans"""

        # Get the list of plans:
        DBresults = dbPlans.query.order_by(dbPlans.id.desc()).all()

        # Format output:
        output = []
        for this_plan in DBresults:
            output.append(this_plan.to_dict())

        return output

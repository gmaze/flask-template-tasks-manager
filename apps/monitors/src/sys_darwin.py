import psutil
from datetime import datetime, timezone
from apps.monitors.models import Monitor_CPU, Monitor_VMEM


def get_cpu_level():
    try:
        return psutil.cpu_percent()
    except:
        return None


def get_vmem_level():
    try:
        return psutil.virtual_memory()
    except:
        return None


def read_save_data(save=True, app=None, db=None):
    date_jour = datetime.now(timezone.utc)

    # Metrics:
    cpu = get_cpu_level()
    vmem = get_vmem_level()

    #
    if save:
        with app.app_context():
            record = Monitor_CPU(**{'timestamp': date_jour, 'value': cpu})
            db.session.add(record)
            db.session.commit()

            record = Monitor_VMEM(**{'timestamp': date_jour,
                                     'value': vmem.percent,
                                     'total': vmem.total/1e6,
                                     'available': vmem.available/1e6,
                                     })
            db.session.add(record)
            db.session.commit()

    return (date_jour, cpu, vmem)

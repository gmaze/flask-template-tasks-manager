import psutil
from pathlib import Path
from datetime import datetime, timezone
from apps.monitors.models import Monitor_CPU, Monitor_VMEM
from apps.monitors.models import Monitor_DISK


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


def get_disk_usage_old(p):
    try:
        return psutil.disk_usage(p)
    except:
        return None


def get_disk_usage(p):
    class DiskUsage:
        percent = 0
        total = psutil.disk_usage('/').free  # Available to user
        # total = 1e9  # 1 Gb allowance
        free = 0

    try:
        root_directory = Path(p)
        size = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())

        du = DiskUsage()
        du.free = du.total - size
        du.percent = size*100/du.total
        return du
    except:
        return None


def read_save_data(save=True, app=None, db=None):
    date_jour = datetime.now(timezone.utc)

    # Metrics:
    cpu = get_cpu_level()
    vmem = get_vmem_level()
    du = get_disk_usage(app.config['STORAGE_PATH'])
    # du = get_disk_usage("/")

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

            record = Monitor_DISK(**{'timestamp': date_jour,
                                     'value': du.percent,
                                     'total': du.total/1e6,
                                     'available': du.free/1e6,
                                     })
            db.session.add(record)
            db.session.commit()

    return (date_jour, cpu, vmem)

import psutil
from datetime import datetime, timezone
# import website.db as DB
from apps.monitors.models import Monitor_CPU

def get_battery_level():
    try:
        return psutil.sensors_battery().percent
    except:
        return None


def get_cpu_level():
    try:
        return psutil.cpu_percent()
    except:
        return None


def read_save_data(save=True, app=None, db=None):
    date_jour = datetime.now(timezone.utc)

    # Capteurs:
    Tension = 0
    Courant = 0
    Pourcentage_BAT = get_battery_level()
    Luminosite = 0

    # Metrics serveur:
    cpu = get_cpu_level()
    mem = 0

    #
    if save:
        with app.app_context():
            record = Monitor_CPU(**{'timestamp':date_jour, 'value':cpu})
            db.session.add(record)
            db.session.commit()

    return (date_jour, Tension, Courant, Pourcentage_BAT, Luminosite, cpu, mem)

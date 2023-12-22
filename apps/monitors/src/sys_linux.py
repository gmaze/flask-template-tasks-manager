from datetime import datetime, timezone
import psutil
# import website.db as DB


def get_battery_level():
    """

    Si la variable d'environnement PYTHONANYWHERE_DOMAIN existe, alors y a pas de batterie !
    """
    try:
        return psutil.sensors_battery().percent
    except:
        return None


def get_cpu_level():
    try:
        return psutil.cpu_percent()
    except:
        return None


def read_save_data(save=True):
    date_jour = datetime.now(timezone.utc)
    Tension = 0
    Courant = 0
    Pourcentage_BAT = get_battery_level()
    Luminosite = 0
    # if save:
    #     DB.insert_sensor(date_jour, Tension, Courant, Pourcentage_BAT, Luminosite)
    return (date_jour, Tension, Courant, Pourcentage_BAT, Luminosite)

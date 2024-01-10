#
# Dans ce sous-module on place les routines qui permettent de lire les valeurs en temps reel
# des capteurs et les metriques du systeme cote server:
# - charge de la batterie
# - intensite lumineuse
# - cpu du serveur
#
# Les fonctions de mise en base sont toujours dans le sous-module "db", ici on n'utilise que les facades
#
# Il y a un sous-module pour chaque systeme d'exploitation ou specifique a une platforme:
# - Darwin (Mac OS)
# - Linux (eg: deploiement chez pythonanywhere)
# - raspberry
# Chacuns des sous-modules doit exposer qqs fonctions avec le meme nom:
# - read_save_data
#

import os
import time
from datetime import datetime, timezone
from threading import Thread
from pathlib import Path
from platform import system


__all__ = {
    'SysTemMonitor',
}


if system() == "Darwin":
    from .sys_darwin import read_save_data

elif system() == "Linux":
    from .sys_linux import read_save_data

else:
    raise ValueError("Unsupported OS ! ['%s']" % system())

# Absolute path to repository:
REPOSITORY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print('REPOSITORY_ROOT', REPOSITORY_ROOT)


class SysTemMonitor:
    lockfile = os.path.sep.join([REPOSITORY_ROOT, "logs", "monitor_lock.log"])

    def __init__(self, app, db, refresh_rate: int = 2):
        """Monitoring du serveur

        Parameters
        ----------
        app:
            Une instance d'application (necessaire pour executer la mise en base des mesures capturees)
        refresh_rate: int, default: 2
            Taux de rafraichissement du captage des mesures, en seconde.

        Examples
        --------
        M = Monitor(app).start()

        """
        self.refresh_rate = refresh_rate  # seconds
        self.db = db
        self.app = app

    def print(self, txt):
        Path(self.lockfile).touch()
        with open(self.lockfile, "a") as f:
            f.write("%s: %s\n" % (datetime.now(timezone.utc), txt))

    @property
    def running(self):
        # Check if a monitor is already running:
        r = os.path.exists(self.lockfile)# and self.thread.is_alive()
        return r

    def runner(self, this_app, this_db):
        self.print("Entering runner")
        while self.running:
            time.sleep(self.refresh_rate)
            Path(self.lockfile).touch()

            read_save_data(save=True, app=this_app, db=this_db)

            self.print("Monitor.checked")
        else:
            self.print("Exit runner")

    def start(self):
        """Start the monitor"""
        if not self.running:
            self.print("Monitor.start")
            Path(self.lockfile).touch()
            self.thread = Thread(target=self.runner, daemon=True, args=(self.app, self.db,),)
            self.thread.start()
        else:
            self.print("Monitor already running !")

        return self

    def stop(self):
        if os.path.exists(self.lockfile):
            self.print("Monitor.stopped")
            os.remove(self.lockfile)
        else:
            self.print("The lockfile does not exist at: %s" % self.lockfile)

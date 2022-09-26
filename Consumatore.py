import threading
import time

from rubrica import *



# Consumatore Thread Class
class Consumatore(threading.Thread):
    def __init__(self, rub, i):
        super().__init__(name="Consumatore"+str(i))
        self.c = rub

    def run(self):
        print(self.c)

        self.c.modifica("gigi", "rossi", 11111111)

        time.sleep(2)

        self.c.cancella("Alberto", "Alberti")

        time.sleep(2)

        self.c.inserisci("Rossano", "Rosso", 3478999)
        self.c.modifica("mario romualdo", "rossi", 2222222)
        self.c.inserisci("Alberto", "Alberti", 3475599)

        time.sleep(2)

        self.c.inserisci("Carlo", "Carli", 3475591)
        self.c.inserisci("Ubaldo", "Ubaldi", 3475511)

        time.sleep(3)

        self.c.cancella("Alberto", "Alberti")
        self.c.cancella("Ubaldo", "Ubaldi")
        time.sleep(1)

        items_produced = 0
        while items_produced < 10:
            self.c.suggerimento()
            items_produced +=1
        
        print(self.c.ordina(crescente=False))
        
        #print(self.c)

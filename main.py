#L'idea di base della gui logger è quella di poter loggare direttammente il risultato di un thread
# all'interno di un qualsiasi widget di tkinter.
#Per realizzare ciò ci siamo avvalsi di un thread che avvia dei tasker che salvano i log e che periodicamente
# vengono reindirizzati al widget di tkinter attraverso il texthandler.

from tkinter import * 
from tkinter import simpledialog 
from tkinter import messagebox
import tkinter as tk
import queue
import logging
import time
import threading
from Consumatore import *
from Produttore import *
from rubrica import *

#   creo una classe che gestisce l'output del testo nel widget
class gestore_testo(logging.Handler):
    def __init__(self, text):
        # faccio partire l' Handler __init__
        logging.Handler.__init__(self)
        # uso un'appoggio in cui poi andrò a salvare il testo del log
        self.text = text

    def emit(self, record): #la fn si occupa di fare l'inserimento dei messaggi di log all'interno della var d'appoggio 
        msg = self.format(record)
        self.text.configure(state='normal')
        self.text.insert(tk.END, msg + '\n')
        self.text.configure(state=tk.DISABLED)
        self.text.yview(tk.END)

class GUILogger(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('GUI Logger')
        self.resizable(width=False, height=False)
        #inizializzo i tasti e la text che andrà a contenere il log
        self.titolo=tk.Label(self, 
          text = "Secondo Assegnamento \n Arena - Biondi \n Programmazione e Analisi Dati 21/22",
          font = ("Roboto", 15), 
          background = 'white', 
          foreground = "black")
        self.titolo.pack(expand=True, fill='x')
        self.avvia_single = tk.Button(self, text='Avvia i test in modalità Single Thread', command=self.avvio_single, font = ("Roboto", 12), 
          background = 'white', 
          foreground = "black")
        self.avvia_single.pack(expand=True, fill='x')
        self.avvia_multi = tk.Button(self, text='Avvia i test in modalità Multithread', command=self.avvio_multi, font = ("Roboto", 12), 
          background = 'white', 
          foreground = "black")
        self.avvia_multi.pack(expand=True, fill='x')
        self.tasto_esci = tk.Button(self, text='Esci', command=self.close_app, font = ("Roboto", 12), 
          background = 'white', 
          foreground = "black")
        self.tasto_esci.pack(expand=True, fill='x')
        self.text_console = tk.Text(self, bg='black', fg='white', font = (" Consolas", 11))
        self.text_console.pack(expand=True, fill='both')

        #   inizializzo la  queue, la task list, e il logger handler cioè dove passo il testo al widget
        self.logger = logging.getLogger()
        self.logger.addHandler(gestore_testo(self.text_console))
        self.log_queue = queue.Queue()
        self.task_list = []
        self.protocol('WM_DELETE_WINDOW', self.close_app)      # uso il meccanismo protocol di tkinter per chiudere l'app da tasto

    def test_single_thread(self, task_thread):        #test single thread
        try:
            self.task_list.append(task_thread) #aggiungo questo task alla lista di task che devo svolgere
            threading.Event().wait(1)
            threads = []
            produttore = Produttore(Rub, 1)
            consumatore = Consumatore (Rub, 1)
            threads.append(produttore)
            threads.append(consumatore)
            produttore.start()
            consumatore.start()
            produttore.join()
            consumatore.join()
        except:
                logger.error('******************ERRORE CRITICO: Impossibile avviare il thread******************')
        messagebox.showinfo("Conferma","Test Single Thread completato! Premi OK per controllare il log.")
        self.task_list.remove(task_thread)    #rimuovo il task dalla lista di quelli da fare

    def test_multithread(self, task_thread): #come per il singlethread ma in multithreading
            #creo una nuova finestra apposita per l'input dell'int
            popup = Tk()
            popup.resizable(width=False, height=False)
            popup.geometry("350x350")
            popup.withdraw()      #la rendo invisibile
            n = simpledialog.askinteger("Insert numero intero","Inserisci un numero intero",parent=popup)
            popup.destroy()#lo elimino dopo l'inserimento dell'int
            self.task_list.append(task_thread)
            if n == 1:
                    self.simple_test()
            else:
                try:
                    threads = []
                    for i in range(n):
                        produttore = Produttore(Rub, i)
                        consumatore = Consumatore (Rub, i)
                        threads.append(produttore)
                        threads.append(consumatore)
                        produttore.start()
                        consumatore.start()
                    for t in threads:
                        t.join()
                except:
                        logger.error('******************ERRORE CRITICO: Impossibile avviare i thread******************')
            messagebox.showinfo("Conferma","Test Multithread completato! Premi OK per controllare il log.")
            self.task_list.remove(task_thread)

    def avvio_single(self): #mi occupo del task da svolgere ovvero avvio un thread che si occupa di realizzare il task, in questo caso la funzione dei test in single thread
        task = threading.Thread(target=lambda: self.test_single_thread(task)) #faccio partire il thread 
        task.start()

    def avvio_multi(self):#come sopra ma in multithread
        task = threading.Thread(target=lambda: self.test_multithread(task))
        task.start()

    def close_app(self):#gestisce la chiusura dell'app e mi accerto che nella task list non vi siano ancora task completare
        if self.task_list:
            time.sleep(5)
        else:
            self.destroy()

if __name__=='__main__':
    Rub = Rubrica()
    guilogger = GUILogger()
    guilogger.mainloop()
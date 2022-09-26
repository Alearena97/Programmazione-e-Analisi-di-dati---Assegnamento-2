# Assegnamento 2  aa 2021-22 622AA modulo programmazione 9 crediti
# Gruppo: Arena - Biondi
# Alessandro Arena 544907 a.arena11@studenti.unipi.it 3407443572
# Rocco Biondi 546237 r.biondi2@studenti.unipi.it 3393368096
from threading import Condition
from threading import Lock
import threading
import Consumatore as consumer
import Produttore as producer
import logging
import queue
import time
import random
import string
import re

#inizializzo il logger
Log_Format = '[%(levelname)s] Il thread %(threadName)-10s %(message)s'
logging.basicConfig(filename = "file_di_log.log", filemode = "w", format = Log_Format, level = logging.ERROR)
logger = logging.getLogger()

#inizializzo la coda con un buffer constant di 3 elementi
DIMENSIONE_BUFFER = 3
q = queue.Queue(DIMENSIONE_BUFFER)


class Rubrica:
    def __init__(self):
        self.rub = {}
        self.lista_doppioni=[]
        self._cv = Condition()


    def __str__(self):
        nome_cognome=list(self.rub.keys()) 
        stringa_completa='' 
        for i in nome_cognome: 
            contatto=i+' '+str(self.rub[i])+'\n' #concateno il nome al numero di telefono
            stringa_completa+=contatto 
        return stringa_completa

    def __eq__(self,r):
        if self.rub == r:   
            return True 
        else:
            return False 

    def __add__(self,r):
         with self._cv: 
            merged = Rubrica()  #creo una nuova istanza della rubrica nella quale inserisco le chiavi delle altre due rubriche 
            for chiave in self.rub.keys(): 
                merged.rub[chiave]=self.rub[chiave] #inserisco nella nuova rubrica le chiavi della rubrica madre
            for valore in r.rub.keys():  
                if valore not in self.rub.keys(): #mi accerto attraverso l'if che il valore presente in r non sia altresì presente in self.rub
                    merged.rub[valore] = r.rub[valore] #se il valore non è presente allora lo pongo in merged, ovvero la risultante della join tra le due
            logging.debug(merged.rub)
            self._cv.notify_all()

    def load(self, nomefile):
        try:#inizalizzo un try che andrà poi a controllare se il file è presente attraverso l'eccezione OSError e se il file di testo è vuoto attraverso un SyntaxError
            with self._cv:
                with open(nomefile,'r') as file_esterno:
                    for riga in file_esterno: 
                        dati = riga.split(" ") 
                        nuovo_nomecognome = ""
                        lista_nomi = dati[:len(dati) - 1] #creo una lista contenente tutti i nomi, tranne i dati, ponendo come indice la lunghezza della lista -1
                        check_ultimo = 0 #pongo una variabile che mi funge da stop all'aggiunta dello spazio alla fine della stringa e la utilizzo come condizione di termine nell'istruzione condizionale che segue
                        for name in lista_nomi:  
                            if check_ultimo < len(lista_nomi)-1: #mi accerto che non sia l'ultimo record inserito
                                nuovo_nomecognome = nuovo_nomecognome + str(name) + " " #concateno in una stringa il record aggiornato e pongo uno spazio alla fine della stringa al fine di dividere ogni nome e cognome
                                check_ultimo = check_ultimo + 1 
                            else:
                                nuovo_nomecognome = nuovo_nomecognome + str(name)
                        self.rub[nuovo_nomecognome]= int(dati[len(dati) - 1])#aggiorno il dict del metodo costruttore ponendo come chiave la nuova coppia nome-cognome e come valore il relativo nr di telefono
                    self._cv.notify_all()
                    return self.rub
        except OSError: 
            print("Il file chiamato", nomefile ,"non è stato trovato")
        except SyntaxError:
            print("Il file di testo è vuoto")       

    def inserisci(self, nome, cognome, dati):
        with self._cv: 
            nomecognome = nome + " " + cognome   
            if nomecognome not in self.rub.keys() and dati not in self.rub.values():   #controllo che nome e cognome non siano presenti in self.rub e che il numero di telefono non sia presente tra i valori associati alle chiavi 
                self.rub[nomecognome]=dati
                logger.error(threading.current_thread().getName()+' inserisce ' + str(nome)  + ' ' +str(cognome)+ ' '+str(dati))
                self._cv.notify_all()
                return True
            else:
                return False
        
    def modifica(self, nome, cognome, newdati):
        with self._cv:
            nomecognome =str(nome) + " " + str(cognome)  
            if newdati not in self.rub.values() and nomecognome in self.rub.keys():   #contro che i nuovi dati non siano tra i numeri di telefono in self.rub e che nome e cognome siano tra le chiavi 
                self.rub[nomecognome]=newdati
                self._cv.notify_all()  
                return True
            else:
                return False

    def cancella(self, nome, cognome):
        with self._cv:      
            nomecognome = str(nome)+' '+str(cognome)   
            if nomecognome in self.rub.keys(): 
                del self.rub[nomecognome]  #cancello da self.rub il nome e il cognome se presenti 
                logger.error(threading.current_thread().getName()+' rimuove ' + str(nome)  + '  ' +str(cognome) +' '+ 'dalla rubrica')
                self._cv.notify_all()
                return True
            else:
                return False

    def cerca(self, nome, cognome):
        with self._cv:
            contatore=0
            logger.error(threading.current_thread().getName()+' ricerca ' + str(nome)  + ' ' +str(cognome) +' '+ 'nella rubrica')
            for key in list(self.rub.keys()): 
                    if re.search(r'_[0-9]+', key): #attraverso una regex mi accerto che nel nome vi siano o meno underscore seguiti da numero
                        self.lista_doppioni.append(self.rub[key]) #se si appendo il suddetto in un'apposita lista
                        contatore+=1 
                    elif nome + " " + cognome == key: #qui controllo se il nome cognome standard (senza underscore e senza numero) sia presente 
                        self.lista_doppioni.append(key)
                        contatore+=1
            self._cv.notify_all()
            if contatore != 0:#se il contatore è diverso da 0 allora vuol dire che sono stati trovati doppioni quindi ritorno la lista di questi
                return self.lista_doppioni
            else:
                return None
                
    def store(self, nomefile):
        try:
            with self._cv:   
                with open(nomefile,'w') as file_esterno:  
                    for i in list(self.rub.keys()):    
                        i = i + " " + str(self.rub[i]) + "\n"  #per ogni elemento della lista delle chiavi concateno all'elemento uno spaio vuoto, il numero di telefono trasformato in stringa e un escape character che fa andare a capo
                        file_esterno.write(i)
                        self._cv.notify_all()    
        except EnvironmentError : #l'eccezione enviroment è la classe superiore di errori come  IOError, OSError e WindowsError semmai presenti
            return("Errore: Il file non esiste") 

    def ordina(self,crescente=True):
        if crescente==True:   
            sorted_keys = sorted(self.rub.keys(), key = lambda x: x.lower()) #ordino le chiavi del dict attraverso una funzione lambda. Abbiamo preferito utilizzare questa piuttoasto che sort in quanto più efficiente in termini computazionali di tempo trascorso e di risorse utilizzate
            sorted_dict = {} 
            for key in sorted_keys: 
                sorted_dict.update({key: self.rub[key]})#aggiorno il dizionario aggiornato ponendo come chiave il nome cognome preso dalla lista ordinata
            formatta = '%s : %s' #il token %s può essere sostiuito da qualsiasi stringa 
            return "\n".join([formatta % (key, str(value)) for key, value in sorted_dict.items()]) #per ottenere la corretta formattazione nome cognome dati itero sul dizionario applicando la corretta formattazione in modo tale che vada a capo per ogni entry del dizionario. Ripeto lo stesso nel ramo else
        else:
            sorted_keys = sorted(self.rub, key = lambda x: x.lower(),reverse=True) 
            sorted_dict = {}
            for key in sorted_keys:
                sorted_dict.update({key: self.rub[key]})
            formatta = '%s : %s'
            return "\n".join([formatta % (key, str(value)) for key, value in sorted_dict.items()]) 

    def smarmella(self, conferma=True):
     #cancella con un solo comando il contenuto della rubrica -- realizzata ex novo e testata in moreTest.py
        if conferma==True:
            with self._cv:
                self.rub.clear() 
            self._cv.notify_all()
            return True
        else:
            return None
        
    def suggerisci(self, nome, cognome):
        with self._cv: #con l'utilizzo di questo metodo utilizzo la condition senza tuttavia gestire manualmente acquire/release, di fatti gestisce autonomamente l'accesso alla risorsa
            try:
                while q.full(): #aspetto che la coda non sia piena
                    self._cv.wait(1)
                q.put(nome+' '+cognome) #inserisco il nome e cognome in coda
                contatto_telefonico = ''.join(random.choice(string.digits) for i in range(8)) #genero il nr di telefono
                self.inserisci(nome,cognome,str(contatto_telefonico))
                logger.error(threading.current_thread().getName()+' suggerisce ' + str(nome)  + '  ' +str(cognome) +' '+ 'e inoltre vi sono '+ str(q.qsize()) +' elementi in coda')
                self._cv.notify_all()
            except:
                logger.error(threading.current_thread().getName()+' non è stato in grado di eseguire la fn suggerisci')
        time.sleep(1)
        
    def suggerimento(self):
        with self._cv: 
            while q.empty(): #finchè la coda è vuota aspetto e poi prendo l'elemento
                self._cv.wait()
            q.get()
            logger.error(threading.current_thread().getName()+'viene attivato '+ 'e inoltre vi sono '+ str(q.qsize()) +' elementi in coda')
            self._cv.notify_all()
        time.sleep(1)
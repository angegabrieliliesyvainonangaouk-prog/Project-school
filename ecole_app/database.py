
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
import os 
#1)Appelation de la variable environnementale ou encore l'url qui nous permet d'appeler une base de donnée
bddc= os.getenv("bdd")#db c'est juste une extension, c'est une variable,normalement cette lign crée  un fichier school.db si il n'existait pas 

#Création du chemin 
engine=create_engine(bddc)
#connect_args={"check_same_thread":False})
    

#initialisation de la fonction session sessionmaker
sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)#aucun enregistrement automatique que ce soit à cout termes ou directement dans la base de donnée

#création de la Base 
Base= declarative_base()
#fonction de dépendance pour l'api 

def get():#cette fonction me permet d'utiliser la bdd selon l'api 
    try :
        db=sessionlocal()#je lève une session où je pourraiq utiliser mes api 
        yield db#Je ne ferme pas la bdd tant que tout mes api ne sont pas terminés
        #ici le code est mis en pause  elle devient un génerateur et le code suivant sera exécuté contrairement à return 
    finally:#oui ils le sont complémentaires 
        db.close()
    



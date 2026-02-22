
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
    
#un api cloud est différent d'un gateway  par de client comme pour un cloud api 

#Mvp 
#v1-1
#Page 1 du site nom de l'école et mot de passe 
#page de remplissage des infos  de l'école nécéssaire  à l'utilisationn de l'ia 
#page 2 choix des classes de l'école 
#page 3 liste des élèves avec les infos  de tous les élèves 
#on y accèdera à la page  4 grâce à un bouton sur le coté qui dira fairel'appel 
#page 4  accès à la liste des élèves de la classe pouyr faire l'appel des présences 

#page 5 response du back end sur le front end après avoir validé l'appel pour dire quelles sont les élèves  dontt les parents recçevront un message 
#sur la page 5 il doit avoir une possibilité  de modifier l'appel 
#Après la deuxième validation de l'appel les données pourrait être enregistré dans ma base de donnée, le message générer  par groq, et envoyé au parent 

#v1-2 
#on ajoutera les infos sur les parents ayant payés qui doivent de l'argent et chaque mois un message sera envoyé au parent pour ce qui doivent 
#toujours fait PAR groq 

#on ajoutera les colonnes pour les notes de matières dans le back end une class note sera crée et sera lié à la classe élève
#on pourra aussi mettre  les notes des année précédentes  dans ma base de donnée pour préparé l'insertion du ml 
#l'accès aux éléves sera fait 

#v1-3
#création  d'un chatbot qui sera basé sur la base de donnée de l'école uniquement pour aider les enseignants ,
# les élèves sur les cours , 
#la direction sur les infos de l'école si par exemple la directrice demande qui n'a pas payé ce mois il envoie les noms des parent 
#il sera capable de  l'envoie de faire un message , utiliser le serveur termi  grâce à des connexion dans mon back end pour envoyer les messages fat si unquement la drectrice lui donne un ordre 
#pour les élèves il fera des quiz , assimilera les difficultés des enfants grâce à ça et envoyera un recapitulatif aux profs sur les difficultés de chaque enfant 
#sur une page avec le résumé de chaque élève 




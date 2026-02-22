#codons le shéma qui va être utilisé par l'api pour communiquer avec e front end 
from pydantic import BaseModel,Field, ConfigDict
from datetime import date ,datetime
#from model import selectionstatus,selectionslot,selectioninscription#j'importe quelque chose  que je crée dans mon fichier model pour l'utiliser



#API  pour mettre connexion vérification du login


#1) Creation de l'outils qui sertà pendre la requête dans le cas d'une création ou d'une modification du fron end 

class ecoleCreate (BaseModel):#colonnes rempli par l'utilisateur 
    school_norm:str 
    password_hash:str
    city_school:str
    #car utc c'est l'horaire universel de référence 
#2) Création de l'outils pour la class ecole qui va nous permettre de renvoyer une requête au fron end par  api

class ecoleOut(BaseModel):#colonnes qui vont être utilisés par le front end (client ) et  qui ne sont pas dangereuse si 
    #sont vues par le front end 
    #la colonne passeword_hash si elle est vue par mon front end c'est dangereux (commme le mdp n'est pas appelé par le  front end alors comment elle
    #fonctionne ?)

    
    school_norm:str#pour qu'elle aux requêtes de renvoie d'erreur si qu'elqun entrre un nom d'écoles déjà existant 
    id:int #On renvoie l'i en réponse pour que l e front end puisse le recopier, pour remplir les clés étranges 
    id_etablissement:str#car je veux les écoles puissent voir leurs identifiant et le noter car je ne les envois pas e,core par message 
    city_school:str
    #status_inscription:selectioninscription
    created_at:datetime
    #2_B) Configuration des attributs et des objets orm en dictionnaire car pour la conversion en json avant le retrour de la  requête seule les dictionnaires python
    # sont acceptés  
    model_config=ConfigDict(from_attributes=True)

#3) Création de l'outils  qui permet de créer dans ma base de donnée les classes 
class classeCreate(BaseModel):#cette partie était pensé pour remplir les données des écoles  
    ecole_id:int
    classe_scolaire_norm:str 

#4) Création de l'outils qui permet répondre  aux  requêtes en se basant sur la class classe
class classeOut(BaseModel):
    id:int #pour que je puisse récupérer 
    #ecole_id:int#Pour répondre aux requêtes qui utilise t les école par rapport aux classes

    classe_scolaire_norm :str #Pour répondre aux requettes d'erreur quand personne tape une classe qui existe déjà dans bdd mmais de manière différentes et aussi répondre aux requtês en rapport aec  la classe


    #4_b) Configuartion des objects orm et des attributs :
    model_config=ConfigDict(from_attributes=True)


#5)Outils  qui récupère une requête pour la  class student
class studentCreate (BaseModel):#il n' ya pas de body dan l'api get  que je veux faire c'est unitile

    
    classe_id:int 
   # matricule_norm :str 
   # name_student:str  
    #gender:str
    #blood_group:str|None #La colonne que je ne mets pas obligatoire à remplir dans ma base de donnée 
    #date_birth:str 
   # place_birth:str 
    #origin:str
    #residence:str
    #parent_contact:str


#7) Outils de qui permet de répondre aux requete de la base student

class StudentOut(BaseModel):#the data visualize by the admin 

    id:int#this is the primary Keys , they are automatic ,
    classe_id:int#this column can stay in the visualization by the admin ,
    matricule_norm :str 
    name_student:str 
    gender:str
    blood_group:str
    date_birth:str 
    place_birth:str 
    origin:str
    residence:str
    parent_contact:str

    
    model_config=ConfigDict(from_attributes=True)




class presenceCreate(BaseModel):
    student_id:int#les colonnes crées avec une clé étrange viont être remplis par le front end qui aura garder en mémoire la clé primaire 
    date_appel: date #je mest la classe  du jour par défaut 
    #status:selectionstatus #il va cliqué par l'utilisateeur  
    #horaires:selectionslot
class presenceOut(BaseModel):
    id:int
    stutend_id:int
    date_appel:date#date.today ce n'est pas une fonction
    #status:selectionstatus 
    #horaires:selectionslot


    
    model_config=ConfigDict(from_attributes=True) 
   

#Schéma pydantic pour le mot de passe et l'id de l'école pour qu'il  sache lors de la vérification  regarder le body  car j'ai mis la requêtes de l'objet json à l'intérieur 
class  tokenCreate(BaseModel):
    id_etablissement:str
    password:str

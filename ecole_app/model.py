 #Codage de la partie 
from sqlalchemy import Column, Integer , ForeignKey,String,Enum,Date, UniqueConstraint,DateTime,Float 
from sqlalchemy.orm import relationship 
from database import Base 
from enum import Enum as Enum_def#la class Enum importé du module enum sert à définir des  valeurs obligatoires qui seront choisi par l'utilisateur
from datetime import datetime,date,timezone
#A) Importation  des modules nécéssaires pour la fonction qui permet de créer des identifiants automatiquement dans ma base de donnée
import secrets
import string

#B)Fonction qui permet de créer  les identifiants ou des mots de passes ade manière aléatoire

#def generation_id(taille_id:int=10)->str :
    #création de la varible qui contiendra toutes les valeurs dans lesquels  la fonction prendra celles ci pour obtenir  des identig=fiants uniques
   # contenant=string.digits + string.ascii_uppercase 
   # return "".join(secrets.choice(contenant)  for i in range(taille_id))#continue à prendre de manière secrète  un élement et l'assembler avec les autres élèments déjà choisi tant  que le mdp n'a pas atteint la taille de 10 



    #1) création de la class ou de la table ecole 

class ecole (Base):

    __tablename__="ecoles"

    id=Column(Integer,primary_key=True)#il n'y apas d'appel avoir cette clée directement 


     #B)création de la colonne school_norm car je ne veux pas  voir dans ma base de donnée plusieurs ecole avec le même nom
    school_norm=Column(String,nullable=False,index=True)

    numero_school=Column(String,unique=True,nullable=True)
    #création de la colonne qui va permettre au établissement de se connecter grâce à un id spécifiques 
    id_etablissement=Column(String, index=True,nullable=False)
    #la colonne password ne doit pas exister car elle pourrait permettre une fuite de donnée , car les mots des utilisateurs seront stockés ddasn ma base de donnée
    #la ville de l'école  pour savoir pour moi qui va valider les inscriptions des écoles à mon site 
    city_school=Column(String,index=True,nullable=False)
    #colonne pour avoir les infod sur les éventuelles attaques possibles l'heure et la date des inscriptions 

    created_at=Column(DateTime,nullable=False,index=True,default=lambda :datetime.now(timezone.utc))
    password_hash=Column(String,nullable=False)#je ne mets pas index=True car cette colonne ne correspond pas à un lieu parmi les demandes  métiers que  je  ferai 
    
#1)pourquoi avec cette valeur selectioninscription.Etat_inscription_secondaire  dasn default ça marche et pas avec "non_validé" ou non_validé ?
    #comme ça  quand  un object sera cré dans  ma bdd c'est moi qui pourrait le modifier 
    #contrainte pour dire qu'il ne peut pas  exister dans une même ville une école avec le même nom 
    __table_args__=(UniqueConstraint("school_norm","city_school",name="ecole_city_unique"),)
#2) Création de la relation entre la class ecole et celle de la class classe
 

    attribut_classe=relationship("classe",back_populates="attribut_ecole")

   

#3) création de la class classe dans ma base de donnée 
class classe (Base):

    __tablename__="classes"
    #Pourquoi   dans chaque  class une colonne identification si cette classe a une relation  avec une autre grâce à relationship 

    id = Column(Integer,primary_key=True,index=True)
    #Base de donnée pour toutes les écoles ,donc des classes  se répeteront dans ma base de donnée
    #Cependant je veux 
    #a)Je veux avoir dans ma base de donnée pour chaque école des noms de classe uniques
    # b) Je veux que les minuscules et les majiscules soient reconnus comme la même chose pour éviter
    #  qu'ils note t  dans ma base donnée une même classe avec deux noms différents
      
    ecole_id=Column(Integer, ForeignKey("ecoles.id"),index=True,nullable=False)#pour faire cette cléé étrange ils utilisent les identification de la class ecole 

    #3)Création d'une colonne qui servira de stockage pour qu'aucune classe présente dans dans la base de donnée soit accpetée 
    #même si elle est écrit différement 
    classe_scolaire_norm=Column(String,nullable=False,index=True)#cette colonne doit être obligatoire dans ma base de donnée 
    #c'est la colonne normalisée qui sera réellemnt utilisé lors d'uen demande en rapport avec les classes non celle normale


    #4) Création de la contrainte unique composée pour répondre à mon problème B
    __table_args__ =(UniqueConstraint ("ecole_id","classe_scolaire_norm",name="condition_pas_de_classe_qui_se_repète_dans_une_classe"),)


    #3)relation entre la class ecole et celle classe  
    #Pour que chaque école dans ma base donnée ait ses classes
    attribut_ecole=relationship("ecole",back_populates="attribut_classe")#CE SONT juste des formules qui vont être utilisé dans l'api 
    

    #4) relation entre la classe et les élèves 
    attribut_eleve=relationship("student", back_populates="attribut_classe")



    #5) Création de la  class student qui servira  comme base de stockage pour la mette les eleves d'une classe 
    #pb :une classe n'est pas unique si on regarde toute la base de donnée cette classe doit être relié à son école sinon les élèevs seront enregistrés 
    # #dans une école où ils ne sont pas 
    # #est-ce -que le fait d'avoir relié les écoles et les classes alors dans la class classe il y'aura l'information de la classe avec l'école 
    #pour chaque identifiant et donc faire une  colonne classe_id qui sera une cké étrange se basant sur la colonne id de la class classe 
    # #relie déjà que que 1 correspond par exemple à la classse de cm2 de l'école JEAN PIAJGET 
    


class student(Base):
    #5-1) Attribution d'un nom que j'utiliserai pour la connecter à une autre classe grâce à ForeignKey
    __tablename__="students"
    #Que ce soit dans la même école ou des écoles différentes les il peut exister des enfants ayant le même nom complet en entier 
    name_student=Column(String,index=True,nullable=False)
    gender=Column(String,nullable=False)
    blood_group=Column(String)
    date_birth=Column(Date,nullable=False)
    place_birth=Column(String,nullable=False)
    origin=Column(String,nullable=False)
    residence=Column(String,nullable=False)
    #le numéro de téléphoen peut ne pas être unique car un parent peut avoir deux enfants 
    parent_contact=Column(String,nullable=False)
    #Le matricule est la seule colonne qui sera unique quelque soit 'école , la classe à l'échelle nationale , un matricule correspond uniquement à une seule ersonne 
     
    matricule_norm=Column(String,unique=True,nullable=False,index=True)#le cas où plusieurs élèves possèdent le même nom de famille , le seule moyen de les identifiés et le 
    #matricule 
    id=Column(Integer,primary_key=True,index=True)
    classe_id=Column(Integer,ForeignKey("classes.id"),index=True,nullable=False)#cette colonne utilise la colonne   id de la class classe
    #pour faire la clé étrange 
 
  
    #6) Relation entre les class classe et ecole en connectant juste avec la classs classe car cette class contient déjà les écoles de touts le classes 
    attribut_classe=relationship("classe",back_populates="attribut_eleve") 


    #7) Relation entre la class student et   celle des présences  

    attribut_presence=relationship("presence",back_populates="attribut_eleve")


    #8)Création de la class presence  

#Objectif ajouter la colonne  horaires dans ma class presence pour pemettre de limiter les dépenses financière de la personne 
#en envoyant les messages aux parents de manières réfléchis 






#11)modélisation de la class présence
class presence (Base):

    __tablename__="presences"
    id=Column(Integer,primary_key=True,index=True)
    student_id=Column(Integer,ForeignKey("students.id"),index=True,nullable=False)
    date_appel=Column(Date,index=True,nullable=False,default=date.today)

    #12)Etablissement des valeurs contraignantes dans bdd pour ces colonnes en utilisant la class Enum de sqlalchemy
    status=Column(String, nullable=False, index=False) #Like for  the moment i needn't create the api where it is necessare for me to take the
    #the status values and the  slot values
    horaires=Column(String,nullable=False,index=False)

    #13)Contraite :On veut empêcher que le message des parents puissent  être envoyé deux fois , et don on va empecher dans ma bdd que si le prof tape deux fois sur valider 
    #l'enregistrement dans la bdd se fait juste une fois ,,pourqu'un seul message soit envoyé 
    __table_args__=(UniqueConstraint("student_id","date_appel","horaires",name="no_send_twice_message"),)#l'attribut table_arg veut un tuple



    #6)Relation entre   la class student et la class presence
    attribut_eleve=relationship("student",back_populates="attribut_presence")


#Fonction création d'un json web token 
#un jwt a besoin  de la durée pendant  il est valide , le mot de passe secret pour  le sécuriser des hacker , et le  suj qui permet de dire où est 
#l'entité que nous cherchons dans le back end pour povoir prendre toute les ligne en rapport avec cette entité dans la bdd
#et potentiellement de l'heure de début du token  pour les log pour savoir plus tard à quelle  heure telle token a commencé à se onnecter pour savoir suspecter les tentatives de connexions
#cette fonction va être utilisé par la fonction de mon api et elle aura besoin du juste de l'id qui devra être fournis à chaque fois et de la clé de creation ou de connexion d'un token 
#le temps c'est mon back end qui fait le temps 
    #7)Relation with log table
    attribut_log=relationship("log",back_populates="attribut_presence")

class  log (Base):
    __tablename__="logs"
    id=Column(Integer,unique=True,nullable=False,index=True,primary_key=True)
    status_message=Column(String,nullable=False,index=True)
    messade_id=Column(String,nullable=True,unique=True)#car s in il ya une erreur i won't receive the value
    message=Column(String,nullable=True)
    presence_id=Column(Integer,ForeignKey("presences.id"),index=True,nullable=False)
    #school_id_2=Column(Integer,ForeignKey("ecoles.id"),index=True,nullable=False)
    solde=Column(Float,nullable=True)#si tu mets index True  ça veut dire que lorsque j'utilise que si je fais une requête de récupération d'une
    numero_destinataire=Column(String,nullable=True,index=True)#if one day i want see the history of this phone 
    message_price=Column(Float,index=False,nullable=True)#est_ce que je compte faire un api nqui me  pemettra de voir  le prix de chaque message
    code_operateur=Column(Integer,nullable=False) 
    #de données par query dans le back end j'obtiendras le resultat grâce à l'index directement 
    #or si je fais l'appel avecc cette colone que l'index est faux alors  mon bdd sera de fouiller ligne par ligne jusqu'à avir la valeur
#1) Pourquoi table_args nécessite une  liste  avec une , et c'est quoi _table_args une classe une   fonction ?
    #_table_args_=(UniqueConstraint("message_id","status_message", name="not"),)
    #connexion avec la  table presence 
    attribut_presence=relationship("presence",back_populates="attribut_log")
    

   #on ne peut relier deux tables vec relationship si lorqu'un se crée des éléments se crée aussi  dans l'autre table , ici quand on crée des écoles , aucuns champ dans la classe log est impacté automatiquement 

from fastapi import FastAPI,UploadFile,File,Depends,HTTPException,Form ,Header,Response,Cookie,Request
from schema import ecoleOut , ecoleCreate,classeOut,classeCreate,tokenCreate,presenceCreate
from database import Base,engine,get
from sqlalchemy.orm import Session
from io import StringIO
from csv import DictReader
from model import ecole,student,classe,presence,log
from sqlalchemy import  insert,func 
import os 
import csv 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import jose
import json 
import requests

#comme j'ai pappelé le fichier model même si mon api ne le nécessite pas  quand  je lance uvicorn sur
# un fichier automatiquement tous les fichoir qui sont appelé dans celui ci seront lancé afin de voir le resultat  de l'api 
#  

#Déclaration de la fatsapi 
app=FastAPI()

 

#On commence par récupérer ceux qui me permettra de reconnaître l'identifiant 

#Création de toutes les tables  dans mon modèle dans ma database 
Base.metadata.create_all(engine)
#Fonction de création d'un jwt
from jose import jwt
from datetime import datetime,timedelta




def create_jwt(id:int,secret_key:str):#cette fonction va devenir la fonction de création d'un  cookies 
     maintenant=datetime.utcnow()
     jwt_cre=jwt.encode({
          "sub":int(id),
          "iat":maintenant,#le temps à l'instant  présent
          "exp":maintenant + timedelta(hours=2)#la durée de vie de mon token avant qu'il redemande une  validation
     },
     secret_key,#ma clé secrète  je dois empêcher toutes personnes mal intentionee de m'attaquer 
     algorithm="HS256")
     #attribution du type de données envoyé dans le headers et creation d'un body dans l'object complex
     obj=Response(content=json.dumps({"status":"ok"}),media_type="application/json")
     obj.set_cookie(key="cookie",
     value=jwt_cre,
          httponly=True,
          secure=False,
          samesite="lax"#il gère une  sécurité pour les csp 
     )
      

     return obj #cette object contiendra à chaque fois le token , le type de donnée dans le headers  et un body avec un dictionnaire status:ok



#Fonctions création  de message ia
#Little variable to save  my environnetement variable 
  
def create_messe(nom_eleve:str,classe:str, ecole:str,status:str,appel:str):
     message=f"Bonjour Madame/Monsieur, nous tenons à vous informer de la part de l'école {ecole} que {nom_eleve}, classe de {classe}, est {status} à l'appel de {appel}."
     return message 
#Don't use the ai to build the message does the economises



#Function who will allow me use  termii (function to send the message )
# i take the environnetalement variable who is the secrets api_key 
api_key_vonage=os.getenv("API_VONAGE_ID")#Pour l'identification du compte"
api_key_von_secret=os.getenv("API_VON_SECRET")#C'est comme le mot de passe pour me connecter  à mon compte vonage 
url_vonage=os.getenv("URL_VONAGE")# c'est l'url de l'endpoints avec qui ma requête  fonctionnera  à qui j'enverrai ma requête ce n'est pas vraiment un secret  c'ets une url que tous les dev  connaissent 
#en argument de la fonction je devrais passer  plut^^ot un conteneur]wwrwrwr
def send_message(number,message):
     #I need to connect me at my account termii thanks the api_keys_secrets 
     #Well, like termii hasn't the sdk library who does the intern HTTP request 
     #i must do the request HTTP  LIKE i did on the fron end 
     #the fetch is requests
     #i need url ,  header , body sweetch the method 
     #Body termi description 
     
     body={ 
          "api_key":api_key_vonage,
          "api_secret":api_key_von_secret,
          "to":number,
          "text":message,
          "from":"SMS",#c'est le sender qui est le lus succeptible de passe pour les opérateurs Gabonais et ne soit pas bloqué par les dnd 
          "type":"text",#car le message que j'enverai pourra être encodé par un gsm standard il n'ya pas de caractère spéciales   
          #il n'ya pas  de clé channel  comme clé de l'object attendus par  l'api rest 
          
     }#Et dans le headers ça devient multipart/form-data car c'est une liste qui est envoyé et donc je n'ai 
     #plus besoin de convertir en json avant que la requêtes http parte
     requête_HTTP=requests.post(url_vonage,headers={"Content-type":"application/json"},data=json.dumps(body))
     return requête_HTTP.json()#la réponse du serveur qu'on reconvertit en dictionnaire ou en object pour python
     

app.mount("/static",StaticFiles(directory="static"),name="static")
#apparement je ne peux pas appeler directement appeler un fichier qui est sur mon ordi au front entd 
#car le front end est comme  à l'extérieur c'et comme si je demandais à un site web de prendre directement les ionfos sur mon ordi or il ne peutr ^pas 
#le fichier stati permet de créer une requêtes http qui permet de trouver ce fichier 





#Fonction pour pour hasher un mdp
from  passlib.context import CryptContext 
#Configuration de la manière  dont sera hashé mon mdp 

configuration_hash=CryptContext(schemes=["argon2"],deprecated="auto")

#2) Fonction de hashage d'un mot de passe 
def hash_mdp(mdp:str)->str:
     return configuration_hash.hash(mdp)

#3) Fonction de normalisation pour les avoir les noms sous un seul format et ainsi éviter d'avoir 
#une même école par exemple 2 fois dans ma bdd parce qu'elle est écris différement 

def normalize(mot:str)->str:
     #1)On met tout mot rentrant dans ma  bdd en miniscule
     variable_1=mot.lower()
     #2)Je gère les espace en début et en fin de mot 
     variable_2=variable_1.strip()
     #3)Je gère les espaces quin sont au milieu en transformant le mot  en liste 
     variable_3=variable_2.split()
     #et le resutat retourné je vais  joindre le mot comme je voudrais 
     return " ".join(variable_3)


#We're defining the rate limite 
from slowapi import Limiter 
from slowapi.util import get_remote_address#revoir le code source de cette fonction de rappelle je peux le modifier 

#url de la bdd où je stockerai 
url_redis=os.getenv("URL_REDIS")
#J'initialise the LImiter class
limite=Limiter(key_func=get_remote_address,storage_uri=url_redis)
#Je vais mettre l'object limite dans l'object natif app=Fastapi()



               


#Objectif quand j'utilise la fonction verif_code c'est pour empêcher u pirateur de hacker ma bdd même si il a l'url 

#pour passer directement à mon endpoints pour modifier mon back end il ets bloqué par le mot de passe 
#API pour  créer l'object école
@app.post("/formulaire_remplir")#il me propose de supprimer la promesse de renvoie d'un objet pour pouvoir prendre retourner juste l'id nécessaire 
#1)Pourquoi l'objet pydantic ecoleCreate n'était pas reconnu par mon serveur et à creer une erreur 422?
#2) Pourquoi on ne met pas l'identifiant dans l'object mais on le met  comme argument  de la fonction qui dérit ce que le server va recevoir(endpoint)?
#3) POurquoi mon vs était lent quand les arguments  de la fonction endpoints étaient déclaré avec un type Form?

#J'impose une limite (rate limite pour chaque ip)
#Pas optimale du tout , il faut pourvoir lever l'erreur 429 dans mon code pour faire comprendre à une personne ayant le même ip d'attendre avant de retenter de créer le compte 
#si la création de son compte n'était pas valide 
@limite.limit("4/4 minutes")

#Ici aussi c'est la même chose plusieurs  exceptions  de différentes librairies sont levées donc on met un try except pour  faire en sorte qu'il soit compris tous en un seul languages 
def formulaire (request:Request,school_norm:str=Form(...), #ici si il n' ya pas une un élément obligatoire une erreur 422 sera levé 
    password:str=Form(...),
    city_school:str=Form(...),
    id_etablissement:str=Form(...),numero_school:str=Form(...),
   fichier:UploadFile=File(...),db:Session=Depends(get)):# erreur inconnu mon model attendait un type de donné mais mon cerveau recevait un autre 
     #probablement les élements envoyés  ne contiennent the value the  key is present 

     if numero_school is None:
          raise HTTPException(status_code=404,detail="Il manque un élément la valeur du numéro")
          #norm_var=normalize()#pour éviter de faire l'appel de  la foncion de manière asynchronne
     #le nom d'une école existe déja dans ma bdd pour cette ville 
     #l'identifiant unique est fait par rapport au école+ville  ce problème est réglé par  le problème plus haut 
     #je dois faire en sorte que les écoles soient unique  dans chaque ville 
     condition_1=db.query(ecole).filter(ecole.city_school==normalize(city_school),
                                       ecole.school_norm==normalize(school_norm)).first()
          
     #cette condition prend dans ma bdd les écoles  avec la ville 
     if  condition_1:#si il existe dans ma bdd cette une école dont le nom et la ville correspond déjà à une dans ma bdd 
          raise HTTPException (status_code=409,detail="Cette école  existe déjà pour cette ville ")
    
     elif  not condition_1:#Ce sont les fonctions quinvont être tapé par l'humain c'est pour ça que je n'ai pas 'identifiant 
          obj_ecole=ecole(school_norm=normalize(school_norm),
                    city_school=normalize(city_school),
                    id_etablissement=normalize(id_etablissement),
                    password_hash=hash_mdp(password),
                    numero_school=numero_school#il peut avoir un problème sur le fait que l'élement que je prend sur le fron tend  a  le même  le nom que l'élément sur le back end 


                    )
          if  obj_ecole  is None :
               raise HTTPException(status_code=404,detail="L'object école n'ets pas crée ")
                    #4)Vu que je n'ai utilisé aucun object décrit dans pydantic le modèle sait comment il va  créer l'object ? 
                    #5)Pourquoi ne pas promettre à l'endpoint pour le remplissage du fomulaire lobjet json pour quil sache ceque cette enpoint devra renvoyer ?
                    # 6)Est-ce que mon front end renverra un multipart avec mon mdp ou un json qui le contient ?  
          db.add(obj_ecole)
          db.flush()
          id_school=obj_ecole.id#je mets juste en mémoire comme ça ma bdd n'est pas rempli si après le fichier uploader n'esst pas bon 
       
          doc_csv=fichier.file.read()#il me propose l'utilisation de await qui va permettre d'accélerer cette requêtes qui était lente 
          #et que d'autres requêtes puissent être exécuté en même 
          
          #2) je ne comprends pas  car il est arrive sous forme bianire à l'api donc je le decode 


          doc=doc_csv.decode("utf-8")#on obtient une chaêne de caractère mais python nécessite un fichier 
        
          sample=doc[:1600]#on récupère l'échantillon après le decodage 
               #After th have decode , how do you say at python how  is delimated the file ? 
          par_sniff=csv.Sniffer().sniff(sample,delimiters=";,")

               #Colonnes qui sont  attendus dans ma bdd pour le fichier csv 
          colonne_attendues=["matricule_eleve","nom_complet_eleve","classe_eleve","sexe_eleve","sang_eleve","lieu_naissance_eleve","date_naissance_eleve","numero_parent_1","residence","origin"]
          #3)Transformation  de la chaîne de caractère en faux fichier et lecture de  ce faux fichier csv 

          fake_file=DictReader(StringIO(doc), dialect=par_sniff)
          colonnes_csv=fake_file.fieldnames
          if set(colonne_attendues)!=set(colonnes_csv) :
               raise HTTPException(status_code=403,detail="les colonnes différentes")
               

          #Je voualais lire toutes les colonnes du fichier ligne par ligne
          #un fichier est comme un dictionnaire 
          condition_2=db.query(ecole).filter(ecole.id==id_school).first()
          for row in fake_file:
                    
               #Prendre la valeur de  chaque classe dans le fichier csv 
               classe_file=normalize(row["classe_eleve"])
               #classe_file  c'est la valeur de la classe lu sur la ligne 
            
               #Une classe ne peut ni être crée ou utilisé si je n'ai pas l'école 
               #condition_1=db.query(classe).filter(classe.ecole_id==id_school).first(), cette condition a une limite si l'école vient juste crée ou remplis comme dans le cas que l'école 
               #condition_1=db.query(ecole).filter(ecole.id==id_school).first()#je mets çanà l'extérieur du for pour éviter de vérifier à chaque ligne du fichier si l'école existe 
            
               #n'aura aucune classe donc cherhcer si l'école existe grâce au champ classe donnera 0 
               if not condition_2:
                    raise HTTPException (status_code=403,detail="ecole inexistante")
               #comme ça si un hacker a accès à ma bdd par mon endpoint il sera obligé de créer une école à chaque fois pour importé une un csv ce qui lui rend la tâche de piratage un peu plus soulantes
               if condition_2 :#l'école  existe on peut créer l'object classe en se basant sur la ligne obtenue par lecture de chaque ligne du csv du champ classe_éleve
                    #ou juste lire la classe car je ne vais pas créer un champ classe si j'ai déjà enregistreé dans mon data cette classe car des lignes de classes vont se répéter 
                 
                    #Si l'école existe on peut créer l'object classe 
                    # Pour créer l'object classe la classe qu'on veut créer ne doit pas exister dans bdd
                   
                    condition_3=db.query(classe).filter(classe.ecole_id==id_school,classe.classe_scolaire_norm==classe_file).first()

                    if  not condition_3 :#ça veut dire que la classe choisi n'existe pas encore dans ma bdd 
                    #Création de l'object classe pour chaque ecole 

                         obj_classe=classe(ecole_id=id_school,
                         classe_scolaire_norm=classe_file)
                              #ce n'est pas la  plu maligne des idées enregistrés  une classe par une si il ya énormement de classe c'est sera trop long
                              #même si  c'est la mémoire temporaire ça doit impaccter sur ma mémoire ou ma ram
                         db.add(obj_classe)
                         db.flush()#en met en mémoire temporaire car on va utiliser les identifaints de la classe pour importer chaque ligne du csv 
                         if obj_classe is None:
                              raise HTTPException(status_code=404, detail="Ton object classe  est vide")
                               #iF the object created isn't the data the one  was expecting , we'll raise the mistake
                         #Dans le cas la classe est crée on va creer toujours l'object pour importation du fichier en entier ligne par ligne
                         obj_import_csv =student( 
                              classe_id=obj_classe.id,
                              matricule_norm =normalize(row["matricule_eleve"]),
                              name_student=normalize(row["nom_complet_eleve"]),
                              gender=normalize(row["sexe_eleve"]),
                              blood_group=normalize(row["sang_eleve"]),
                              date_birth=row["date_naissance_eleve"],#car la date de naissance ne devrait pas en str mais en date 
                              place_birth=normalize(row["lieu_naissance_eleve"]),
                              origin=normalize(row["origin"]),
                              residence=normalize(row["residence"]),
                              parent_contact=normalize(row["numero_parent_1"])
                              )
                         db.add(obj_import_csv)
                              #Permet de mettre un identifiant automatiquement et de garder en mémoire, on est dans le cas d'un élève donc ça ne sert pas vraiment       
                 #De créer une nouvelle classe  je vais juste utiliser l'object déjà crée
                         #classe_scolaire_norm=obj_classe
                         #Dans le cas où on n'a pas crée l'objet classe mais plutôt utilisé la classe car elle était déjà dans la bdd 
                    elif condition_3:#si l'object classe existe déjà
                         obj_import_csv =student( 
                              classe_id=condition_3.id,#car condition_2 est l'object si la classe existe dans bdd
                              matricule_norm =normalize(row["matricule_eleve"]),
                              name_student=normalize(row["nom_complet_eleve"]),
                              gender=normalize(row["sexe_eleve"]),
                              blood_group=normalize(row["sang_eleve"]),
                              date_birth=row["date_naissance_eleve"],
                              place_birth=normalize(row["lieu_naissance_eleve"]),
                              origin=normalize(row["origin"]),
                              residence=normalize(row["residence"]),
                              parent_contact=normalize(row["numero_parent_1"])
                              )
                         db.add(obj_import_csv)
                              
          db.commit()#car c'est trop long de sauvegarder dans la bdd une ligne à la fois 
          return "ok"
     
      #je voudrais bien retourner l'identifiant dont l'écoel aura besoin pour se connecter , dois je le faire 
#sur un api get séparé ou je peux le retourner dans la fonction ? 

#cas où le fichier csv est vide 


#La fonction de vérification d'un mot de passe (création , it'sn't the enpoints, we needn't the rate limite 
def verif(password:str,password_hash:str):#Pour sauter le problème avec les  noms des arguments qui se ressemblent , j'utiliserai ma fonction de manière positionnel
#password_hash c'est le mot de passe provenant du back end et est hashé
#Je compare le mot de passe hashé dans mon back et celui envoyé dans mon front end   ce qui va permettre l'activation de sel qui s'active qu'au 
#mdp qui a subi le hashage
      return CryptContext(schemes=["argon2"],deprecated="auto").verify(password,password_hash)
      #le resultat sera vrai ou faux 
#API connexion mot de passe 

secret_keys=os.getenv("KEY_JWT")
@app.post("/authentification")# this isn't impactint for my database
@limite.limit("3/minutes")#si toutes les classes   doivent se connecter à la même horaire ce qui est logique 
#on part du principe un  adress ip public correspond au wifi d'une seule école 
def authentification(request:Request,t:tokenCreate,db:Session=Depends(get))->dict:

     obj_3=db.query(ecole).filter(ecole.id_etablissement==t.id_etablissement).first()

     if not obj_3:
          raise HTTPException(status_code=404,detail="Yayeeeee Cet identifiant n'existe pas")
     if obj_3:#La tokénisation va être use in this case 
          if  not verif(t.password,obj_3.password_hash):
               raise HTTPException(status_code=403,detail="Mot de passe érroné")
          return create_jwt(obj_3.id,secret_keys)#je le retourne directement car le resultat de la fonction est un object 
          #la tokénisation sera retournée
      #le badge sera crée dans le back end(serveur) ensuite envoyé vers le front end (le front end va le garder en méoire )  

#Fonction de creation d'un json web token  who serves me the bagde 

#We made the api get responsble de l'affichage des classes 


@app.get("/classe_display")


#si toutes les classes de l'écoles de manières simultanées se connectent et envoient une requête en même temps
#j'ai 10 classes  donc 10 professeurs en moyenne dans une école 
@limite.limit("12/minute")

#My goal will be display the class switch each école 
def display(request:Request,cookie:str=Cookie(...),db:Session=Depends(get)):
     #On doit prendre dans  le cookie le token  pour obtenir l'id de chaque classe pour l'affichage du contenu de chauqe classe 
     #dans l'endpoints suivants  

    try:
     #Pourquoi utilisons nous directement le nom  du cookie pour décoder le token ? 
     #On  le fait car lorsuqe nous utilisons l'object complexe Cookie on extrait auto^matiquement le token du cookie sans moins effort
     #Donc actuellement dans le cookie il n'ya quele token qui ets selctionné
          paylod=jwt.decode(cookie,secret_keys,algorithms="HS256")
          id_ecole_token=paylod["sub"]
          #il peut arriver que  token soit là mais sans le sujet et si je n'anticipe cette erreur en tant que hacer je peux jouer sur ça
          #pour balancer des requêtes et faire crasher mon code 
          if  id_ecole_token  is None:
               raise KeyError
     # expiré peut survenir , ou que quequ'un envoie un token qui  est inconnu par ma fonction 
     #jwt.decode une error de type exception   qui fera crashé le code et cette exception n'est pas reconnu par fastapi d'où le crash 
    except jose.exceptions.JWTError:
        # C'est ici que tombent les erreurs de token (expiré, faux, hacké)
          raise HTTPException(status_code=401, detail={"erreur":9,"message":"Token invalide ou expiré"})
     #on doit utliser try except pour attraper les erreurs  de tye except dans mon code
    except ValueError:
          raise HTTPException(status_code=401,detail={"erreur":10,"message":"Le type de ton token n'est pas celui attendu par ma bdd "})
    except KeyError:
          raise HTTPException(status_code=401,detail={"erreur":11,"message":"le sujet n'existe pas dans ce token"})
    #except  Exception:
          #raise HTTPException(status_code=403,detail={"erreur":12,"message":"erreur inconnu"})
     
     
    obj_school_classe=db.query(classe).filter(classe.ecole_id==id_ecole_token).all()
    #if not obj_school_classe :
          #raise HTTPException(status_code=403, detail={"error":13,"message":"tu n'es pas chez toi ici"})
    return obj_school_classe#je voulais renvoyer toutes les classes de l'écoles et sur mon front end je vais faire 
     #un tableau de chaque classe dont en cliquant sur une classe on  sera  dirié vers 
     #un tableau avec la liste des élèves  et une colonne dans ce tableau à choix multiple qui correponds à présent , absent , en retard etc





#Api Get responsable de l'affichage des l'affichage des élèves d'une classe 
@app.get("/display_student_classe/{classe_id}")

@limite.limit("12/minutes")
def display(request:Request,classe_id:int,cookie:str=Cookie(...),db:Session=Depends(get)):
     #la présence avant la correspondance
     try:
     
     # I deblock the token  to have access the endpoints
          token=jwt.decode(cookie,secret_keys,algorithms="HS256")
          value_id=token["sub"]
          # je m'en moque que d'autres classes puissent voir les classes les élèves d'une autres classes 
          #cependant je ne veux pas qque d'autres écoles voient les éleves des classes d'autres écoles 
          #ça tombe bien la  rable classe possède une clé étrange fait à partir de la l'id de la table école 
          #la table student est composé de la clé étrange qui class_id qui provient de l'id des élément dans la table classe
     except jose.exceptions.JWTError:
          raise HTTPException(status=1,detail={"erreur":14,"message":"Le token ou l'object envoyé ne correspond à ce qui a été donnée"})


     except Exception :
          raise HTTPException(status_code=4,detail={"erreur":15,"message":"Accès non autorisé , erreur non antcipé mais mon serveur ne va pas crashé"})
          #i'm going to block the personne who want to entry inside my application without the well token , #c'est unitile 
          #car la classe jwt.decode lève une erreur elle même et n'utilise pas python , donc une erreur qu'on ne peut pas empêcher 
          #si on me hacke de sortir une erreur 500 (bref à revoir )
      #j'ai fait une erreur je mets le Token dans mes arguments  mais je en vérifie so whoever or anybody can entry in ma endoinpst with his token 
      #I must ever check out the tokenvalue     
     #je prend les élèves de toutes la classe demandé par mon fetch
     obj_student=db.query(student).join(classe).filter(classe.ecole_id==value_id,student.classe_id==classe_id).all()
     if not obj_student :#j'anticipe si il le hacker passe mon token je veux lui compliquer un peu la tâche 
          raise HTTPException(status_code=5,details={"erreur":16,"message":"l'identifiant de la classe choisie 'existe pas"})
     return obj_student#je pourrai faire afficher tous les élèves de la classe sur le front end je préfère retouner tout l'objet car j'aurai besoin des id des élèves pour la table suivantes





import asyncio
#from the moment the cookies block the extern resquets

@app.post("/presence_appel")

@limite.limit("12/minute")

async def presence(request:Request,cookie:str=Cookie(...),identifiant_eleve:list[int]=Form(...),horaires:str=Form(...),date_jour:str=Form(...),status:list[str]=Form(...),db:Session=Depends(get)):
     try:
     #On doit d'abord décoder le token  et l'ouvrir
          variable=jwt.decode(cookie,secret_keys,algorithm="HS256")
          id_token=variable["sub"]

     except Exception:
          raise HTTPException (status_code=403,detail={"erreur":17,"message":"plusieurs erreurs erreur possibles en rapport avec le token "})
     #On a réellemnt du sujet de l'école je ne pense pas car l'id de classe student prend toute le ligen de la table
     #cette ligne qui a classe_id , classe_id=classe.id  qui prend aussi la lligne de manière récursive  on a l'école grâce student.id 
     #le token servait juste de clé 
     #je dois enregitrer les valeurs provenant dans mon navigateur  vers  mon serveur 
     #cependant des règles métiers doivent être respectées
     #on doit empêcher que dans ma bdd  qu'une ligen avec les mêmes   student_id","date_appel","horaires"
     #est-ce qu'on va lire par ligne pas ligne ? 
     #Le problème n'est pas de lire ligne par ligne mais de faire en sorte que des données soient crées 
     #uniquement si ils  remplissent mes coinditions 
     #et c'est pareil pour les messages 
     #Regle 1 je ne tolère pas que les appels de début de cours me renvoient absent 
     appel_debut=["appel_1","appel_3","appel_5","appel_7"]
     appel_fin=["appel_2","appel_4","appel_6","appel_8"]
     #les valeurs à l'intérieur  de ces set  doivent correspondre aux valeurs qui sont sur mon front end
     #Je ne lèverai pas l'erreur en m'appuyant sur ma bdd  car mon modèle ,ne décrit pas cette règle métier 
     if horaires in appel_debut:#c'est une liste je en peux pas fairz  juse status=="à la valeur que je veux je dois faire un for pour y accéder "
          for stat in status:
               if stat=="absent":
                    raise HTTPException(status_code=403, detail={"erreur":18,"message":"status invalide pour cette horaire"})
     if horaires in appel_fin:
          for stat in status:
               if stat=="retard":
                    raise HTTPException(status_code=403,detail={"erreur":19,"message":"status pour cette horaire invalide"})
     #On veut limiter la latence donc on va vérifier en  classe_groupe pour savoir si il 
     #existe des cas où des lignes avce la même heure, le même jour et le même sont appélés donc on va utiliser un in 
     liste_student_classe=[i for i in identifiant_eleve]
     #L'erreur  métier qui va suivre est définie dans mon modèle donc on  peut utiliser un query pour comparer  format de modèle attendus 
     #cette ligne permet de gérer la multiténacité, c'est à dire qu'aucune école   A ne peut faire un query  pour les élements 
     #des écoles n , cependant si une ecole essaye je ne serai pas si il y a un hacker dans mon site qui teste des trucs donc je dois lever une erreur 
     #pour dire que les élèves qui puissent appeler par une école soient les élèves de cette école 

     obj=db.query(presence).join(student,student.classe_id==classe.id).join(classe,classe.ecole_id==ecole.id).filter(classe.ecole_id==id_token,presence.student_id.in_(liste_student_classe),presence.horaires==horaires,presence.date_appel==date_jour).all()
     #je prends tous les élèves dont il ya une répétitions et je lève l'erreur
     
     if obj:
          raise HTTPException(status_code=403, detail={"erreur":20,"message":"vous avez déjà fait l'appel pour cette heure là à ce jour là"})
     #i choisit de ne pas faire l'enregistrement des   données avant d'envoyer un message
     # car si il ya coupure entre l'enregistrement de l'appel et l'envoie des messages , l'appel pour 
     # l'heure x sera stocké dans ma bdd et j'ai une contrainte qui empêche la répétition d'appel  pour les mêmes horaires deux fois dans 
     # ma bdd , donc j'enregistrerais que lorsque les messages seront parties 
     #Conditions pour  faire les messages
     #comme c'est par rapport à ceux que  le front end  m'apportera que je ferai mes messages ou pas 
     #création des messages de retard 
     #Pour tous les  éleves le status
     liste_id_eleve=[i for i in identifiant_eleve] 
     #La multiténacité 
     #Comme je ne vérifie pas quelle école fait le query vers ma bdd une école peut changer juste l'id d'une classe et avoir les infos des élèves d'une autre école 
     donnees_1=db.query(presence,student,classe,ecole ).join(student).join(classe).join(ecole).filter(ecole.id==id_token,presence.date_appel==date_jour,presence.horaires=="appel_1",presence.student_id.in_(liste_id_eleve),presence.status=="retard").all()
     #en  prenant avec all je prends pour chaque ligne de mon metadata une ligne qui contient avec une seule ligne l'identifiant de l'élève sont status  au jour x à l'heure y et comme j'ai connecté les tables 
     #avec une ligne j'ai la classe , son nom  et son école 
     #Quand j'ai tous les retardataires de la classe je fais  maintenant la creation et l'envoie du message 
     #les noms de élèves  ne sont pas dans ma table presence mais dans  la table student
     #les classes sont dans la table classe 
     #les noms des écoles sont dans la  table ecole 
     #nous avons besoin de ces élements pour faire le message
     #donc on join les tables selon 
     #i'm going to take  certains object  inside among the response sent me back by the termii servor 
     liste_obj=[]

     for obj_1 in  donnees_1: 
          #On crée les messages  d'un élève à la fois 
          message_1=create_messe(nom_eleve=obj_1.student.name_student,classe=obj_1.classe.classe_scolaire_norm, ecole=obj_1.ecole.school_norm,status=obj_1.presence.status,appel="appel_1")#normalement le message est crée 
          #pour rassurer que pour chaque élève on a bien le numéro de son parent  et pas le numéro du parent de quelqu'un d'autre 
          #on va stocker le message  et le numéro à qui ce message devra être envoyé crée dans  une liste  au fur et à mesure que les messages des élèves se créent pour un élève à la fois un numéro 
          #pour l'instant partons sur une consommation de 2 écoles maximums don 600 MESSAGES par appel   dans le pire des monde 
          reponse_vonage_1= await send_message(message_1,obj_1.student.parent_contact)#lenvoie des messages vers le fournisseur est asynchrone
          res=await reponse_vonage_1.json()#je me suis trompé avant ce n'est pas l'envoie de message qui peut prendre des messages mais plutôt la réponse  suite à la requête          
          #attendre   0.01s après une requête est unitilie dans mon cas une requête pour aller jusqu'à l'api termii peut prendre 
          #énormément de temps  environ 1 s  sans compter le temps que mon api return une réponse à mon front end
          #await asyncio.sleep(0.01)
          #here's the response resend by vonage api {
  #"message-count": "1",
  #"messages": [
   # {
     # "to": "33612345678",
      #"message-id": "0A0000001234567B",
      #"status": "0",
      #"remaining-balance": "14.55780000",
      #"message-price": "0.06320000", 
      #"network": "20810"
    #}
  #]
#}
#{
 # "message-count": "1",
 # "messages": [
 #   {
    #  "status": "2",
    #  "error-text": "Missing From parameter"
    #}
  #]
#}
          
          #for each case we register  an object
          if res["messages"][0]["status"]!="0":
               obj_log1={}
               #i'm registe the object 
               #the name inside  the square brackets  and the quotes
               obj_log1["message"]=res["messages"][0]["error-text"]#i save the message 
               obj_log1["status_message"]=res["messages"][0]["status"]
               
               


               #i need retrieve the   id presence and id school  that i'll put inside the object created
               obj_log1["presence_id"]=obj_1.presence.id#comme obj correpond à celui récupérer  l'object qui est ligne presence 
               obj_log1["school_id"]=obj_1.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
               
              
               liste_obj.append(obj_log1)
               
              
          #case 2 where  termii return me ok 

          elif res["messages"][0]["status"]=="0":
               #I create the dctionnairy where i'll put the object
               obj_log2={}
               #i fill this dictionnary by the value send back by termii
               obj_log2["numero_destinataire"]=res["messages"][0]["to"] 
               obj_log2["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
               obj_log2["status_message"]=res["messages"][0]["status"]
               obj_log2["solde"]=res["messages"][0]["remaining-balance"]
               obj_log2["message_price"]=res["messages"][0]["message-price"]
               obj_log2["code_operateur"]=res["messages"][0]["network"]

               

               #WE take the id will serve me inside the obJECT 1
               obj_log2["presence_id"]=obj_1.presence.id#needn't get it is an object 
               obj_log2["school_id"]=obj_1.ecole.id#j'ai le droit de viser l'id d'une table précise 
               
               #Now i put this object inside the   object list
               liste_obj.append(obj_log2)

     stockage_way=insert(log).values(liste_obj)
     db.execute(stockage_way)
     db.commit()#Je viens d'enregistrer  les données dans la bdd de données l'appel suivant va faire 




          #j'enregistrerais les données pour mes logs ici 
     #Pour l'instant appel de fin de cours nméro 2
     #je prends dans ma bdd jointe l'appel_2 pour faire les messages 
     #Multiténacité  on vérifie que l'école que l'école qui fairt la requête aura des infos que de son école et si elle met des élements qui sont  dans une autre école  
     #elle n'aura pas  les infos de cette autres écoles et même si je ne suis pas au courant pour l'instant de qui veut me hacker ce n'est pas grave 
     donnee_2=db.query(presence,student,classe,ecole).join(student).join(classe).join(ecole).filter(ecole.id==id_token,presence.status=="absent",presence.horaires=="appel_2",presence.date_appel==date_jour).all()
     
     if donnee_2 :
          for obj_2 in donnee_2:
               message_2=create_messe(nom_eleve=obj_2.name_student,classe=obj_2.classe_scolaire_norm,ecole=obj_2.school_norm,status=obj_2.status,appel="appel_2")
               #j'envoie le sms à termii
               requête_vonage_2=await send_message(message=message_2,numero=obj_2.parent_contact)
               res= await requête_vonage_2.json()# je convertis en object  le json envoyé
               #je recupère la réponse de la réponse envoyé par 
               asyncio.sleep(0.1)#i say  wait 0,1 before send the first message 


               if res["messages"][0]["status"]=="0":
                    #I create the dctionnairy where i'll put the object
                    obj_log3={}
               #i fill this dictionnary by the value send back by termii 
                    obj_log3["numero_destinataire"]=res["messages"][0]["to"] 
                    obj_log3["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
                    obj_log3["status_message"]=res["messages"][0]["status"]
                    obj_log3["solde"]=res["messages"][0]["remaining-balance"]
                    obj_log3["message_price"]=res["messages"][0]["message-price"]
                    obj_log3["code_operateur"]=res["messages"][0]["network"]
               
               
               #WE take the id will serve me inside the obJECT 1
                    obj_log3["presence_id"]=obj_2.presence.id#needn't get it is an object 
                    obj_log3["school_id"]=obj_2.ecole.id#j'ai le droit de viser l'id d'une table précise 
               
               #Now i put this object inside the   object list
                    liste_obj.append(obj_log3)

               elif res["messages"][0]["status"]!="0":
                    obj_log4={}
               #i'm registe the object 
               #the name inside  the square brackets  and the quotes
                    obj_log4["message"]=res["messages"][0]["error-text"]#i save the message 
                    obj_log4["status_message"]=res["messages"][0]["status"]

               #i need retrieve the   id presence and id school  that i'll put inside the object created
                    obj_log4["presence_id"]=obj_2.presence.id#needn't get it is an object 
                    obj_log4["school_id"]=obj_2.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
                    liste_obj.append(obj_log4)
          stockage_way=insert(log).values(liste_obj)
          db.execute(stockage_way)
          db.commit()

     #Appel_3
    #2 ème  appel de début de cours 
     donnee_3=db.query(presence).join(student).join(classe).join(ecole).filter(presence.status=="retard",presence.horaires=="appel_3",presence.date_appel==date_jour).all()
    

     if donnee_3 and donnee_2:
          for obj_3  in donnee_3:
               message_3=create_messe(nom_eleve=obj_3.name_student,classe=obj_3.classe_scolaire_norm,ecole=obj_3.school_norm,status=obj_3.status,appel="appel_3")
               #j'envoie le sms à termii
               requête_termii_3=send_message(message=message_3,numero=obj_3.parent_contact)
               res=requête_termii_3.json()# je convertis en object  le json envoyé

               #je recupère la réponse de la réponse envoyé par 
               if res["messages"][0]["status"]=="0":
                    #I create the dctionnairy where i'll put the object
                    obj_log5={}
               #i fill this dictionnary by the value send back by termii 
                    obj_log5["numero_destinataire"]=res["messages"][0]["to"] 
                    obj_log5["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
                    obj_log5["status_message"]=res["messages"][0]["status"]
                    obj_log5["solde"]=res["messages"][0]["remaining-balance"]
                    obj_log5["message_price"]=res["messages"][0]["message-price"]
                    obj_log5["code_operateur"]=res["messages"][0]["network"]
               
               #WE take the id will serve me inside the obJECT 1
                    obj_log5["presence_id"]=obj_3.presence.id#needn't get it is an object 
                    obj_log5["school_id"]=obj_3.ecole.id#j'ai le droit de viser l'id d'une table précise 
                    liste_obj.append(obj_log5)

               elif res["messages"][0]["status"]!="0":
                    obj_log6={}
               #i'm registe the object 
               #the name inside  the square brackets  and the quotes
                    obj_log6["message"]=res["messages"][0]["error-text"]#i save the message 
                    obj_log6["status_message"]=res["messages"][0]["status"]
               
               
               #i need retrieve the   id presence and id school  that i'll put inside the object created
                    obj_log6["presence_id"]=obj_3.presence.id#needn't get it is an object 
                    obj_log6["school_id"]=obj_3.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
                    liste_obj.append(obj_log6)
          stockage_way=insert(log).values(liste_obj)
          db.execute(stockage_way)
          db.commit()



     #2 appel de fin de cours 
     donnee_4=db.query(presence).join(student).join(classe).join(ecole).filter(presence.status=="absent",presence.horaires=="appel_4",presence.date_appel==date_jour).all()
     if donnee_4 and donnee_2:
          for obj_4 in donnee_4:
               message_4=create_messe(nom_eleve=obj_4.name_student,classe=obj_4.classe_scolaire_norm,ecole=obj_4.school_norm,status=obj_4.status,appel="appel_4")
               #j'envoie le sms à termii
               requête_termii_4=send_message(message=message_4,numero=obj_4.parent_contact)
               res=requête_termii_4.json()# je convertis en object  le json envoyé

               if res["messages"][0]["status"]=="0":
                    #I create the dctionnairy where i'll put the object
                    obj_log7={}
               #i fill this dictionnary by the value send back by termii 
                    obj_log7["numero_destinataire"]=res["messages"][0]["to"] 
                    obj_log7["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
                    obj_log7["status_message"]=res["messages"][0]["status"]
                    obj_log7["solde"]=res["messages"][0]["remaining-balance"]
                    obj_log7["message_price"]=res["messages"][0]["message-price"]
                    obj_log7["code_operateur"]=res["messages"][0]["network"]
               
               #WE take the id will serve me inside the obJECT 1
                    obj_log7["presence_id"]=obj_4.presence.id#needn't get it is an object 
                    obj_log7["school_id"]=obj_4.ecole.id#j'ai le droit de viser l'id d'une table précise 
                    #we register the element 
                    liste_obj.append(obj_log7)


               elif res["messages"][0]["status"]!="0":
                    obj_log8={}
               #i'm registe the object 
               #the name inside  the square brackets  and the quotes
                    obj_log8["message"]=res["messages"][0]["error-text"]#i save the message 
                    obj_log8["status_message"]=res["messages"][0]["status"]
               
               
               #i need retrieve the   id presence and id school  that i'll put inside the object created
                    obj_log8["presence_id"]=obj_4.presence.id#needn't get it is an object 
                    obj_log8["school_id"]=obj_4.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
                    liste_obj.append(obj_log8)
               
          stockage_way=insert(log).values(liste_obj)
          db.execute(stockage_way)
          db.commit()
      #Cas 5          
     donnee_5=db.query(presence).join(student).join(classe).join(ecole).filter(presence.status=="retard",presence.horaires=="appel_5",presence.date_appel==date_jour).all()
     if donnee_5 and donnee_4:
          for obj_5 in donnee_5:
               message_5=create_messe(nom_eleve=obj_5.name_student,classe=obj_5.classe_scolaire_norm,ecole=obj_5.school_norm,status=obj_5.status,appel="appel_5")
               #j'envoie le sms à termii
               requête_termii_5=send_message(message=message_5,numero=obj_5.parent_contact)
               res=requête_termii_5.json()# je convertis en object  le json envoyé

               if res["messages"][0]["status"]=="0":
                    #I create the dctionnairy where i'll put the object
                    obj_log9={}
               #i fill this dictionnary by the value send back by termii 
                    obj_log9["numero_destinataire"]=res["messages"][0]["to"] 
                    obj_log9["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
                    obj_log9["status_message"]=res["messages"][0]["status"]
                    obj_log9["solde"]=res["messages"][0]["remaining-balance"]
                    obj_log9["message_price"]=res["messages"][0]["message-price"]
                    obj_log9["code_operateur"]=res["messages"][0]["network"]
               
               #WE take the id will serve me inside the obJECT 1
                    obj_log9["presence_id"]=obj_5.presence.id#needn't get it is an object 
                    obj_log9["school_id"]=obj_5.ecole.id#j'ai le droit de viser l'id d'une table précise 
                    liste_obj.append(obj_log9)

               elif res["messages"][0]["status"]!="0":
                    obj_log10={}
               #i'm registe the object 
               #the name inside  the square brackets  and the quotes
                    obj_log10["message"]=res["messages"][0]["error-text"]#i save the message 
                    obj_log10["status_message"]=res["messages"][0]["status"]
               
               
               #i need retrieve the   id presence and id school  that i'll put inside the object created
                    obj_log10["presence_id"]=obj_5.presence.id#needn't get it is an object 
                    obj_log10["school_id"]=obj_5.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
                    liste_obj.append(obj_log10)

          stockage_way=insert(log).values(liste_obj)
          db.execute(stockage_way)
          db.commit()


     #pour l'appel 6 3ème appels fin de cours 
     donnee_6=db.query(presence).join(student).join(classe).join(ecole).filter(presence.status=="absent",presence.horaires=="appel_6",presence.date_appel==date_jour).all()
     if donnee_6 and donnee_4:
          for obj_6 in donnee_6:
               message_6=create_messe(nom_eleve=obj_6.name_student,classe=obj_6.classe_scolaire_norm,ecole=obj_6.school_norm,status=obj_6.status,appel="appel_6")
               #j'envoie le sms à termii
               requête_termii_6=send_message(message=message_6,numero=obj_6.parent_contact)
               res=requête_termii_6.json()

               if res["messages"][0]["status"]=="0":
                    #I create the dctionnairy where i'll put the object
                    obj_log11={}
               #i fill this dictionnary by the value send back by termii 
                    obj_log11["numero_destinataire"]=res["messages"][0]["to"] 
                    obj_log11["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
                    obj_log11["status_message"]=res["messages"][0]["status"]
                    obj_log11["solde"]=res["messages"][0]["remaining-balance"]
                    obj_log11["message_price"]=res["messages"][0]["message-price"]
                    obj_log11["code_operateur"]=res["messages"][0]["network"]
               
               #WE take the id will serve me inside the obJECT 1
                    obj_log11["presence_id"]=obj_6.presence.id#needn't get it is an object 
                    obj_log11["school_id"]=obj_6.ecole.id#j'ai le droit de viser l'id d'une table précise 
               
               elif res["messages"][0]["status"]!="0":
                    obj_log12={}

               #the name inside  the square brackets  and the quotes
                    obj_log12["message"]=res["messages"][0]["error-text"]#i save the message 
                    obj_log12["status_message"]=res["messages"][0]["status"]
               
               

               #i need retrieve the   id presence and id school  that i'll put inside the object created
                    obj_log12["presence_id"]=obj_6.presence.id#needn't get it is an object 
                    obj_log12["school_id"]=obj_6.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
                    liste_obj.append(obj_log12)
               
          stockage_way=insert(log).values(liste_obj)
          db.execute(stockage_way)
          db.commit()
     #pour l'appel 7  ,4 appels de  début  de cours 

     donnee_7=db.query(presence).join(student).join(classe).join(ecole).filter(presence.status=="retard",presence.horaires=="appel_7",presence.date_appel==date_jour).all()
     if donnee_7 and donnee_6:
          for obj_7 in donnee_7:
               message_7=create_messe(nom_eleve=obj_7.name_student,classe=obj_7.classe_scolaire_norm,ecole=obj_7.school_norm,status=obj_7.status,appel="appel_7")
               #j'envoie le sms à termii
               requête_termii_7=send_message(message=message_7,numero=obj_7.parent_contact)
               res=requête_termii_7.json()
               


               if res["messages"][0]["status"]=="0":
                    #I create the dctionnairy where i'll put the object
                    obj_log13={}
               #i fill this dictionnary by the value send back by termii 
                    obj_log13["numero_destinataire"]=res["messages"][0]["to"] 
                    obj_log13["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
                    obj_log13["status_message"]=res["messages"][0]["status"]
                    obj_log13["solde"]=res["messages"][0]["remaining-balance"]
                    obj_log13["message_price"]=res["messages"][0]["message-price"]
                    obj_log13["code_operateur"]=res["messages"][0]["network"]
               
               #WE take the id will serve me inside the obJECT 1
                    obj_log13["presence_id"]=obj_7.presence.id#needn't get it is an object 
                    obj_log13["school_id"]=obj_7.ecole.id#j'ai le droit de viser l'id d'une table précise
               #WE SAVE THE DICTionnary
                    liste_obj.append(obj_log13) 

               elif res["messages"][0]["status"]!="0":
                    obj_log14={}
               #i'm registe the object 
               #the name inside  the square brackets  and the quotes
                    obj_log14["message"]=res["messages"][0]["error-text"]#i save the message 
                    obj_log14["status_message"]=res["messages"][0]["status"]
               
               

               #i need retrieve the   id presence and id school  that i'll put inside the object created
                    obj_log14["presence_id"]=obj_7.presence.id#needn't get it is an object 
                    obj_log14["school_id"]=obj_7.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
                    liste_obj.append(obj_log14)
               
          stockage_way=insert(log).values(liste_obj)
          db.execute(stockage_way)
          db.commit()

     #Pour le dernier appel  4 eme appel fin des cours 
     donnee_8=db.query(presence).join(student).join(classe).join(ecole).filter(presence.status=="absent",presence.horaires=="appel_8",presence.date_appel==date_jour).all()
     if donnee_8 and donnee_5:
          for obj_8 in donnee_8:
               message_8=create_messe(nom_eleve=obj_8.name_student,classe=obj_8.classe_scolaire_norm,ecole=obj_8.school_norm,status=obj_8.status,appel="appel_8")
               #j'envoie le sms à termii
               requête_termii_8=send_message(message=message_8,numero=obj_8.parent_contact)
               res=requête_termii_8.json()

               if res["messages"][0]["status"]=="0":
                    #I create the dctionnairy where i'll put the object
                    obj_log15={}
               #i fill this dictionnary by the value send back by termii 
                    obj_log15["numero_destinataire"]=res["messages"][0]["to"] 
                    obj_log15["message_id"]=res["messages"][0]["message-id"]#here i take the  text    who correponds at this key 
                    obj_log15["status_message"]=res["messages"][0]["status"]
                    obj_log15["solde"]=res["messages"][0]["remaining-balance"]
                    obj_log15["message_price"]=res["messages"][0]["message-price"]
                    obj_log15["code_operateur"]=res["messages"][0]["network"]
               
               #WE take the id will serve me inside the obJECT 1
                    obj_log15["presence_id"]=obj_8.presence.id#needn't get it is an object 
                    obj_log15["school_id"]=obj_8.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #We save the dictionnary  that i received 
                    liste_obj.append(obj_log15)

               elif res["messages"][0]["status"]!="0":
                    obj_log16={}
               #i'm registe the object 
               #the name inside  the square brackets  and the quotes
                    obj_log16["message"]=res["messages"][0]["error-text"]#i save the message 
                    obj_log16["status_message"]=res["messages"][0]["status"]
               
               

               #i need retrieve the   id presence and id school  that i'll put inside the object created
                    obj_log16["presence_id"]=obj_8.presence.id#needn't get it is an object 
                    obj_log16["school_id"]=obj_8.ecole.id#j'ai le droit de viser l'id d'une table précise 
               #I register the object inside the list
                    liste_obj.append(obj_log16)
               
          #J'ai une liste d'objet je peux l'enregister en une fois dans ma bdd 
     #je vais faire l'insertion de tous  mon ditionnaire dans ma bdd
     stockage_way=insert(log).values(liste_obj)
     db.execute(stockage_way)
     db.commit()
     return "OK"





#L'api qui remplira la table présence e, enverra les messsages , les compteras  

#Je dois faire un api qui me  permet d'afficher le nombre de message de message de l'école et la somme 
@app.get("/message")

@limite.limit("12/minute")
#on aura besoin du token  car je veux protéger cette api et que je veux que chauqe école voit les messages qu'ils ont dépensé 
#après je mettrais  le temps à l'intérieur ppur afficher que le nombre de message par  mois  et que le message se rénitialise à la fin 
def somme_spent(request:Request,cookie:str=Cookie(...),db:Session=Depends(get)):
     try:
     #Decodons le token qui est arrivé et  qui contient le sujet qui est l'id de l'école  pour 
     #qu'un personne sans  le bon token puisse accéder à ces données , même si il sait qu'in faut un token 
          token_decode=jwt.decode(cookie,secret_keys,algorithm="HS256")#je viens de decoder le token qui  était coder et je viens de vérifier si la 
     #clé secrète et le token attendus correspond à ce qui devrait être vu par mon api c'est surtout  grâce à la clé étrange
     #je dois mainteant récupérer les lignes dans ma base de donnée 
     #par école  le nombre de message dont le status est ok et la somme de tous les messages 
     #car je suppose qu'on a obtenu un dictionnaire après le décodage 
     #comme la fonctin  jwt.decode ne vérifie  pas nativement le sujet dans un token  car c'est claims champs optionnel 
     # je vis forcer le code à prendre l'absence  dusujet comme une exception à lever 
          id_ecole=token_decode["sub"]
          if   id_ecole is None:
               raise HTTPException(status_code=403,detail={"error":21,"message":"Le sujet n'est pas présent dans  le token "})

     except Exception:
          raise HTTPException(status_code=403,detail={"error":22,"message":"l'erreur est  en rapport avec le token"})
     #mantenant je vais récupérer toute  les lignes pour chaque écoles 
     #c'est longs uniquement de prendre tout à la fois prend ce dont tu as besoin 
     
     #Finalement je prendrai en une seule requête tout ce dont j'aurai besoin 
     #au lieu de prendre unresultat à la fois je prendrais tous les resultats 
      #Je prend que le nécessaire  dans ma bdd pour mon api , c'est à dire ici les colonnes
     obj_values=db.query(func.count(log.status_message),func.sum(log.message_price)).join(ecole).filter(ecole.id==id_ecole,log.status_message=="0").first()#
     #Je prend que le nécessaire  dans ma bdd pour mon api , c'est à dire ici les colonnes,log.status_message).first()#
     #ps j'ai le nombre de message par rapport à l'école que j'envoie 
     #je vais récupérer la somme total de messages envoyés par une école 

     # vérificatiion du resultat envoyé pour prévoir  qu'une école n'ait pas envoyé de message 
     #obj_vaues[0]-> resultat de  func.count(log.status_message)(le nombre de méssage totales pour une école)
     #obj_vaues[1]-> resultat funct.sum(log.message_price) 
     if  obj_values[0]!=0  and  obj_values[1] is not None:#
          obj_sent={"mess_sent":obj_values[0],#je mets le resultat obtenue pour le comptage
          "mess_spent_total":round( obj_values[1]*655.957,0)}#pour que le prix soit en franccefa gabonais? au gabon personne n'utilise 10 franc ou 5 francs 
          

     elif obj_values[0]==0  and obj_values[1] is None:
          obj_sent={"mess_sent":obj_values[0],
          "mess_spent_total": 0}
      

     
          
     return obj_sent

                    

     














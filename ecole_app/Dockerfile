# 1. Image de base Linux avec Python installé
FROM python:3.11-slim 

# 2. On définit le dossier de travail interne au conteneur
WORKDIR /app

# 3. Installation obligatoire du logiciel Nginx
# Justification : L'image 'python' ne contient pas Nginx par défaut.
RUN apt-get update && apt-get install -y nginx

# 4. Copie de TON fichier de bibliothèques
# Justification : On utilise exactement le nom de ton fichier local.
COPY ecole_app/librairie_reqcuises.txt .#here i copy my file librairie at the workplace  who is the root, this workplace exists to put the command like that  
RUN pip install --no-cache-dir -r ecole_app/librairie_reqcuises.txt 

# 5. Copie de tes fichiers de code et de config
# Justification : On met 'cerveau.py' et 'nginx.conf' dans le conteneur.
COPY . .

# On déplace ton fichier de config là où Nginx s'attend à le trouver
RUN mv nginx.conf /etc/nginx/nginx.conf

# 6. Lancement de l'API
# Justification : --host 0.0.0.0 est obligatoire pour que le conteneur soit joignable.
CMD ["uvicorn", "cerveau:app", "--host", "0.0.0.0", "--port", "5000"]

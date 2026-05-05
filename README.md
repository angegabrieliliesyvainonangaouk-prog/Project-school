
Stelyse Lydia
1. Overview

Stelyse Lydia is a school attendance management solution designed to address the specific challenges faced by educational institutions in Gabon.
2. Objectives (Why?)

The primary goal is to provide Gabonese schools that cannot afford expensive subscriptions with a reliable solution to ensure child safety. Given the persistent issue of kidnapping, securing students is an absolute priority. This project aims to minimize operational costs while maximizing protection.
3. Target Audience (For whom?)

The system is primarily intended for primary schools. Unlike secondary school students who might miss classes for social reasons, the absence of a primary school child is, in most cases, a sign of a critical external factor requiring an immediate alert.
4. Physical Constraints and Limitations

The development takes local realities into account:

    National Sovereignty: Data protection within the national territory.

    Technological Inequality: Optimized for low-resource devices (low RAM consumption).

    Energy Instability: Resilience against frequent power outages.

5. Operations and Impact

The system provides concrete solutions to assist both parents and teachers:

    Smart Alerts: SMS notifications are sent only when the "presence cycle" is broken (unforeseen absence) to reduce costs associated with messaging APIs.

    Data Persistence: Form selections are stored in the browser's memory. In the event of a power cut, the teacher can resume the roll call exactly where they left off.

    Ergonomics and Precision: Use of a strict color code (Green for "Present", Red for "Absent/Late") to limit human error.

    Time-based Segmentation: Roll calls are divided by class schedules (Start of class: Present/Late | End of class: Absent/Present).

6. Technical Architecture (Frameworks)

    Backend: Python using SQLAlchemy (ORM) and Pydantic for data validation via request bodies.

    Database: PostgreSQL.

    Frontend: HTML and lightweight JavaScript for asynchronous communication with the backend.

    Deployment: Containerization via Docker (Backend and Frontend bundled together for the MVP).

    Security & Networking: Use of an Nginx reverse proxy.

    Sovereign Approach: In-house security management to prevent the outsourcing of sensitive data outside national borders.




















Stelyse Lydia
1. Présentation

Stelyse Lydia est une solution de gestion de présence scolaire conçue pour répondre aux défis spécifiques des établissements d'enseignement au Gabon.
2. Objectifs (Pourquoi ?)

L'objectif principal est d'offrir aux écoles gabonaises n'ayant pas les moyens de souscrire à des abonnements coûteux une solution fiable pour garantir la sécurité des enfants. Face au problème persistant du kidnapping, la sécurisation des élèves est une priorité absolue. Le projet vise à minimiser les dépenses opérationnelles tout en maximisant la protection.
3. Public cible (Pour qui ?)

Le système est prioritairement destiné aux écoles primaires. Contrairement aux élèves du secondaire qui peuvent s'absenter pour des raisons sociales, l'absence d'un enfant en primaire est, dans la majorité des cas, le signe d'un facteur externe critique nécessitant une alerte immédiate.
4. Contraintes et limites physiques

Le développement prend en compte les réalités locales :

    Souveraineté nationale : Protection des données sur le territoire.

    Inégalités technologiques : Optimisation pour des appareils à ressources limitées (faible consommation de RAM).

    Instabilité énergétique : Résilience face aux coupures d'électricité fréquentes.

5. Fonctionnement et Impact

Le système apporte des solutions concrètes pour aider les parents et les enseignants :

    Alertes intelligentes : Envoi de SMS uniquement en cas de rupture du cycle de présence (absence imprévue) pour réduire les coûts liés aux API d'envoi de messages.

    Persistance des données : Le choix du formulaire est gardé en mémoire dans le navigateur. En cas de coupure de courant, l'enseignant peut reprendre l'appel exactement là où il s'était arrêté.

    Ergonomie et précision : Utilisation d'un code couleur strict (Vert pour "Présent", Rouge pour "Absent/Retard") pour limiter les erreurs humaines.

    Segmentation temporelle : Les appels sont divisés par horaires (Début de cours : Présent/Retard | Fin de cours : Absent/Présent).

6. Architecture Technique (Frameworks)

    Backend : Python avec l'ORM SQLAlchemy et Pydantic pour la validation des données via le corps des requêtes (body).

    Base de données : PostgreSQL.

    Frontend : HTML et JavaScript léger pour la communication asynchrone avec le backend.

    Déploiement : Conteneurisation via Docker (Backend et Frontend regroupés pour le MVP).

    Sécurité et Réseau : Utilisation d'un reverse proxy Nginx.

    Approche Souveraine : Gestion interne de la sécurité pour éviter l'externalisation des données sensibles hors des frontières nationales.

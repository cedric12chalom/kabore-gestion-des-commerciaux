# 🌍 GeoCommerce Pro

**Système de Gestion des Commerciaux avec Géolocalisation GPS en Temps Réel**

[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-red)](https://www.django-rest-framework.org/)
[![Angular](https://img.shields.io/badge/Angular-17-red)](https://angular.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.3-blue)](https://postgis.net/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table des matières

- [Contexte](#contexte)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Déploiement](#déploiement)
- [API Documentation](#api-documentation)
- [Comptes de démonstration](#comptes-de-démonstration)
- [Screenshots](#screenshots)

---

## 🎯 Contexte

**Projet académique** - Licence 2, Institut Universitaire Saint Jean  
**Enseignant** : M. KINKEU Daniel  
**Année académique** : 2025-2026  
**Correction** : Semaine du 08 Juin 2026

GeoCommerce Pro est une application SaaS full-stack permettant aux entreprises de :
- Gérer leur force de vente terrain
- Suivre les positions GPS des commerciaux en temps réel
- Planifier et tracer les visites clients
- Gérer les commandes et opportunités commerciales
- Analyser les performances via des dashboards interactifs

---

## 🏗️ Architecture

```
GeoCommerce Pro/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── users/             # Auth JWT + rôles (Admin/Manager/Commercial)
│   │   ├── commerciaux/       # Gestion commerciaux, zones, produits
│   │   ├── clients/           # Clients avec géocodage PostGIS
│   │   ├── visites/           # Planification, check-in/check-out GPS
│   │   ├── gps/               # Tracking temps réel, WebSocket
│   │   ├── commandes/         # Commandes + pipeline opportunités
│   │   ├── dashboard/         # KPIs + analytics
│   │   └── notifications/     # Alertes + messagerie interne
│   ├── core/                  # Settings, URLs, middleware
│   ├── fixtures/              # Données de démonstration
│   └── requirements.txt
│
├── frontend/                   # Angular 17 SPA
│   ├── src/app/
│   │   ├── auth/              # Login JWT, profil
│   │   ├── dashboard/         # Dashboards manager/commercial
│   │   ├── commerciaux/       # CRUD commerciaux
│   │   ├── clients/           # Gestion clients
│   │   ├── visites/           # Calendrier + CR visite
│   │   ├── gps/               # Carte Leaflet temps réel
│   │   ├── commandes/         # Commandes + opportunités
│   │   ├── rapports/          # Analytics + exports
│   │   └── shared/            # UI components réutilisables
│   └── environments/
│
└── docker-compose.yml          # Stack complet local
```

### Stack Technique

| Couche | Technologie |
|--------|-------------|
| **Backend** | Django 4.2 + Django REST Framework |
| **Auth** | JWT (djangorestframework-simplejwt) |
| **Database** | PostgreSQL 15 + PostGIS |
| **Temps réel** | Django Channels + Redis |
| **Frontend** | Angular 17+ (Standalone Components) |
| **UI** | Angular Material |
| **Carte** | Leaflet.js |
| **Charts** | Chart.js + ng2-charts |
| **Déploiement** | Render (backend) + Vercel (frontend) |

---

## ✨ Fonctionnalités

### 🔐 Authentification & Sécurité
- [x] Login JWT avec refresh token
- [x] Rotation des refresh tokens + blacklist
- [x] 3 rôles : Admin, Manager, Commercial
- [x] Permissions granulaires (filtrage par propriétaire)
- [x] Rate limiting + CORS sécurisé

### 📍 Géolocalisation GPS (Fonctionnalité Centrale)
- [x] Envoi position toutes les 30 secondes
- [x] Carte interactive Leaflet avec marqueurs temps réel
- [x] Historique de parcours + replay
- [x] Calcul distance parcourue + vitesse moyenne
- [x] Zones géographiques (polygones PostGIS)
- [x] Alertes sortie de zone
- [x] Clients proches du commercial
- [x] Mode hors-ligne synchronisable

### 👥 Gestion Commerciaux
- [x] Fiches commerciaux avec photos
- [x] Téléphones multiples (1:N)
- [x] Zones assignées
- [x] Objectifs mensuels/trimestriels
- [x] Statuts : Actif, Congé, Suspendu

### 🏢 Gestion Clients
- [x] Clients géocodés (lat/lng PostGIS)
- [x] Secteurs d'activité + potentiel (A/B/C/D)
- [x] Recherche par nom/ville

### 📅 Visites
- [x] Planification avec calendrier
- [x] Check-in / Check-out GPS
- [x] Compte-rendu de visite
- [x] Signature électronique

### 📦 Commandes & Opportunités
- [x] Saisie commande depuis terrain
- [x] Pipeline commercial (Prospect → Gagné/Perdu)
- [x] Objectifs et quotas

### 📊 Dashboards & Rapports
- [x] Dashboard Manager (KPIs équipe, carte, alertes)
- [x] Dashboard Commercial (agenda, objectifs)
- [x] Graphiques analytiques (Chart.js)
- [x] Export PDF/CSV

### 🔔 Notifications
- [x] Alertes temps réel
- [x] Messagerie interne commercial-manager
- [x] Alertes d'inactivité
---

## 🚀 Installation

### Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ avec PostGIS
- Redis (pour WebSocket)

### Option 1 : Docker (Recommandé)

```bash
# Cloner le projet
git clone https://github.com/votre-username/geocommerce-pro.git
cd geocommerce-pro

# Lancer la stack complète
docker-compose up --build

# Backend : http://localhost:8000
# Frontend : http://localhost:4200
# Admin Django : http://localhost:8000/admin
```

### Option 2 : Installation manuelle

#### Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres PostgreSQL

# Créer la base de données PostgreSQL + PostGIS
createdb geocommerce_pro
psql -d geocommerce_pro -c "CREATE EXTENSION postgis;"

# Migrations + données de démo
python manage.py migrate
python manage.py seed_demo

# Créer un superuser (optionnel)
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

#### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer en mode développement
ng serve

# Build production
ng build --configuration production
```

---

## 🌐 Déploiement

### Backend sur Render.com

1. Créer un compte sur [render.com](https://render.com)
2. Créer un **PostgreSQL** service (avec PostGIS)
3. Créer un **Web Service** avec :
   - Build Command : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command : `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`
4. Configurer les variables d'environnement dans le dashboard Render

### Frontend sur Vercel.com

1. Créer un compte sur [vercel.com](https://vercel.com)
2. Importer le repo GitHub
3. Framework Preset : **Angular**
4. Build Command : `ng build --configuration production`
5. Output Directory : `dist/geocommerce-pro/browser`
6. Ajouter les variables d'environnement pour l'URL API

---

## 📚 API Documentation

### Swagger UI
Une fois le backend lancé :
- **Swagger** : `http://localhost:8000/api/docs/`
- **Redoc** : `http://localhost:8000/api/redoc/`
- **Schema OpenAPI** : `http://localhost:8000/api/schema/`

### Endpoints principaux

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/login/` | Login JWT |
| `POST /api/auth/refresh/` | Refresh token |
| `POST /api/auth/logout/` | Logout (blacklist) |
| `GET /api/v1/commerciaux/` | Liste commerciaux |
| `GET /api/v1/clients/` | Liste clients |
| `GET /api/v1/visites/` | Liste visites |
| `POST /api/v1/visites/{id}/checkin/` | Check-in GPS |
| `POST /api/v1/visites/{id}/checkout/` | Check-out GPS |
| `GET /api/v1/gps/temps-reel/` | Positions temps réel |
| `POST /api/v1/gps/positions/` | Envoyer position |
| `GET /api/v1/commandes/` | Liste commandes |
| `GET /api/v1/dashboard/manager/` | Dashboard manager |
| `GET /api/v1/dashboard/commercial/` | Dashboard commercial |

---

## 👤 Comptes de démonstration

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| **Admin** | admin@geocommerce.pro | admin123 |
| **Manager** | manager@geocommerce.pro | manager123 |
| **Commercial** | commercial@geocommerce.pro | commercial123 |
| **Commercial 2** | commercial2@geocommerce.pro | commercial123 |

---

## 📸 Screenshots

### Page de connexion
![Login](docs/screenshots/login.png)

### Dashboard Manager
![Dashboard](docs/screenshots/dashboard.png)

### Carte GPS Temps Réel
![Carte](docs/screenshots/carte.png)

### Gestion des Commerciaux
![Commerciaux](docs/screenshots/commerciaux.png)

---

## 📝 Notes pour la correction

### Livrables attendus
- [x] Backend déployé sur Render.com
- [x] Frontend déployé sur Vercel.com
- [x] Repository GitHub public avec commits réguliers
- [x] README complet avec instructions
- [x] Comptes de démonstration fournis

### Grille de notation respectée
| Critère | Implémenté |
|---------|-----------|
| Modélisation & API Backend | ✅ |
| Géolocalisation GPS | ✅ |
| Authentification JWT | ✅ |
| Interface Admin Django | ✅ |
| Frontend Angular Structure | ✅ |
| Services HTTP & API | ✅ |
| Formulaires & Validation | ✅ |
| Dashboard & Rapports | ✅ |
| Design & UX | ✅ |
| GitHub & README | ✅ |
| Déploiement production | ✅ |

---

## 👨‍🏫 Enseignant

**M. KINKEU Daniel**  
Institut Universitaire Saint Jean (Saint Jean Ingénieur)  
Cours : Développement Web Angular et Django  
Licence 2 — Année académique 2025-2026

> *"L'école n'est pas un piège — ensemble, luttons contre le travail de la dernière minute."*
> — M. KINKEU Daniel

---

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**🔗 Liens de déploiement**
- **Backend API** : https://geocommerce-pro-backend.onrender.com
- **Frontend App** : https://geocommerce-pro.vercel.app
- **Documentation API** : https://geocommerce-pro-backend.onrender.com/api/docs/

---

*Développé avec ❤️ pour le cours de Développement Web Angular & Django*

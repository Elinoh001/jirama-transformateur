# ⚡ JIRAMA TRANSFORMATEURS

<h3 align="center">🌍 Smart GIS & Preventive Maintenance Platform</h3>

<p align="center">
  <strong>Géolocalisation • Gestion intelligente • Maintenance préventive</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PROJECT-JIRAMA%20TRANSFORMATEURS-123B65?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PYTHON-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/VUE.JS-3-42B883?style=for-the-badge&logo=vuedotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/POSTGRESQL-POSTGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
</p>

<p align="center">
  <em>Une plateforme moderne pour centraliser, géolocaliser et améliorer le suivi des transformateurs de distribution électrique.</em>
</p>

---

## 📑 Sommaire

- [Présentation](#-présentation)
- [Problématique](#-problématique)
- [Objectifs](#-objectifs)
- [Fonctionnalités](#-fonctionnalités)
- [Aperçu de l'architecture](#️-architecture-technique)
- [Technologies](#-technologies)
- [Structure du projet](#-structure-du-projet)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Base de données spatiale](#️-base-de-données-spatiale)
- [Sécurité](#-sécurité)
- [Contexte académique](#-contexte-académique)
- [Perspectives](#-perspectives)

---

## 🌐 Présentation

**JIRAMA Transformateurs** est une application web de gestion et de géolocalisation des transformateurs de distribution électrique.

Développée dans le contexte de la JIRAMA à Antsirabe, cette solution vise à mettre en place un système d'information centralisé permettant de consulter les équipements, suivre leur état et organiser les opérations de maintenance.

La plateforme associe une interface web moderne, une API REST et une base de données spatiale afin de faciliter l'exploitation des informations techniques et géographiques.

<p align="center">
  <img src="https://img.shields.io/badge/GIS-Interactive%20Mapping-1677C8?style=flat-square" />
  <img src="https://img.shields.io/badge/Database-Spatial%20Data-336791?style=flat-square" />
  <img src="https://img.shields.io/badge/Maintenance-Preventive-159B75?style=flat-square" />
</p>

## ❗ Problématique

Le suivi des transformateurs nécessite une bonne connaissance de leur localisation, de leurs caractéristiques techniques, de leur état et de leur historique de maintenance.

La dispersion des informations peut compliquer :

- La localisation rapide des équipements.
- Le suivi de leur état de fonctionnement.
- La planification des inspections.
- Le traitement des incidents.
- L'analyse des relevés de charge.
- La prise de décision concernant les interventions.

**Solution proposée :** une plateforme numérique centralisée qui facilite la gestion du parc de transformateurs grâce aux technologies GIS et aux outils de gestion de données.

## 🎯 Objectifs

| Objectif | Description |
|:---|:---|
| 🌍 Géolocaliser | Visualiser les transformateurs sur une carte interactive |
| 🗄️ Centraliser | Regrouper les informations techniques dans une base unique |
| 🔧 Maintenir | Organiser les inspections et les opérations préventives |
| 🚨 Surveiller | Suivre les anomalies, les pannes et les alertes |
| 📊 Analyser | Exploiter les relevés et les indicateurs disponibles |
| 📄 Décider | Produire des rapports pour faciliter le suivi du parc |

## 🚀 Fonctionnalités

### 🗺️ 01 — GIS & Géolocalisation
- Carte interactive avec Leaflet.
- Localisation des transformateurs.
- Marqueurs selon l'état des équipements.
- Clustering des marqueurs.
- Recherche géographique et par secteur.
- Filtrage spatial avec PostGIS.
- Calcul de distances et recherche par rayon.
- Import et export GeoJSON.

### ⚡ 02 — Gestion des transformateurs
- Enregistrement des équipements.
- Références uniques.
- Caractéristiques techniques.
- Puissance nominale et tensions.
- État et niveau d'huile si renseignés.
- Historique des modifications.
- Recherche multicritère.
- Import et export des données.

### 🔧 03 — Maintenance préventive
- Planification des inspections.
- Gestion des échéances.
- Calendrier de maintenance.
- Affectation des techniciens.
- Suivi des inspections en retard.
- Historique des opérations.
- Rapports de maintenance.

### 🚨 04 — Gestion des pannes
- Déclaration des incidents.
- Niveau de gravité.
- Description et localisation.
- Suivi de résolution.
- Historique des événements.
- Association aux interventions.

### 🛠️ 05 — Gestion des interventions
- Création des ordres de travail.
- Affectation des techniciens.
- Suivi des statuts.
- Gestion des priorités.
- Rapports d'intervention.
- Validation et clôture.

### 📈 06 — Analyse des charges
- Enregistrement des relevés.
- Historique des mesures.
- Calcul du taux de charge.
- Détection des dépassements de seuil.
- Visualisation graphique.
- Comparaison des équipements.

Formule utilisée :

\[
Taux\ de\ charge = \frac{Puissance\ mesurée}{Puissance\ nominale}\times100
\]

Les calculs nécessitent des mesures disponibles et valides.

### 📊 07 — Dashboard & Reporting
- Vue globale du parc.
- Indicateurs dynamiques.
- Répartition par état et secteur.
- Suivi des inspections.
- Statistiques des pannes.
- Graphiques d'évolution.
- Export des rapports.

### 🔐 08 — Administration & Sécurité
- Authentification JWT.
- Gestion des utilisateurs.
- Rôles et permissions.
- Journal des activités.
- Gestion des paramètres.
- Traçabilité des modifications.

---

## 🏗️ Architecture technique

<p align="center">
  <strong>Une architecture Full-Stack organisée en couches.</strong>
</p>

```text
                    👤 UTILISATEUR
                          |
                          ▼
                ┌──────────────────┐
                │   VUE.JS 3       │
                │   FRONTEND       │
                └──────────────────┘
                          |
                     AXIOS / HTTP
                          |
                          ▼
                ┌──────────────────┐
                │   FASTAPI        │
                │   REST API       │
                └──────────────────┘
                          |
             ┌────────────┼────────────┐
             ▼            ▼            ▼
        CONTROLLERS    SERVICES     SECURITY
             |            |            |
             └────────────┼────────────┘
                          |
                          ▼
                ┌──────────────────┐
                │   SQLALCHEMY     │
                │   GEOALCHEMY2    │
                └──────────────────┘
                          |
                          ▼
                ┌──────────────────┐
                │   POSTGRESQL     │
                │   + POSTGIS      │
                └──────────────────┘
```

## 💻 Technologies

### Backend

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge" />
</p>

### Frontend

<p>
  <img src="https://img.shields.io/badge/Vue.js-42B883?style=for-the-badge&logo=vuedotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/Pinia-FFD859?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white" />
</p>

### Base de données

<p>
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/PostGIS-4169E1?style=for-the-badge" />
</p>

### Outils

<p>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white" />
</p>

## 📁 Structure du projet

```text
jirama-transformateur/
│
├── backend/
│   ├── app/
│   │   ├── config/
│   │   ├── controllers/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── router/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.js
│   │
│   ├── package.json
│   └── vite.config.js
│
├── database/
├── docs/
├── .gitignore
└── README.md
```

*Cette structure représente l'organisation cible ; adapte-la aux fichiers réellement présents dans le dépôt.*

## ⚙️ Installation

### Prérequis

- Python 3.12+
- Node.js et npm
- PostgreSQL
- PostGIS
- Git

### 1. Cloner le dépôt

```powershell
git clone https://github.com/Elinoh001/jirama-transformateur.git
cd jirama-transformateur
```

### 2. Configurer le backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Créer le fichier `.env` à partir de `.env.example` et renseigner les paramètres de connexion.

### 3. Configurer PostgreSQL/PostGIS

Créer la base de données :

```sql
CREATE DATABASE jirama_transformateurs;
```

Activer PostGIS dans cette base :

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

Vérifier :

```sql
SELECT PostGIS_Version();
```

### 4. Lancer le backend

```powershell
uvicorn app.main:app --reload
```

API :

`http://127.0.0.1:8000`

Documentation interactive :

`http://127.0.0.1:8000/docs`

### 5. Lancer le frontend

Dans un nouveau terminal :

```powershell
cd frontend
npm install
npm run dev
```

Ouvrir l'adresse locale affichée par Vite.

## 🛰️ Base de données spatiale

Le projet utilise PostGIS pour le stockage et l'exploitation des données géographiques.

| Technologie | Utilisation |
|---|---|
| PostgreSQL | Stockage relationnel |
| PostGIS | Gestion des données spatiales |
| GeoAlchemy2 | Intégration spatiale avec SQLAlchemy |
| Shapely | Manipulation des géométries |
| GiST | Indexation spatiale |
| Leaflet | Visualisation cartographique |

Opérations spatiales envisagées :

- `ST_DWithin`
- `ST_Distance`
- `ST_Intersects`
- `ST_Within`
- `ST_ClusterDBSCAN`

## 🔒 Sécurité

La plateforme prévoit :

- Authentification par JWT.
- Mots de passe hachés.
- Gestion des rôles.
- Protection des routes.
- Validation des entrées.
- Variables d'environnement pour les secrets.
- Journalisation des actions importantes.

## 🎓 Contexte académique

| Élément | Information |
|---|---|
| Niveau | Licence 3 |
| Domaine | Génie logiciel et base de données |
| Projet | JIRAMA Transformateurs |
| Zone d'étude | Antsirabe, Madagascar |
| Type | Application web GIS |
| Base de données | PostgreSQL + PostGIS |

Ce projet met en application les connaissances en conception logicielle, architecture Full-Stack, bases de données relationnelles et spatiales, développement d'API et visualisation géographique.

## 🔮 Perspectives d'évolution

- Extension à d'autres zones géographiques.
- Automatisation des programmes de maintenance.
- Analyses spatiales avancées.
- Notifications par email.
- Amélioration des rapports décisionnels.
- Intégration de nouvelles sources de données techniques.

---

<p align="center">
  <strong>⚡ JIRAMA TRANSFORMATEURS</strong>
  <br/>
  <em>La donnée au service d'une meilleure gestion des équipements électriques.</em>
  <br/><br/>
  <a href="https://github.com/Elinoh001/jirama-transformateur">Voir le dépôt GitHub</a>
</p>

<p align="center">
  <sub>Projet académique — Licence 3 — Génie logiciel et base de données</sub>
</p>
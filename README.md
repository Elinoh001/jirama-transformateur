<div align="center">

# ⚡ JIRAMA Transformers

### Plateforme de gestion & de suivi préventif des transformateurs

<p>
  <strong>Projet de stage — Licence 3 | Génie Logiciel & Base de Données</strong>
</p>

<p>
  <img src="https://img.shields.io/badge/Vue.js-3-42b883?style=for-the-badge&logo=vue.js&logoColor=white" alt="Vue.js">
  <img src="https://img.shields.io/badge/FastAPI-Python-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-PostGIS-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Leaflet-Maps-199900?style=for-the-badge&logo=leaflet&logoColor=white" alt="Leaflet">
</p>

<p>
  <img src="https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Version-0.1.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/License-Academic-lightgrey?style=flat-square" alt="License">
</p>

<br>

> 🏗️ Une application web destinée à centraliser, cartographier et assurer le suivi préventif des transformateurs de distribution de la JIRAMA.

</div>

---

## 📖 À propos

**JIRAMA Transformers** est une plateforme web conçue dans le cadre d'un projet de stage et de soutenance de **Licence 3 en Génie Logiciel et Base de Données**.

L'application a pour objectif de centraliser les informations relatives aux transformateurs de distribution et de faciliter leur **suivi technique et préventif**.

Elle combine une **gestion structurée des données**, une **cartographie interactive** et un système de **priorisation préventive** afin d'aider à identifier les équipements nécessitant une attention particulière.

---

## ✨ Fonctionnalités

<table>
<tr>
<td width="50%">

### 🏭 Gestion des transformateurs

* ➕ Ajouter un transformateur
* ✏️ Modifier ses informations
* 🔎 Rechercher et consulter
* 📋 Consulter sa fiche technique
* 🟢 Suivre son état

</td>
<td width="50%">

### 🗺️ Cartographie

* 📍 Localisation des transformateurs
* 🧭 Carte interactive
* 🔎 Recherche géographique
* 🏭 Sélection d'un équipement
* 📌 Consultation depuis la carte

</td>
</tr>

<tr>
<td width="50%">

### 🔧 Maintenance

* 🔍 Gestion des inspections
* 🛠️ Gestion des interventions
* 📅 Historique de maintenance
* 📝 Observations techniques
* 👷 Suivi des opérations

</td>
<td width="50%">

### ⚠️ Suivi préventif

* 📊 Analyse de plusieurs critères
* ⏱️ Suivi de l'ancienneté
* 🔍 Suivi des inspections
* 🛠️ Prise en compte des interventions
* 🚨 Identification des équipements prioritaires

</td>
</tr>
</table>

---

## 🎯 Objectif

> **Concevoir et développer une plateforme web permettant de centraliser les données des transformateurs de distribution de la JIRAMA, de gérer leur maintenance et d'assurer leur suivi préventif grâce à une interface cartographique.**

### Objectifs spécifiques

```text
        CENTRALISER
             │
             ▼
      Données techniques
             │
             ▼
        LOCALISER
             │
             ▼
     Carte interactive
             │
             ▼
         SURVEILLER
             │
             ▼
      Inspections & état
             │
             ▼
         PRÉVENIR
             │
             ▼
    Priorité de maintenance
```

---

## 🧠 Suivi préventif

Le système attribue une **priorité de suivi** aux transformateurs à partir de règles simples et explicables.

### Critères pris en compte

| Critère           | Exemple                        |
| ----------------- | ------------------------------ |
| 📅 Ancienneté     | Date d'installation            |
| 🔍 Inspection     | Date de la dernière inspection |
| 🛠️ Interventions | Nombre d'interventions         |
| ⚙️ État           | État actuel du transformateur  |
| 📜 Historique     | Historique de maintenance      |

### Niveau de priorité

<div align="center">

|        Niveau       | Signification                          |
| :-----------------: | -------------------------------------- |
|    🟢 **NORMAL**    | Aucun problème particulier             |
| 🟠 **À SURVEILLER** | Inspection recommandée                 |
|  🔴 **PRIORITAIRE** | Intervention ou inspection à planifier |

</div>

> ℹ️ Le projet utilise actuellement un **système de règles de priorité**. Il ne prétend pas effectuer une prédiction basée sur l'intelligence artificielle.

---

## 🗺️ Cartographie

La plateforme intègre une carte interactive permettant de visualiser les transformateurs selon leur position géographique.

```text
                    🗺️ CARTE
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
   📍 Normal       🟠 À surveiller   🔴 Prioritaire
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
               📋 Fiche technique
```

Technologies utilisées :

**Leaflet + OpenStreetMap + PostGIS**

---

## 🏗️ Architecture

```text
┌──────────────────────────────────────────────────┐
│                  👤 UTILISATEUR                  │
└────────────────────────┬─────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│                  🖥️ FRONTEND                    │
│                                                  │
│                  Vue.js 3 + Vite                 │
│                                                  │
│ Dashboard │ Transformateurs │ Carte │ Maintenance│
└────────────────────────┬─────────────────────────┘
                         │
                      REST API
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│                  ⚙️ BACKEND                     │
│                                                  │
│                  FastAPI / Python                │
│                                                  │
│ API │ Logique métier │ Auth │ Suivi préventif   │
└────────────────────────┬─────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│                  🗄️ DATABASE                    │
│                                                  │
│               PostgreSQL + PostGIS               │
│                                                  │
│ Transformateurs │ Inspections │ Interventions   │
│ Historique      │ Données géographiques         │
└──────────────────────────────────────────────────┘
```

---

## 🛠️ Stack technologique

<div align="center">

| Domaine          | Technologie                 |
| :--------------- | :-------------------------- |
| 🎨 Frontend      | **Vue.js 3 + Vite**         |
| ⚙️ Backend       | **Python + FastAPI**        |
| 🗄️ Database     | **PostgreSQL**              |
| 🌍 Spatial       | **PostGIS**                 |
| 🗺️ Cartographie | **Leaflet + OpenStreetMap** |
| 🔌 API           | **REST API**                |
| 📐 Conception    | **UML / PlantUML**          |
| 🔧 Versionnement | **Git + GitHub**            |
| 💻 IDE           | **Visual Studio Code**      |

</div>

---

## 🗃️ Modèle de données

Les principales entités du système sont :

```text
┌─────────────────────┐
│   TRANSFORMATEUR    │
├─────────────────────┤
│ id                  │
│ reference           │
│ puissance           │
│ etat                │
│ date_installation   │
│ latitude            │
│ longitude           │
└──────────┬──────────┘
           │
       ┌───┴───────────────┐
       │                   │
       ▼                   ▼
┌───────────────┐   ┌────────────────┐
│  INSPECTION   │   │  INTERVENTION  │
├───────────────┤   ├────────────────┤
│ id            │   │ id             │
│ date          │   │ date           │
│ type          │   │ description    │
│ observation   │   │ cout           │
│ etat          │   │ statut         │
│ technicien    │   │                │
└───────────────┘   └────────────────┘
```

---

## 📂 Structure du projet

```text
jirama-transformers/
│
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 models/
│   │   ├── 📁 schemas/
│   │   ├── 📁 routes/
│   │   ├── 📁 services/
│   │   ├── 📁 database/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   ├── 📁 views/
│   │   ├── 📁 services/
│   │   ├── 📁 router/
│   │   └── 📁 assets/
│   │
│   ├── package.json
│   └── vite.config.js
│
├── 📁 database/
│   ├── schema.sql
│   └── seed.sql
│
├── 📁 docs/
│   ├── 📁 uml/
│   └── 📁 documentation/
│
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/Elinoh001/jirama-transformers.git
cd jirama-transformers
```

### 2. Configurer PostgreSQL

Créer la base de données :

```sql
CREATE DATABASE jirama_db;
```

Puis activer PostGIS :

```sql
CREATE EXTENSION postgis;
```

### 3. Backend

```bash
cd backend

python -m venv venv
```

Sous Windows :

```bash
venv\Scripts\activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer l'API :

```bash
uvicorn app.main:app --reload
```

### 4. Frontend

Dans un autre terminal :

```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Variables d'environnement

Créer un fichier `.env` dans `backend/` :

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/jirama_db
```

⚠️ **Ne jamais envoyer `.env` sur GitHub.**

Utiliser `.env.example` pour partager uniquement la structure de configuration.

---

## 📅 Roadmap — 2 mois

```text
Semaine 01  ██████████  Analyse + besoins + UML
Semaine 02  ██████████  Base de données + architecture
Semaine 03  ██████████  Backend + API + CRUD
Semaine 04  ██████████  Frontend + gestion des transformateurs
Semaine 05  ██████████  Cartographie interactive
Semaine 06  ██████████  Inspections + interventions
Semaine 07  ██████████  Suivi préventif + dashboard
Semaine 08  ██████████  Tests + documentation + soutenance
```

---

## 🧪 Tests

Le projet sera testé progressivement sur :

* ✅ API REST
* ✅ opérations CRUD
* ✅ connexion PostgreSQL
* ✅ données géographiques
* ✅ calcul de priorité
* ✅ cartographie
* ✅ interface utilisateur
* ✅ intégration frontend/backend

---

## 📈 Évolution possible

Les fonctionnalités suivantes pourront être envisagées ultérieurement :

* 🔐 Gestion avancée des utilisateurs et rôles
* 📧 Notifications automatiques
* 📱 Interface responsive améliorée
* 📊 Rapports de maintenance
* 📤 Export PDF / Excel
* 🤖 Analyse prédictive basée sur des données historiques réelles

---

## 🎓 Contexte académique

**Projet de stage — Licence 3**

**Parcours :** Génie Logiciel et Base de Données (GB)

**Thème :** Plateforme de gestion et de suivi préventif des transformateurs JIRAMA

**Lieu :** JIRAMA Antsirabe

---

## 👨‍💻 Auteur

<div align="center">

### Valery Elinoh

**L3 — Génie Logiciel & Base de Données**

Projet académique réalisé dans le cadre d'un stage et d'une soutenance.

<br>

⭐ **Si ce projet vous intéresse, n'hésitez pas à explorer le dépôt.**

</div>

---

<div align="center">

**⚡ JIRAMA Transformers**

*Centraliser • Localiser • Surveiller • Prévenir*

</div>

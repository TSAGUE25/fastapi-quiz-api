# Quiz API — FastAPI

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-pytest-green?logo=pytest)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> API REST de génération de quiz pédagogiques — Examen Datascientest  
> **Auteur :** Emmanuel TSAGUE — Data Scientist / Data Analyst, EDF MAD EDVANCE

---

## Description

API construite avec **FastAPI** pour générer des quiz à partir d'une base de questions CSV.  
Elle expose 3 endpoints protégés par authentification HTTP Basic :

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/verify` | GET | Aucune | Vérifie que l'API est en ligne |
| `/generate_quiz` | POST | Utilisateur | Génère un quiz filtré par type et catégorie |
| `/create_question` | POST | Admin | Ajoute une question dans la base |

---

## Démarrage rapide

```bash
# Cloner le dépôt
git clone https://github.com/TSAGUE25/fastapi-quiz-api.git
cd fastapi-quiz-api

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Installer les dépendances
pip install -r requirements.txt

# (Optionnel) Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos propres mots de passe

# Lancer l'API
uvicorn main:app --reload
```

L'API est disponible sur `http://127.0.0.1:8000`  
Documentation interactive Swagger : `http://127.0.0.1:8000/docs`

---

## Utilisation

### Vérifier que l'API fonctionne

```bash
curl http://127.0.0.1:8000/verify
# {"status":"ok","message":"L'API Quiz est fonctionnelle."}
```

### Générer un quiz (authentification utilisateur)

```bash
curl -X POST http://127.0.0.1:8000/generate_quiz \
  -u alice:wonderland \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "Test de positionnement",
    "categories": ["BDD", "Docker"],
    "number_of_questions": 5
  }'
```

**Utilisateurs disponibles :**

| Username | Password |
|----------|----------|
| alice | wonderland |
| bob | builder |
| clementine | mandarine |

### Ajouter une question (authentification admin)

```bash
curl -X POST http://127.0.0.1:8000/create_question \
  -u admin:4dm1N \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qu'\''est-ce que FastAPI ?",
    "subject": "Automation",
    "correct": "A",
    "use": "Test de validation",
    "responseA": "Un framework Python pour créer des APIs REST",
    "responseB": "Un système de gestion de bases de données",
    "responseC": "Un outil de visualisation",
    "responseD": ""
  }'
```

---

## Structure du projet

```
fastapi-quiz-api/
├── main.py              # Application FastAPI (endpoints + auth + logique)
├── questions.csv        # Base de questions (79 questions, 6 catégories)
├── tests/
│   └── test_main.py    # 11 tests unitaires (pytest)
├── requirements.txt     # Dépendances Python
├── .env.example         # Template variables d'environnement
├── .gitignore
└── README.md
```

---

## Tests

```bash
pytest tests/ -v
```

**11 tests couverts :**
- `/verify` : statut OK
- `/generate_quiz` : 401 sans auth, 401 mauvais mdp, 200 avec auth valide, 404 catégorie inconnue, 422 number=0
- `/create_question` : 403 si utilisateur, 201 si admin, 401 sans auth, 422 champ manquant

---

## Catégories de questions disponibles

| Catégorie (`subject`) | Types de test (`use`) |
|-----------------------|-----------------------|
| BDD | Test de positionnement |
| Systèmes distribués | Test de positionnement, Test de validation |
| Streaming de données | Test de positionnement, Test de validation |
| Docker | Test de positionnement, Test de validation |
| Classification | Test de validation |
| Machine Learning | Total Bootcamp |
| Data Science | Total Bootcamp |
| Automation | Test de validation |

---

## Corrections apportées vs version examen

| Problème | Correction |
|----------|------------|
| Admin credentials hardcodés | Variables d'environnement (`QUIZ_ADMIN_USERNAME`, `QUIZ_ADMIN_PASSWORD`) |
| Double authentification incohérente | Séparation `verify_user` / `verify_admin` (deux fonctions distinctes) |
| Admin absent de `users_db` | Admin authentifié via `verify_admin` (indépendant de `users_db`) |
| `secrets.compare_digest` absent | Comparaison timing-safe avec `secrets.compare_digest` |
| Aucune validation de `number_of_questions` | `Field(ge=1, le=20)` dans le modèle Pydantic |
| Aucun test | 11 tests `pytest` avec `TestClient` |
| `requests.txt` vide | Exemples `curl` dans le README |

---

## Auteur

**Emmanuel TSAGUE** — Data Scientist / Data Analyst  
EDF MAD EDVANCE | Formation Datascientest 2024  
GitHub : [TSAGUE25](https://github.com/TSAGUE25)

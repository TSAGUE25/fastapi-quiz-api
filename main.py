# -*- coding: utf-8 -*-
"""
Quiz API — FastAPI
==================
API REST pour la génération de quiz pédagogiques et la gestion des questions.

Endpoints :
  GET  /verify           : vérifie que l'API est en ligne
  POST /generate_quiz    : génère un quiz filtré (authentification utilisateur)
  POST /create_question  : ajoute une question (authentification admin)
"""

import csv
import os
import random
import secrets
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration — variables d'environnement avec valeurs par défaut pour dev
# ---------------------------------------------------------------------------

# En production : définir ces variables dans un fichier .env ou les secrets CI/CD
ADMIN_USERNAME = os.getenv("QUIZ_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("QUIZ_ADMIN_PASSWORD", "4dm1N")

# Base de données fictive des utilisateurs (mots de passe hachés en production)
USERS_DB: dict[str, str] = {
    "alice":      os.getenv("USER_ALICE_PASSWORD",      "wonderland"),
    "bob":        os.getenv("USER_BOB_PASSWORD",        "builder"),
    "clementine": os.getenv("USER_CLEMENTINE_PASSWORD", "mandarine"),
}

CSV_PATH = os.path.join(os.path.dirname(__file__), "questions.csv")

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Quiz API",
    description="API de génération de quiz pédagogiques — Datascientest",
    version="1.0.0",
)

security = HTTPBasic()


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------

def verify_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Vérifie les identifiants utilisateur (HTTPBasic). Retourne le username."""
    stored_password = USERS_DB.get(credentials.username)
    password_ok = stored_password is not None and secrets.compare_digest(
        credentials.password.encode("utf-8"),
        stored_password.encode("utf-8"),
    )
    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Vérifie les identifiants admin (HTTPBasic). Retourne le username admin."""
    username_ok = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        ADMIN_USERNAME.encode("utf-8"),
    )
    password_ok = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        ADMIN_PASSWORD.encode("utf-8"),
    )
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin refusé.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ---------------------------------------------------------------------------
# Chargement des questions
# ---------------------------------------------------------------------------

def load_questions() -> list[dict]:
    """Charge les questions depuis le fichier CSV (appelé à chaque requête pertinente)."""
    questions = []
    with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            questions.append(row)
    return questions


# ---------------------------------------------------------------------------
# Modèles Pydantic
# ---------------------------------------------------------------------------

class QuizRequest(BaseModel):
    test_type: str = Field(..., description="Type de test (ex: 'Test de validation')")
    categories: List[str] = Field(..., min_length=1, description="Liste des matières")
    number_of_questions: int = Field(..., ge=1, le=20, description="Nombre de questions (1-20)")


class QuestionModel(BaseModel):
    question: str = Field(..., min_length=5)
    subject: str = Field(..., min_length=2)
    correct: str = Field(..., description="Lettre(s) de la bonne réponse (ex: 'A' ou 'A,B')")
    use: str = Field(..., description="Type de test")
    responseA: str
    responseB: str
    responseC: str = ""
    responseD: str = ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/verify", summary="Vérifier que l'API est en ligne")
def verify():
    """Endpoint de santé — retourne un message si l'API répond."""
    return {"status": "ok", "message": "L'API Quiz est fonctionnelle."}


@app.post(
    "/generate_quiz",
    summary="Générer un quiz",
    description="Retourne N questions filtrées par type de test et catégorie(s). Nécessite une authentification utilisateur.",
)
def generate_quiz(
    quiz_request: QuizRequest,
    username: str = Depends(verify_user),
):
    """Génère un quiz personnalisé. Authentification : alice/bob/clementine."""
    questions = load_questions()

    filtered = [
        q for q in questions
        if q.get("use") == quiz_request.test_type
        and q.get("subject") in quiz_request.categories
    ]

    if not filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune question trouvée pour use='{quiz_request.test_type}' "
                   f"et categories={quiz_request.categories}.",
        )

    random.shuffle(filtered)
    return {
        "user": username,
        "total_available": len(filtered),
        "returned": min(quiz_request.number_of_questions, len(filtered)),
        "questions": filtered[: quiz_request.number_of_questions],
    }


@app.post(
    "/create_question",
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une question (admin)",
    description="Ajoute une nouvelle question dans la base CSV. Nécessite l'authentification admin.",
)
def create_question(
    question: QuestionModel,
    admin: str = Depends(verify_admin),
):
    """Ajoute une question. Authentification : credentials admin (HTTPBasic)."""
    questions = load_questions()

    new_row = question.model_dump()

    # Écriture dans le CSV (append)
    with open(CSV_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=questions[0].keys())
        # N'écrire que les champs du CSV existant (ignorer les extras)
        filtered_row = {k: new_row.get(k, "") for k in questions[0].keys()}
        writer.writerow(filtered_row)

    return {
        "status": "created",
        "message": "Question ajoutée avec succès.",
        "question": question.question,
    }

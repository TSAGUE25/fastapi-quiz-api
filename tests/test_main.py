# -*- coding: utf-8 -*-
"""
Tests unitaires — Quiz API
===========================
Teste les 3 endpoints : /verify, /generate_quiz, /create_question
"""

import pytest
from fastapi.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# /verify
# ---------------------------------------------------------------------------

def test_verify_returns_ok():
    response = client.get("/verify")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# /generate_quiz — authentification
# ---------------------------------------------------------------------------

def test_generate_quiz_no_auth_returns_401():
    response = client.post("/generate_quiz", json={
        "test_type": "Test de positionnement",
        "categories": ["BDD"],
        "number_of_questions": 3
    })
    assert response.status_code == 401


def test_generate_quiz_wrong_credentials_returns_401():
    response = client.post(
        "/generate_quiz",
        json={"test_type": "Test de positionnement", "categories": ["BDD"], "number_of_questions": 3},
        auth=("alice", "mauvais_mdp"),
    )
    assert response.status_code == 401


def test_generate_quiz_valid_user_returns_questions():
    response = client.post(
        "/generate_quiz",
        json={"test_type": "Test de positionnement", "categories": ["BDD"], "number_of_questions": 3},
        auth=("alice", "wonderland"),
    )
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) <= 3


def test_generate_quiz_unknown_category_returns_404():
    response = client.post(
        "/generate_quiz",
        json={"test_type": "Test de positionnement", "categories": ["INEXISTANT"], "number_of_questions": 3},
        auth=("bob", "builder"),
    )
    assert response.status_code == 404


def test_generate_quiz_number_too_large_is_capped():
    """L'API retourne min(n_demandées, n_disponibles) — pas d'erreur."""
    response = client.post(
        "/generate_quiz",
        json={"test_type": "Test de positionnement", "categories": ["BDD"], "number_of_questions": 20},
        auth=("alice", "wonderland"),
    )
    assert response.status_code == 200


def test_generate_quiz_number_zero_returns_422():
    """number_of_questions=0 est rejeté par la validation Pydantic (ge=1)."""
    response = client.post(
        "/generate_quiz",
        json={"test_type": "Test de positionnement", "categories": ["BDD"], "number_of_questions": 0},
        auth=("alice", "wonderland"),
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# /create_question — authentification admin
# ---------------------------------------------------------------------------

VALID_QUESTION = {
    "question": "Qu'est-ce que FastAPI ?",
    "subject": "Automation",
    "correct": "A",
    "use": "Test de validation",
    "responseA": "Un framework Python pour créer des APIs REST",
    "responseB": "Un système de gestion de bases de données",
    "responseC": "Un outil de visualisation",
    "responseD": "",
}


def test_create_question_as_user_returns_403():
    """Un utilisateur normal ne peut pas créer de question."""
    response = client.post(
        "/create_question",
        json=VALID_QUESTION,
        auth=("alice", "wonderland"),
    )
    assert response.status_code == 403


def test_create_question_admin_valid_returns_201():
    response = client.post(
        "/create_question",
        json=VALID_QUESTION,
        auth=("admin", "4dm1N"),
    )
    assert response.status_code == 201
    assert response.json()["status"] == "created"


def test_create_question_no_auth_returns_401():
    response = client.post("/create_question", json=VALID_QUESTION)
    assert response.status_code == 401


def test_create_question_missing_field_returns_422():
    incomplete = {k: v for k, v in VALID_QUESTION.items() if k != "question"}
    response = client.post(
        "/create_question",
        json=incomplete,
        auth=("admin", "4dm1N"),
    )
    assert response.status_code == 422

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_problem_crud(client):
    payload = {
        "title": "A + B Problem",
        "difficulty": "easy",
        "description": "Read two integers and output their sum.",
        "input_description": "Two integers.",
        "output_description": "Their sum.",
        "constraints": "Integers fit in 32-bit signed range.",
        "sample_input": "1 2\n",
        "sample_output": "3\n",
        "tags": ["basic", "math"],
        "test_cases": [
            {"input_data": "1 2\n", "expected_output": "3\n", "is_sample": True, "sort_order": 1},
            {"input_data": "-5 8\n", "expected_output": "3\n", "is_sample": False, "sort_order": 2},
        ],
    }
    created = client.post("/api/v1/problems", json=payload)
    assert created.status_code == 201
    problem = created.json()
    assert problem["title"] == payload["title"]
    assert len(problem["test_cases"]) == 2

    listed = client.get("/api/v1/problems?tag=math")
    assert listed.status_code == 200
    assert listed.json()["meta"]["total"] == 1

    detail = client.get(f"/api/v1/problems/{problem['id']}")
    assert detail.status_code == 200
    assert detail.json()["tags"][0]["name"] in {"basic", "math"}


def test_submission_requires_existing_problem(client):
    response = client.post(
        "/api/v1/submissions",
        json={"problem_id": 999, "language": "python", "code": "print(1)"},
    )
    assert response.status_code == 404

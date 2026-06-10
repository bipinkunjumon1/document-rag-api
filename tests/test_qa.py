def test_qa_requires_api_key(client):
    resp = client.post("/api/v1/qa/ask", json={"question": "hi"})
    assert resp.status_code == 401


def test_qa_no_documents_returns_idk(client, api_headers):
    resp = client.post(
        "/api/v1/qa/ask",
        headers=api_headers,
        json={"question": "What is GitLab?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["question"] == "What is GitLab?"
    assert "don't know" in body["answer"].lower()
    assert body["sources"] == []


def test_qa_with_documents_returns_mock_answer(client, api_headers):
    text = (
        "GitLab is a DevSecOps platform. "
        "It includes CI/CD pipelines and security scanners. "
    ) * 5
    upload = client.post(
        "/api/v1/documents/upload",
        headers=api_headers,
        files={"file": ("doc.txt", text.encode("utf-8"), "text/plain")},
    )
    assert upload.status_code == 200

    resp = client.post(
        "/api/v1/qa/ask",
        headers=api_headers,
        json={"question": "What is GitLab?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"].startswith("MOCK_ANSWER")
    assert len(body["sources"]) >= 1


def test_qa_validation_error_on_empty_question(client, api_headers):
    resp = client.post(
        "/api/v1/qa/ask", headers=api_headers, json={"question": ""}
    )
    assert resp.status_code == 422

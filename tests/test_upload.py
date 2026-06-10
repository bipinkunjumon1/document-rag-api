def test_upload_requires_api_key(client):
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("a.txt", b"hello world", "text/plain")},
    )
    assert resp.status_code == 401


def test_upload_txt_success(client, api_headers):
    content = (
        "GitLab is a complete DevSecOps platform. "
        "It provides CI/CD, source control, and security scanning. "
    ) * 10
    resp = client.post(
        "/api/v1/documents/upload",
        headers=api_headers,
        files={"file": ("notes.txt", content.encode("utf-8"), "text/plain")},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["filename"] == "notes.txt"
    assert body["chunks_created"] >= 1
    assert "document_id" in body


def test_upload_rejects_unsupported_extension(client, api_headers):
    resp = client.post(
        "/api/v1/documents/upload",
        headers=api_headers,
        files={"file": ("a.docx", b"data", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert resp.json()["success"] is False


def test_list_documents(client, api_headers):
    client.post(
        "/api/v1/documents/upload",
        headers=api_headers,
        files={"file": ("a.txt", b"one two three four five six seven", "text/plain")},
    )
    resp = client.get("/api/v1/documents", headers=api_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["filename"] == "a.txt"

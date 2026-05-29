"""
Tests CA-01 a CA-05 de US-001 (webhook WhatsApp).
"""

VALID_PAYLOAD = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "id": "wamid.test123",
                                "from": "521234567890",
                                "type": "text",
                                "text": {"body": "Hola Koach"},
                            }
                        ]
                    }
                }
            ]
        }
    ]
}


# CA-01: GET con token correcto retorna el challenge
def test_verify_webhook_valid_token(client):
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test_token",
            "hub.challenge": "abc123",
        },
    )
    assert response.status_code == 200
    assert response.text == "abc123"


# CA-02: GET con token incorrecto retorna 403
def test_verify_webhook_invalid_token(client):
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "abc123",
        },
    )
    assert response.status_code == 403


# CA-03: POST retorna 200 con payload válido
def test_receive_message_returns_200(client):
    response = client.post("/webhook", json=VALID_PAYLOAD)
    assert response.status_code == 200


# CA-04: POST con mensaje de voz no falla y retorna 200
def test_receive_non_text_message_returns_200(client):
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.audio1",
                                    "from": "521234567890",
                                    "type": "audio",
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200


# CA-05: Payload malformado no rompe el servidor
def test_malformed_payload_returns_200(client):
    response = client.post("/webhook", json={"unexpected": "payload"})
    assert response.status_code == 200


def test_completely_invalid_json_body(client):
    response = client.post(
        "/webhook",
        content=b"esto no es json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200

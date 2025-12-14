def test_create_vehicle(mock_post) -> None:
    vehicle = {"id": 1, "user_id": 1, "license_plate": "ABC123", "name": "My Car"}
    response = client.post("/vehicles", headers=valid_header, json=vehicle)
    assert response.status_code == 200
    assert vehicles_db[1]["name"] == "My Car"
    vehicles_db.clear()

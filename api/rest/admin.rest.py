### GET USER DETAILS (7.1)
GET http://127.0.0.1:8000/admin/users/1
Authorization: Bearer YOUR_ADMIN_TOKEN_HERE

###

### CREATE RESERVATION FOR USER (7.3)
POST http://127.0.0.1:8000/admin/reservations
Content-Type: application/json
Authorization: Bearer YOUR_ADMIN_TOKEN_HERE

{
  "user_id": 1,
  "vehicle_id": 2,
  "parking_lot_id": 3,
  "start_time": "2025-01-01T10:00:00",
  "end_time": "2025-01-01T12:00:00"
}

###

### DELETE RESERVATION (7.4)
DELETE http://127.0.0.1:8000/admin/reservations/1
Authorization: Bearer YOUR_ADMIN_TOKEN_HERE

###

### DELETE USER (1.6)
DELETE http://127.0.0.1:8000/admin/users/1
Authorization: Bearer YOUR_ADMIN_TOKEN_HERE

###

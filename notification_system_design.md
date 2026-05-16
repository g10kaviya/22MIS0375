STAGE 1

Core Actions
The notification platform should support the following core actions:

Create Notification — Admin/HR creates a new notification (Placement, Result, or Event)
Fetch Notifications — Students retrieve their notifications (with pagination)
Mark as Read — Student marks a specific notification as read
Mark All as Read — Student marks all their notifications as read
Get Unread Count — Student fetches count of unread notifications
Delete Notification — Admin removes a notification

REST API Endpoints
1. Create Notification
POST /api/notifications

Request Headers:
json{
  "Authorization": "Bearer <token>",
  "Content-Type": "application/json"
}

Request Body:
json{
  "title": "TCS Placement Drive",
  "message": "TCS is visiting campus on 25th May for recruitment.",
  "notificationType": "Placement",
  "targetStudentIds": ["student_101", "student_102"],
  "targetAll": false
}

FieldTypeRequiredDescriptiontitlestringYesNotification titlemessagestringYesNotification bodynotificationTypeenumYesOne of: Placement, Result, EventtargetStudentIdsstring[]NoSpecific students to notify. Ignored if targetAll is truetargetAllbooleanNoIf true, notify all registered students

Response (201 Created):
json{
  "success": true,
  "data": {
    "notificationId": "d146095a-0d86-4a34-9e69-3900a14576bc",
    "title": "TCS Placement Drive",
    "message": "TCS is visiting campus on 25th May for recruitment.",
    "notificationType": "Placement",
    "createdAt": "2026-05-16T10:30:00Z"
  }
}

Error Response (400 Bad Request):
json{
  "success": false,
  "error": "notificationType must be one of: Placement, Result, Event"
}

3. Get Notifications for a Student
GET /api/students/{studentId}/notifications?page=1&limit=20&type=Placement&isRead=false
Query Parameters:
ParameterTypeDefaultDescriptionpageinteger1Page numberlimitinteger20Items per pagetypestring(all)Filter by notification typeisReadboolean(all)Filter by read status
Response (200 OK):
json{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "d146095a-0d86-4a34-9e69-3900a14576bc",
        "title": "TCS Placement Drive",
        "message": "TCS is visiting campus on 25th May for recruitment.",
        "notificationType": "Placement",
        "isRead": false,
        "createdAt": "2026-05-16T10:30:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalItems": 98,
      "limit": 20
    }
  }
}

4. Mark Notification as Read
PATCH /api/students/{studentId}/notifications/{notificationId}/read
Response (200 OK):
json{
  "success": true,
  "data": {
    "id": "d146095a-0d86-4a34-9e69-3900a14576bc",
    "isRead": true,
    "readAt": "2026-05-16T11:00:00Z"
  }
}

5. Mark All Notifications as Read
PATCH /api/students/{studentId}/notifications/read-all
Response (200 OK):
json{
  "success": true,
  "data": {
    "updatedCount": 15
  }
}

6. Get Unread Notification Count
GET /api/students/{studentId}/notifications/unread-count
Response (200 OK):
json{
  "success": true,
  "data": {
    "unreadCount": 7
  }
}

7. Delete Notification (Admin)
DELETE /api/notifications/{notificationId}
Response (200 OK):
json{
  "success": true,
  "data": {
    "deleted": true
  }
}

Real-Time Notification Mechanism
WebSockets 
When a student is logged in and has the app open, they should receive new notifications instantly without refreshing the page. WebSockets provide a persistent, bidirectional connection between the client and server.

How it works:
When a student logs in, the client opens a WebSocket connection and joins a room identified by their studentId.
When an admin creates a new notification, the server pushes the notification to each targeted student's room via WebSocket.
If targetAll is true, the server broadcasts to all connected clients.
If a student is offline (not connected), the notification is still saved in the DB. They will see it when they next fetch notifications via the REST API.

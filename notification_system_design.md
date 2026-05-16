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
    "notificationId": "d1",
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

2. Get Notifications for a Student

Response (200 OK):
json{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "d1",
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

3. Mark Notification as Read
PATCH /api/students/{studentId}/notifications/{notificationId}/read
Response (200 OK):
json{
  "success": true,
  "data": {
    "id": "d1",
    "isRead": true,
    "readAt": "2026-05-16T11:00:00Z"
  }
}

4. Mark All Notifications as Read
PATCH /api/students/{studentId}/notifications/read-all
Response (200 OK):
json{
  "success": true,
  "data": {
    "updatedCount": 15
  }
}

5. Get Unread Notification Count
GET /api/students/{studentId}/notifications/unread-count
Response (200 OK):
json{
  "success": true,
  "data": {
    "unreadCount": 7
  }
}

6. Delete Notification (Admin)
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


STAGE 2

PostgreSQL:

Notifications have a well-defined, consistent structure (id, type, message, timestamp, read status) — a relational model fits naturally.
We need complex queries: filtering by student, type, read status, date ranges, and ordering by recency. SQL handles this efficiently.
ACID compliance ensures that when a notification is created and sent to 50,000 students, either all records are committed or none are (transactional consistency).
PostgreSQL supports indexing, partitioning, and JSONB for any future semi-structured data needs.

Database Schema
sqlCREATE TABLE students (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE notification_type AS ENUM ('Placement', 'Result', 'Event');

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    notification_type notification_type NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE student_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id VARCHAR(50) NOT NULL REFERENCES students(id),
    notification_id UUID NOT NULL REFERENCES notifications(id),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, notification_id)
);

Scaling
As data volume increases (50,000 students × thousands of notifications):

The student_notifications table will grow into hundreds of millions of rows. Solution: Use table partitioning by created_at (e.g., monthly partitions). Old partitions can be archived or dropped.
Frequent unread count queries will strain the DB. Solution: Maintain a cached unread_count per student in Redis. Increment on new notification, decrement on mark-as-read.
"Notify All" creates 50,000 rows at once. Solution: Use batch inserts (insert 1,000 rows per batch) and process asynchronously via a message queue.

SQL Queries for REST APIs

1. Create Notification:

INSERT INTO notifications (title, message, notification_type)
VALUES ('TCS Placement Drive', 'TCS is visiting campus...', 'Placement')
RETURNING id;

INSERT INTO student_notifications (student_id, notification_id)
SELECT s.id, 'd1'
FROM students s
WHERE s.id IN ('student_101', 'student_102');

2. Get Notifications for a Student:
sqlSELECT n.id, n.title, n.message, n.notification_type, 
       sn.is_read, sn.created_at
FROM student_notifications sn
JOIN notifications n ON n.id = sn.notification_id
WHERE sn.student_id = 'student_101'
ORDER BY sn.created_at DESC
LIMIT 20 OFFSET 0;

3. Mark as Read:
sqlUPDATE student_notifications
SET is_read = TRUE, read_at = NOW()
WHERE student_id = 'student_101' 
  AND notification_id = 'd1';

4. Mark All as Read:
sqlUPDATE student_notifications
SET is_read = TRUE, read_at = NOW()
WHERE student_id = 'student_101' AND is_read = FALSE;

5. Get Unread Count:
sqlSELECT COUNT(*) AS unread_count
FROM student_notifications
WHERE student_id = 'student_101' AND is_read = FALSE;

6. Delete Notification:
sqlDELETE FROM student_notifications WHERE notification_id = 'd1';
DELETE FROM notifications WHERE id = 'd1';


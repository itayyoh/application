// Auth as admin user
db.auth('mongodb_admin', 'admin_password_123')

// Switch to application database
db = db.getSiblingDB('urlshortener')

// Create application user
db.createUser({
    user: 'url_shortener_user',
    pwd: 'app_password_123',
    roles: [
        {
            role: "readWrite",
            db: "urlshortener"
        }
    ]
})

// Create indexes
db.urls.createIndex({ "_id": 1 }, { unique: true })
db.urls.createIndex({ "created_at": 1 })
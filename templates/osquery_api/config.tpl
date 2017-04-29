{
  "options": {
    "host_identifier": "{{hostname}}",
    "schedule_splay_percent": 10
  },
  "schedule": {
    "test_users": {
      "query": "SELECT * FROM USERS LIMIT 2;",
      "interval": 30
    }
  }
}

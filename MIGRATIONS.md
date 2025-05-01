# Database Migrations

## Local Development
```bash
# Create a new migration
flask db migrate -m "description of changes"

# Apply migrations
flask db upgrade
```

## Production (Render)
```bash
# Run migrations manually
render run --service nearwise flask db upgrade
```

## Best Practices
1. Always backup your database before running migrations
2. Test migrations locally before running in production
3. Run migrations during low-traffic periods
4. Monitor the application after migrations
5. Have a rollback plan ready

## Current Schema
- Users table: id, email, password_hash, created_date
- Location table: id, name, address, user_id 
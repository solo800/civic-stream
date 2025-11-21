# User Authentication & Subscriptions - Development Plan

## Overview
Add user authentication and city subscription management to enable deployment and user testing of the civic engagement app.

## Tech Stack
- **Backend**: Flask + SQLAlchemy
- **Database**: AWS RDS PostgreSQL (db.t4g.micro ~$15-20/month)
- **Auth**: JWT tokens (Flask-JWT-Extended)
- **Hosting**: AWS Lambda + API Gateway (serverless)
- **Email**: AWS SES ($0.10/1000 emails)
- **Secrets**: AWS Secrets Manager

## Database Schema

### Users
- id, email, hashed_password (bcrypt), created_at, verified_at

### Cities
- id, name, legistar_api_url, api_key_required, active

### User_Subscriptions
- user_id, city_id, notification_preferences, created_at

### Future Tables
- meetings, agenda_items, stakeholders (Phase 7)

## API Endpoints

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get current user (protected)

### Subscriptions
- `GET /cities` - List available cities
- `POST /subscriptions` - Subscribe to city (protected)
- `GET /subscriptions` - Get user's subscriptions (protected)
- `DELETE /subscriptions/{city_id}` - Unsubscribe (protected)

## Development Phases

### Phase 1-4: Local Development (Week 1-2)
1. Design database schema
2. Set up Flask app with SQLAlchemy + Alembic (local PostgreSQL)
3. Build authentication endpoints
4. Build subscription endpoints
5. Seed cities table (Seattle, NYC, SF)

### Phase 5-6: AWS Deployment (Week 3)
6. Create RDS PostgreSQL instance
7. Configure VPC, security groups, Secrets Manager
8. Deploy Flask to Lambda (AWS Lambda Web Adapter or Zappa)
9. Set up API Gateway HTTP API
10. Run migrations against RDS

### Phase 7: Scraper Integration (Week 4)
11. Deploy scrapers as scheduled Lambda functions (EventBridge)
12. Create tables for scraped data
13. Link meetings to cities for notifications

### Phase 8: Frontend (Week 5)
14. Simple static site (S3 + CloudFront) or skip for API-only POC
15. Share API documentation with testers

## AWS Cost Estimate
- RDS db.t4g.micro: ~$15-20/month
- Lambda: Free tier (1M requests/month)
- API Gateway: $1/million requests
- NAT Gateway: $32/month (or use public RDS for POC)
- **Total: ~$20-50/month**

## Key Decisions

### Cost Optimization
- Use RDS public access for POC (avoid NAT Gateway cost)
- Restrict security group to known IPs
- Free tier eligible: db.t3.micro (750 hours/month for 12 months)

### Connection Pooling
- Configure SQLAlchemy with low pool_size for Lambda
- Consider RDS Proxy ($15/month) if connection issues arise

### Cold Starts
- Accept 1-3 second Lambda cold starts for POC
- Can add CloudWatch warming pings if needed

## Tools & Libraries
- Flask, Flask-JWT-Extended, Flask-RESTX
- SQLAlchemy, Alembic (migrations)
- psycopg2-binary (PostgreSQL driver)
- python-dotenv (local config)
- boto3 (AWS SDK)
- AWS SAM / Serverless Framework / Zappa (deployment)

## Deferred Features
- Email verification
- Password reset
- Rate limiting
- OAuth/social login
- Advanced notification preferences
- Mobile app

## Next Steps
1. Design detailed database schema with foreign keys and indexes
2. Initialize Flask project structure
3. Set up local PostgreSQL and create initial migration
4. Build and test auth endpoints locally
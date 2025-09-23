# AI Educational Platform Deployment Guide

This guide provides step-by-step instructions for deploying the AI-powered educational mobile app to Google Cloud Run with all integrations.

## Prerequisites

- Google Cloud Platform account with billing enabled
- Firebase project
- GitHub repository
- Docker installed locally
- Terraform installed
- Flutter SDK for mobile app development

## 1. Environment Setup

### 1.1 Google Cloud Configuration

1. Create a new Google Cloud Project:
   ```bash
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   ```

2. Enable required APIs:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

3. Create a service account for deployment:
   ```bash
   gcloud iam service-accounts create github-actions \
       --description="Service account for GitHub Actions deployment" \
       --display-name="GitHub Actions"
   ```

4. Grant necessary permissions:
   ```bash
   gcloud projects add-iam-policy-binding your-project-id \
       --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
       --role="roles/cloudtranslate.user"
   gcloud projects add-iam-policy-binding your-project-id \
       --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
       --role="roles/containerregistry.ServiceAgent"
   gcloud projects add-iam-policy-binding your-project-id \
       --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
       --role="roles/storage.admin"
   ```

### 1.2 Firebase Setup

1. Create a new Firebase project or use existing one
2. Enable Authentication with Email/Password
3. Set up Firestore Database
4. Download service account key and save as `firebase-credentials.json`

### 1.3 Third-Party Services

1. **Judge0 API**: Get API key from https://judge0.com
2. **Twilio**: Set up account and get SID, Auth Token, Phone Number
3. **SendGrid**: Set up account and get API key
4. **Blockchain API**: Choose a provider and get API credentials

## 2. Local Development Setup

### 2.1 Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```bash
   python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
   ```

5. Start the backend:
   ```bash
   uvicorn main:app --reload
   ```

### 2.2 Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install Flutter dependencies:
   ```bash
   flutter pub get
   ```

3. Configure Firebase:
   ```bash
   flutterfire configure
   ```

4. Run the app:
   ```bash
   flutter run
   ```

### 2.3 Docker Setup

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 3. Infrastructure Deployment

### 3.1 Terraform Configuration

1. Navigate to infrastructure directory:
   ```bash
   cd infrastructure/terraform
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Review and modify variables in `terraform.tfvars`:
   ```hcl
   project_id = "your-project-id"
   region = "us-central1"
   firebase_project_id = "your-firebase-project"
   ```

4. Deploy infrastructure:
   ```bash
   terraform plan
   terraform apply
   ```

### 3.2 Cloud Run Deployment

1. Build and push Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/ai-edu-backend
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy ai-edu-backend \
       --image gcr.io/your-project-id/ai-edu-backend \
       --platform managed \
       --allow-unauthenticated \
       --region us-central1 \
       --set-env-vars DATABASE_URL=$DATABASE_URL,FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
   ```

## 4. CI/CD Pipeline

### 4.1 GitHub Actions Setup

1. Create repository secrets:
   - `GCP_SA_KEY`: Service account key JSON
   - `FIREBASE_CREDENTIALS`: Firebase credentials JSON
   - `JUDGE0_API_KEY`: Judge0 API key
   - `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_PHONE`
   - `SENDGRID_API_KEY`
   - `BLOCKCHAIN_API_KEY`

2. The CI/CD pipeline will automatically:
   - Run tests on pull requests
   - Build and deploy on main branch pushes
   - Run security scans

## 5. Monitoring and Logging

### 5.1 Application Monitoring

1. Enable Cloud Monitoring:
   ```bash
   gcloud monitoring dashboards create --config-from-file=dashboard.json
   ```

2. Set up alerts for:
   - High error rates
   - Slow response times
   - Database connection issues

### 5.2 Logging

1. Configure structured logging in the application
2. Set up log-based metrics in Cloud Logging
3. Create log sinks for long-term storage

## 6. Security Implementation

### 6.1 Authentication & Authorization

- Firebase Authentication for user management
- JWT tokens for API access
- Role-based access control (RBAC)

### 6.2 Data Protection

- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement rate limiting and DDoS protection

### 6.3 Compliance

- Regular security audits
- Dependency vulnerability scanning
- GDPR compliance for user data

## 7. Scaling Strategies

### 7.1 Auto-scaling

1. Configure Cloud Run concurrency:
   ```bash
   gcloud run services update ai-edu-backend \
       --max-instances 100 \
       --concurrency 80 \
       --cpu 2 \
       --memory 4Gi
   ```

2. Database optimization:
   - Connection pooling
   - Query optimization
   - Read replicas for high traffic

### 7.2 Performance Optimization

1. Implement caching with Redis
2. Use CDN for static assets
3. Optimize images and videos
4. Database indexing strategy

## 8. Testing and Validation

### 8.1 Load Testing

1. Use Locust for load testing:
   ```bash
   locust -f load_test.py --host https://your-app-url
   ```

2. Monitor performance metrics during tests

### 8.2 Integration Testing

1. Run automated tests:
   ```bash
   pytest tests/
   ```

2. Test all third-party integrations

## 9. Production Deployment Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Firebase rules set up
- [ ] SSL certificates installed
- [ ] Monitoring and alerts configured
- [ ] Backup procedures in place
- [ ] Security headers implemented
- [ ] Load testing completed
- [ ] Documentation updated

## 10. Troubleshooting

### Common Issues

1. **Database Connection Errors**: Check DATABASE_URL and firewall rules
2. **Firebase Authentication**: Verify credentials and project settings
3. **Cloud Run Deployment**: Check build logs and resource limits
4. **Third-party API Limits**: Monitor usage and implement retry logic

### Support

For issues, check:
- Cloud Run logs: `gcloud logs read`
- Firebase console
- GitHub Actions logs
- Application health endpoint: `/health`

## 11. Maintenance

### Regular Tasks

1. **Weekly**: Review logs and performance metrics
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Load testing and capacity planning
4. **Annually**: Security audit and architecture review

### Backup Strategy

1. Database backups: Automated daily backups
2. Configuration backups: Version control
3. Log retention: 30 days in Cloud Logging

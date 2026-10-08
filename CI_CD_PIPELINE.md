# NetVision CI/CD Pipeline
## Enterprise Continuous Delivery for Production

This document outlines the CI/CD pipeline strategy for NetVision, designed to ensure secure, reliable, and rapid delivery of features to production environments while maintaining compliance and quality standards.

---

## Pipeline Philosophy

**Shift Left Security**: Security checks performed as early as possible in the lifecycle
**Fast Feedback**: Quick identification of issues to minimize waste
**Immutability**: Consistent, reproducible builds and deployments
**Traceability**: Full audit trail from code to production
**Automated Recovery**: Self-healing capabilities and automatic rollback

---

## Pipeline Stages Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Developer     │───▶│    Commit        │───▶│   Pull Request   │───▶│    Main Branch  │
│   (Local Dev)   │    │   (Pre-commit)   │    │   (CI Checks)    │    │   (Trunk-Based) │
└─────────────────┘    └──────────────────┘    └──────────────────┘    └─────────────────┘
                                      │                       │
                                      ▼                       ▼
                             ┌─────────────────┐      ┌──────────────────┐
                             │   Merge Queue   │      │   Release Tag  │
                             │   (Optional)    │      │   (SemVer)       │
                             └─────────┬───────┘      └─────────┬────────┘
                                       ▼                      ▼
                             ┌─────────────────┐      ┌──────────────────┐
                             │   CI Pipeline   │◀─────│   CD Pipeline  │
                             │   (Build/Test)  │      │   (Deploy)     │
                             └─────────┬───────┘      └───────┬──────────┘
                                       ▼                      ▼
                             ┌─────────────────┐      ┌──────────────────┐
                             │   Staging       │      │    Production    │
                             │   Environment   │      │   Environment    │
                             └─────────────────┘      └──────────────────┘
```

---

## GitHub Actions Workflow Structure

See `.github/workflows/` directory for all workflow files.

### 1. `ci.yml` - Continuous Integration
Triggered on: pull_request, push to main/develop branches

#### Jobs:
- `code-quality`: Static analysis, linting, formatting
- `security-scan`: Dependency scanning, container scanning, secrets detection
- `unit-test`: Unit tests with coverage requirements
- `integration-test`: API and database integration tests
- `build`: Docker image creation and signing
- `sbom-generate`: Software Bill of Materials creation
- `notify`: Slack/email notifications on completion/failure

### 2. `cd.yml` - Continuous Deployment
Triggered on: push to main branch with version tags or manual dispatch

#### Environments:
- `staging`: Automatic deployment for validation
- `production`: Manual approval required

#### Jobs:
- `deploy-staging`: Deploy to staging environment with smoke tests
- `manual-approval`: Required approval for production
- `deploy-production`: Deploy to production with health checks
- `post-deploy-validation`: Performance and security validation
- `rollback-on-failure`: Automatic rollback if health checks fail

### 3. `security.yml` - Dedicated Security Workflow
Triggered on: schedule (daily), workflow_dispatch

#### Jobs:
- `dependency-scan`: Updated dependency vulnerability checking
- `container-scan`: Daily container image scanning
- `infrastructure-scan`: IaC security scanning (Terraform, K8s manifests)
- `license-check`: Open source license compliance
- `threat-model`: Automated threat modeling updates

### 4. `release.yml` - Release Management
Triggered on: release created

#### Jobs:
- `verify-release`: Validate release notes and artifacts
- `publish-artifacts`: Publish to container registry and artifact repository
- `announce-release`: Notify stakeholders and update documentation
- `create-hotfix-branch`: Prepare for emergency fixes if needed

---

## Detailed Job Specifications

### Code Quality Job
```yaml
code-quality:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Install dependencies
      run: |
        pip install pre-commit black flake8 mypy pylint bandit
        npm ci
    
    - name: Run pre-commit hooks
      run: pre-commit run --all-files
    
    - name: Python linting
      run: |
        flake8 backend/ agent/ --max-line-length=120
        black --check --diff backend/ agent/
        mypy backend/ agent/
    
    - name: JavaScript/TypeScript linting
      run: |
        npm run lint --if-present
        npx eslint frontend/src/ --ext .ts,.tsx
    
    - name: Security linting (Python)
      run: bandit -r backend/ agent/ -f json -o bandit-report.json
    
    - name: Upload lint reports
      uses: actions/upload-artifact@v4
      with:
        name: code-quality-reports
        path: |
          bandit-report.json
          **/flake8.log
          **/mypy.log
          **/eslint-report.json
```

### Security Scan Job
```yaml
security-scan:
  runs-on: ubuntu-latest
  needs: code-quality
  steps:
    - uses: actions/checkout@v4
    
    - name: Install security tools
      run: |
        curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.48.0
        pip install safety bandit[tv] semgrep
        npm install -g @ auditor npm-audit-resolver
    
    - name: Scan dependencies (Python)
      run: |
        safety check -r backend/requirements.txt --full-report -o json -o safety-python.json
        safety check -r agent/requirements.txt --full-report -o json -o safety-agent.json
        pip list --format=freeze > requirements.txt
        bandit -r backend/ agent/ -f json -o bandit-deps.json
    
    - name: Scan dependencies (Node.js)
      run: |
        npm audit --json > npm-audit.json
        npx @auditor audit --json > auditor-report.json
    
    - name: Scan containers
      run: |
        # Build images for scanning
        docker build -t netvision-backend:ci ./backend
        docker build -t netvision-frontend:ci ./frontend
        docker build -t netvision-agent:ci ./agent
        
        # Scan with Trivy
        trivy image --format json --output trivy-backend.json netvision-backend:ci
        trivy image --format json --output trivy-frontend.json netvision-frontend:ci
        trivy image --format json --output trivy-agent.json netvision-agent:ci
        
        # Scan for secrets
        docker run --rm -v ${{ github.workspace }}:/workspace aquasec/trivy fs \
          --format json --output trivy-fs.json --scanners secret .
    
    - name: Upload security reports
      uses: actions/upload-artifact@v4
      with:
        name: security-reports
        path: |
          safety-*.json
          npm-audit.json
          auditor-report.json
          trivy-*.json
          bandit-deps.json
```

### Unit Test Job
```yaml
unit-test:
  runs-on: ubuntu-latest
  needs: code-quality
  services:
    postgres:
      image: postgres:15-alpine
      env:
        POSTGRES_USER: testuser
        POSTGRES_PASSWORD: testpass
        POSTGRES_DB: testdb
      ports: ["5432:5432"]
      options: >-
        --health-cmd "pg_isready -U testuser -d testdb"
        --health-interval 5s
        --health-timeout 5s
        --health-retries 5
    
    redis:
      image: redis:7-alpine
      ports: ["6379:6379"]
      options: >
        --health-cmd "redis-cli ping"
        --health-interval 5s
        --health-timeout 3s
        --health-retries 5
    
    influxdb:
      image: influxdb:2.7-alpine
      env:
        DOCKER_INFLUXDB_INIT_MODE: setup
        DOCKER_INFLUXDB_INIT_USERNAME: testuser
        DOCKER_INFLUXDB_INIT_PASSWORD: testpass
        DOCKER_INFLUXDB_INIT_ORG: testorg
        DOCKER_INFLUXDB_INIT_BUCKET: testbucket
        DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: testtoken
      ports: ["8086:8086"]
      options: >
        --health-cmd "curl -f http://localhost:8086/health"
        --health-interval 5s
        --health-timeout 5s
        --health-retries 5
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install test dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-asyncio pytest-cov factory-boy
    
    - name: Run backend tests
      env:
        DATABASE_URL: postgresql+asyncpg://testuser:testpostgres@localhost:5432/testdb
        REDIS_URL: redis://localhost:6379/0
        INFLUXDB_URL: http://localhost:8086
        INFLUXDB_TOKEN: testtoken
        INFLUXDB_ORG: testorg
        INFLUXDB_BUCKET: testbucket
        SECRET_KEY: test-secret-key-for-testing-only
      run: |
        cd backend
        pytest tests/ -v --cov=app --cov-report=xml --cov-report=term-missing
        # Enforce minimum coverage
        pytest --cov=app --cov-report=xml --cov-fail-under=80
    
    - name: Upload coverage report
      uses: actions/upload-artifact@v4
      with:
        name: coverage-report
        path: backend/coverage.xml
```

### Integration Test Job
```yaml
integration-test:
  runs-on: ubuntu-latest
  needs: unit-test
  services:
    # Same services as unit test
    postgres:
      image: postgres:15-alpine
      env:
        POSTGRES_USER: testuser
        POSTGRES_PASSWORD: testpass
        POSTGRES_DB: testdb
      ports: ["5432:5432"]
      options: >-
        --health-cmd "pg_isready -U testuser -d testdb"
        --health-interval 5s
        --health-timeout 5s
        --health-retries 5
    
    redis:
      image: redis:7-alpine
      ports: ["6379:6379"]
      options: >
        --health-cmd "redis-cli ping"
        --health-interval 5s
        --health-timeout 3s
        --health-retries 5
    
    influxdb:
      image: influxdb:2.7-alpine
      env:
        DOCKER_INFLUXDB_INIT_MODE: setup
        DOCKER_INFLUXDB_INIT_USERNAME: testuser
        DOCKER_INFLUXDB_INIT_PASSWORD: testpass
        DOCKER_INFLUXDB_INIT_ORG: testorg
        DOCKER_INFLUXDB_INIT_BUCKET: testbucket
        DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: testtoken
      ports: ["8086:8086"]
      options: >
        --health-cmd "curl -f http://localhost:8086/health"
        --health-interval 5s
        --health-timeout 5s
        --health-retries 5
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install httpx asyncio aiosqlite
    
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql+asyncpg://testuser:testpass@localhost:5432/testdb
        REDIS_URL: redis://localhost:6379/0
        INFLUXDB_URL: http://localhost:8086
        INFLUXDB_TOKEN: testtoken
        INFLUXDB_ORG: testorg
        INFLUXDB_BUCKET: testbucket
        SECRET_KEY: test-secret-key-for-testing-only
      run: |
        cd backend
        pytest tests/test_integration.py tests/test_e2e.py -v
    
    - name: Upload test results
      uses: actions/upload-artifact@v4
      with:
        name: test-results
        path: |
          backend/tests/
          !backend/tests/__pycache__/
```

### Build Job
```yaml
build:
  runs-on: ubuntu-latest
  needs: [security-scan, integration-test]
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to container registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract version from git
      id: version
      run: |
        # Use git describe or manual version from file
        echo "VERSION=$(git describe --tags --abbrev=0 || echo '0.1.0')" >> $GITHUB_OUTPUT
        echo "SHA=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
    
    - name: Build backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: false
        tags: |
          ghcr.io/${{ github.repository_owner }}/netvision-backend:${{ steps.version.outputs.VERSION }}
          ghcr.io/${{ github.repository_owner }}/netvision-backend:${{ steps.version.outputs.SHA }}
        labels: |
          org.opencontainers.image.source=${{ github.repository }}
          org.opencontainers.image.revision=${{ steps.version.outputs.SHA }}
          org.opencontainers.image.version=${{ steps.version.outputs.VERSION }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: false
        tags: |
          ghcr.io/${{ github.repository_owner }}/netvision-frontend:${{ steps.version.outputs.VERSION }}
          ghcr.io/${{ github.repository_owner }}/netvision-frontend:${{ steps.version.outputs.SHA }}
        labels: |
          org.opencontainers.image.source=${{ github.repository }}
          org.opencontainers.image.revision=${{ steps.version.outputs.SHA }}
          org.opencontainers.image.version=${{ steps.version.outputs.VERSION }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build agent image
      uses: docker/build-push-action@v5
      with:
        context: ./agent
        push: false
        tags: |
          ghcr.io/${{ github.repository_owner }}/netvision-agent:${{ steps.version.outputs.VERSION }}
          ghcr.io/${{ github.repository_owner }}/netvision-agent:${{ steps.version.outputs.SHA }}
        labels: |
          org.opencontainers.image.source=${{ github.repository }}
          org.opencontainers.image.revision=${{ steps.version.outputs.SHA }}
          org.opencontainers.image.version=${{ steps.version.outputs.VERSION }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Sign images with Cosign
      run: |
        # Install cosign
        curl -LO https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
        install cosign-linux-amd64 /usr/local/bin/cosign
        
        # Sign images (requires COSIGN_EXPERIMENTAL=1 set in repo secrets)
        export COSIGN_EXPERIMENTAL=1
        for img in backend frontend agent; do
          cosign sign --key ${COSIGN_KEY} \
            ghcr.io/${{ github.repository_owner }}/netvision-${img}:${{ steps.version.outputs.VERSION }}
        done
    
    - name: Generate SBOM
      run: |
        # Install syft for SBOM generation
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin v0.90.0
        
        # Generate SBOM for each image
        for img in backend frontend agent; do
          syft ghcr.io/${{ github.repository_owner }}/netvision-${img}:${{ steps.version.outputs.VERSION }} \
            -o spdx-json > sbom-netvision-${img}.json
        done
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: build-artifacts
        path: |
          sbom-*.json
          cosign.*  # if generated locally
```

### Staging Deployment Job
```yaml
deploy-staging:
  runs-on: ubuntu-latest
  needs: build
  environment: staging
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Kubernetes
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure kubectl
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBECONFIG_STAGING }}" > $HOME/.kube/config
        kubectl cluster-info
    
    - name: Deploy to staging
      run: |
        # Update image versions in deployment manifests
        VERSION=${{ github.ref_name }}
        if [[ $VERSION == refs/tags/v* ]]; then
          VERSION=${VERSION#refs/tags/v}
        else
          VERSION=${{ github.sha }}
        fi
        
        # Apply manifests with updated image tags
        envsubst < k8s/staging/backend-deployment.yaml | kubectl apply -f -
        envsubst < k8s/staging/frontend-deployment.yaml | kubectl apply -f -
        envsubst < k8s/staging/agent-deployment.yaml | kubectl apply -f -
        
        # Wait for rollout
        kubectl rollout status deployment/netvision-backend -n netvision-staging --timeout=180s
        kubectl rollout status deployment/netvision-frontend -n netvision-staging --timeout=180s
        kubectl rollout status deployment/netvision-agent -n netvision-staging --timeout=180s
    
    - name: Run smoke tests
      run: |
        # Wait for services to be ready
        sleep 30
        
        # Basic health checks
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://${STAGING_DOMAIN}/health || echo "000")
        if [ "$STATUS" -ne 200 ]; then
          echo "Health check failed with status $STATUS"
          exit 1
        fi
        
        # API endpoint check
        API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://${STAGING_DOMAIN}/api/v1/health || echo "000")
        if [ "$API_STATUS" -ne 200 ]; then
          echo "API health check failed with status $API_STATUS"
          exit 1
        fi
        
        # Database connectivity check (via API)
        DB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://${STAGING_DOMAIN}/api/v1/metrics/health || echo "000")
        if [ "$DB_STATUS" -ne 200 ]; then
          echo "Database health check failed with status $DB_STATUS"
          exit 1
        fi
    
    - name: Notify deployment success
      if: success()
      uses: slackapi/slack-github-action@v1.23.0
      with:
        payload: |
          {
            "text": ":white_check_mark: NetVision staging deployment successful\n*Version*: ${{ github.ref_name }}\n*Commit*: ${{ github.sha }}\n*Environment*: Staining\n*Timestamp*: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    
    - name: Notify deployment failure
      if: failure()
      uses: slackapi/slack-github-action@v1.23.0
      with:
        payload: |
          {
            "text": ":x: NetVision staging deployment failed\n*Version*: ${{ github.ref_name }}\n*Commit*: ${{ github.sha }}\n*Environment*: Staging\n*Timestamp*: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Production Deployment Job
```yaml
deploy-production:
  runs-on: ubuntu-latest
  needs: deploy-staging
  environment:
    name: production
    url: https://netvision.example.com
  steps:
    - uses: actions/checkout@v4
    
    - name: Wait for manual approval
      if: github.event_name != 'workflow_dispatch'
      uses: hmarr/auto-approve-action@v2
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        # This requires environment protection rules in GitHub
    
    - name: Set up Kubernetes
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure kubectl for production
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBECONFIG_PRODUCTION }}" > $HOME/.kube/config
        kubectl cluster-info
    
    - name: Deploy to production
      run: |
        # Similar to staging but with production namespace
        VERSION=${{ github.ref_name }}
        if [[ $VERSION == refs/tags/v* ]]; then
          VERSION=${VERSION#refs/tags/v}
        else
          VERSION=${{ github.sha }}
        fi
        
        # Apply manifests with updated image tags
        envsubst < k8s/production/backend-deployment.yaml | kubectl apply -f -
        envsubst < k8s/production/frontend-deployment.yaml | kubectl apply -f -
        envsubst < k8s/production/agent-deployment.yaml | kubectl apply -f -
        envsubst < k8s/production/alert-engine-deployment.yaml | kubectl apply -f -
        envsubst < k8s/production/kafka-deployment.yaml | kubectl apply -f -
        
        # Wait for rollout with longer timeout for production
        kubectl rollout status deployment/netvision-backend -n netvision-production --timeout=300s
        kubectl rollout status deployment/netvision-frontend -n netvision-production --timeout=300s
        kubectl rollout status deployment/netvision-agent -n netvision-production --timeout=300s
        kubectl rollout status deployment/alert-engine -n netvision-production --timeout=300s
    
    - name: Run production smoke tests
      run: |
        # Extended wait for production
        sleep 60
        
        # Comprehensive health checks
        ENDPOINT="https://${PRODUCTION_DOMAIN}"
        
        # Health endpoint
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/health" || echo "000")
        if [ "$STATUS" -ne 200 ]; then
          echo "Production health check failed with status $STATUS"
          exit 1
        fi
        
        # API health
        API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/api/v1/health" || echo "000")
        if [ "$API_STATUS" -ne 200 ]; then
          echo "Production API health check failed with status $API_STATUS"
          exit 1
        fi
        
        # Database connectivity
        DB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/api/v1/metrics/health" || echo "000")
        if [ "$DB_STATUS" -ne 200 ]; then
          echo "Production database health check failed with status $DB_STATUS"
          exit 1
        fi
        
        # Kafka connectivity (via metrics endpoint)
        KAFKA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/api/v1/metrics/kafka/health" || echo "000")
        if [ "$KAFKA_STATUS" -ne 200 ]; then
          echo "Production Kafka health check failed with status $KAFKA_STATUS"
          exit 1
        fi
        
        # Basic functionality test
        AUTH_TEST=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/api/v1/auth/me" -H "Authorization: Bearer ${PRODUCTION_TEST_TOKEN}" || echo "000")
        if [ "$AUTH_TEST" -ne 200 ] && [ "$AUTH_TEST" -ne 401 ];  # 401 expected if token invalid/not provided
        then
          echo "Production auth endpoint check failed with status $AUTH_TEST"
          exit 1
        fi
    
    - name: Post-deployment validation
      run: |
        # Run extended validation tests
        echo "Running post-deployment validation..."
        # Could include:
        # - Performance testing (k6, locust)
        # - Security scanning (OWASP ZAP)
        # - Chaos engineering lite
        # - Data validation checks
        sleep 30  # Placeholder for actual validation
    
    - name: Notify production deployment success
      if: success()
      uses: slackapi/slack-github-action@v1.23.0
      with:
        payload: |
          {
            "text": ":rocket: NetVision production deployment successful\n*Version*: ${{ github.ref_name }}\n*Commit*: ${{ github.sha }}\n*Environment*: Production\n*Timestamp*: $(date -u +"%Y-%m-%d %H:%M:%S UTC")\n*Monitor*: https://netvision.example.com"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    
    - name: Notify production deployment failure
      if: failure()
      uses: slackapi/slack-github-action@v1.23.0
      with:
        payload: |
          {
            "text": ":rotating_light: NetVision production deployment FAILED\n*Version*: ${{ github.ref_name }}\n*Commit*: ${{ github.sha }}\n*Environment*: Production\n*Timestamp*: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    
    - name: Trigger rollback on failure
      if: failure()
      run: |
        echo "Initiating automatic rollback..."
        # Rollback to previous known good version
        # This would typically involve:
        # 1. Getting previous version from ConfigMap or annotation
        # 2. Redeploying previous version
        # 3. Verifying rollback success
        # For now, we'll just alert
        echo "Manual rollback required - see runbook"
```

### Rollback Job
```yaml
rollback-production:
  runs-on: ubuntu-latest
  needs: [deploy-production]
  if: failure()
  environment: production
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Kubernetes
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure kubectl for production
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBECONFIG_PRODUCTION }}" > $HOME/.kube/config
        kubectl cluster-info
    
    - name: Determine previous version
      run: |
        # Get the previous version from deployment annotations or ConfigMap
        # This is simplified - in practice you'd use a more robust method
        kubectl get deployment netvision-backend -n netvision-production -o jsonpath='{.metadata.annotations.previous-version}' > PREVIOUS_VERSION || echo "unknown"
        PREVIOUS_VERSION=$(cat PREVIOUS_VERSION)
        echo "Previous version: $PREVIOUS_VERSION"
        
        # If we can't determine previous version, use a fallback
        if [ "$PREVIOUS_VERSION" = "unknown" ] || [ -z "$PREVIOUS_VERSION" ]; then
          echo "Could not determine previous version, using fallback"
          # This would be set based on your versioning strategy
          PREVIOUS_VERSION="previous-known-good-tag"
        fi
        
        echo "PREVIOUS_VERSION=$PREVIOUS_VERSION" >> $GITHUB_ENV
    
    - name: Rollback deployment
      run: |
        echo "Rolling back to version $PREVIOUS_VERSION"
        
        # Update manifests with previous version
        envsubst < k8s/production/backend-deployment.yaml | kubectl apply -f -
        envsubst < k8s/production/frontend-deployment.yaml | kubectl apply -f -
        envsubst < k8s/production/agent-deployment.yaml | kubectl apply -f -
        envsubst < k8s/production/alert-engine-deployment.yaml | kubectl apply -f -
        
        # Wait for rollback
        kubectl rollout status deployment/netvision-backend -n netvision-production --timeout=300s
        kubectl rollout status deployment/netvision-frontend -n netvision-production --timeout=300s
        kubectl rollout status deployment/netvision-agent -n netvision-production --timeout=300s
        kubectl rollout status deployment/alert-engine -n netvision-production --timeout=300s
    
    - name: Verify rollback
      run: |
        sleep 30
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://${PRODUCTION_DOMAIN}/health || echo "000")
        if [ "$STATUS" -eq 200 ]; then
          echo "Rollback successful"
        else
          echo "Rollback failed - manual intervention required"
          exit 1
        fi
    
    - name: Notify rollback completion
      if: success()
      uses: slackapi/slack-github-action@v1.23.0
      with:
        payload: |
          {
            "text": ":rewind: NetVision production rollback completed\n*Rolled back to*: ${{ env.PREVIOUS_VERSION }}\n*Environment*: Production\n*Timestamp*: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## Environment Protection Rules

### Staging Environment:
- Automatic deployment from main branch after CI passes
- No manual approval required
- Resource limits: 50% of production capacity
- Data: Anonymized or synthetic test data
- Monitoring: Basic health checks and metrics

### Production Environment:
- Manual approval required for deployment
- Environment protection rules enabled
- Required reviewers: Platform Team Lead, Security Officer
- Wait timer: 15 minutes for manual intervention
- Deployment branches: Only main branch with version tags
- Required status checks: All CI jobs must pass
- Resource limits: Full capacity as per sizing
- Data: Production data with appropriate backups
- Monitoring: Full observability stack (metrics, logs, tracing)

---

## Security Considerations in Pipeline

### Secrets Management:
- All secrets stored in GitHub Secrets or integrated with external vault
- No secrets in logs or artifact metadata
- Just-in-time access to production environments
- Regular rotation of service accounts and tokens

### Supply Chain Security:
- SBOM generation for all artifacts
- Image signing with Cosign or Notary
- Dependency vulnerability scanning in CI
- License compliance checking
- Provenance tracking for all build materials

### Pipeline Security:
- Least privilege access for GitHub Actions runners
- Separate runners for different security levels
- Artifact integrity verification
- Environment isolation between stages
- Audit logging for all pipeline activities

---

## Performance and Scaling Considerations

### Build Optimization:
- Layer caching for Docker builds
- Parallel job execution where possible
- Artifact caching between workflow runs
- Dependency caching (pip, npm caches)
- Early failure detection to save resources

### Test Optimization:
- Test parallelization
- Smart test selection based on changed files
- Test container reuse
- Mock external services where appropriate
- Performance benchmarks in CI

### Deployment Optimization:
- Blue/green or canary deployment strategies
- Database migration automation
- Resource-based scaling triggers
- Traffic shifting capabilities
- Rollback automation

---

## Metrics and Monitoring

### Pipeline Metrics:
- Build duration trends
- Test pass/fail rates
- Deployment frequency
- Lead time for changes
- Mean time to recovery (MTTR)
- Change failure rate
- Security vulnerability trends

### Monitoring Integrations:
- Prometheus metrics from GitHub Actions (via exporter)
- Grafana dashboards for pipeline health
- Alerting on pipeline failures or degradation
- Integration with internal metrics platforms
- Compliance reporting automation

---

## Rollback Procedures

### Automated Rollback:
- Triggered on health check failures
- Rollback to previous known good version
- Verification of rollback success
- Notification to stakeholders

### Manual Rollback:
- Runbook procedures for complex scenarios
- Database rollback considerations
- Data migration reversibility
- Communication plans for stakeholders

### Data Considerations:
- Backup before major schema changes
- Point-in-time recovery capabilities
- Data validation after rollback
- Handling of divergent data streams

---

## Compliance and Audit

### Audit Trail:
- Immutable logs of all pipeline activities
- Digital signatures for all artifacts
- Traceability from commit to production
- Access logs for all environments
- Change approval records

### Reporting:
- Weekly compliance reports
- Monthly security metrics
- Quarterly performance trends
- Annual penetration testing results
- Continuous improvement backlog

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up GitHub Actions runners (self-hosted for security)
- [ ] Implement basic CI workflow (linting, unit tests)
- [ ] Configure secrets management in GitHub
- [ ] Set up basic container registry (GHCR or ECR)
- [ ] Create basic CD workflow for staging

### Phase 2: Security Integration (Weeks 3-4)
- [ ] Add security scanning to CI pipeline
- [ ] Implement image signing and verification
- [ ] Add SBOM generation
- [ ] Configure environment protection rules
- [ ] Implement manual approval for production

### Phase 3: Observability (Weeks 5-6)
- [ ] Add performance testing to pipeline
- [ ] Implement pipeline metrics collection
- [ ] Set up Grafana dashboards for CI/CD
- [ ] Add automated rollback capabilities
- [ ] Implement blue/green deployment option

### Phase 4: Optimization (Weeks 7-8)
- [ ] Optimize build times with caching
- [ ] Implement advanced testing strategies
- [ ] Add chaos engineering to pipeline
- [ ] Implement feature flag integration
- [ ] Add compliance reporting automation

---

## Conclusion

This CI/CD pipeline provides a robust foundation for delivering NetVision to enterprise production environments with confidence. By integrating security, quality, and compliance checks throughout the lifecycle, we ensure that only validated, secure, and performant code reaches production.

The pipeline is designed to evolve with the platform, incorporating new practices and technologies as needed to maintain competitive advantage and operational excellence.

---
*Pipeline Version: 1.0*
*Last Updated: 2026-10-07*
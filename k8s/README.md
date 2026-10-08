# NetVision Kubernetes Manifests

This directory contains Kubernetes manifests for deploying NetVision to production environments.

## Directory Structure

```
k8s/
├── base/           # Base templates (environment-agnostic)
├── staging/        # Staging environment specific values
└── production/     # Production environment specific values
```

## Deployment Instructions

### Prerequisites
- Kubernetes 1.24+
- Helm 3.0+
- External secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.)
- Ingress controller (NGINX, Istio, etc.)
- Monitoring stack (Prometheus, Grafana, Loki)
- Logging stack (Elasticsearch, Fluentd, Kibana or Loki)

### Deployment Methods

#### Using Helm (Recommended)
```bash
# Add required repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add influxdata https://helm.influxdata.com
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add elastic https://helm.elastic.co

# Deploy base services (use upgrade --install to safely rerun these commands)
helm upgrade --install postgres bitnami/postgresql \
  --set auth.username=user \
  --set auth.password=REPLACE_WITH_DATABASE_PASSWORD \
  --set auth.database=monitoring

helm upgrade --install influxdb influxdata/influxdb \
  --set influxdb.username=admin \
  --set influxdb.password=REPLACE_WITH_INFLUXDB_PASSWORD \
  --set influxdb.database=monitoring

# Deploy NetVision application
helm upgrade --install netvision ./k8s \
  -f k8s/staging/values.yaml  # Use k8s/production/values.yaml for production
```

Pass the same `--namespace <namespace>` to each command if deploying outside
the default namespace; releases with the same name in different namespaces are
separate Helm releases. Replace placeholder credentials and secret values
before deploying.

#### Using Kubectl

The `staging` and `production` directories currently contain Helm values files,
not Kustomize overlays. Deploy them with the Helm commands above.

To apply individual non-templated manifests directly, use `kubectl apply -f`
on the relevant files in `k8s/base/`; files containing Helm template
expressions must be rendered by Helm first.

## Environment Variables

All configuration is managed through environment variables and ConfigMaps/Secrets.
See individual manifest files for specific variables.

## Scaling

Horizontal Pod Autoscaler (HPA) is configured for all deployments.
Adjust autoscaling parameters in the values.yaml files.

## Security

- All containers run as non-root users
- Read-only root filesystem where possible
- Unnecessary Linux capabilities dropped
- Network policies enforce zero-trust principles
- Secrets should be managed externally (not stored in Git)

## Monitoring

- Prometheus metrics endpoints exposed on all services
- ServiceMonitors included for automatic discovery
- Health checks configured for liveness and readiness probes
- Resource requests and limits defined for QoS classes

## Customization

Override values in the environment-specific values.yaml files:
- k8s/staging/values.yaml
- k8s/production/values.yaml

For more complex customization, create additional overlay directories.
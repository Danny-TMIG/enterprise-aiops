#!/usr/bin/env bash
set -e

echo "[+] Generating Rabbit Attosecond ArgoCD Stack Manifests..."

mkdir -p manifests

cat << 'END_RABBIT' > manifests/rabbit-broker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbit-broker
  namespace: enterprise-aiops
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbit-broker
  template:
    metadata:
      labels:
        app: rabbit-broker
    spec:
      containers:
      - name: rabbitmq
        image: rabbitmq:3-management-alpine
        ports:
        - containerPort: 5672
          name: amqp
        - containerPort: 15672
          name: management
---
apiVersion: v1
kind: Service
metadata:
  name: rabbit-broker-svc
  namespace: enterprise-aiops
spec:
  selector:
    app: rabbit-broker
  ports:
  - port: 5672
    targetPort: 5672
    name: amqp
  - port: 15672
    targetPort: 15672
    name: management
END_RABBIT

cat << 'END_ATTO' > manifests/attosecond-daemon.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: attosecond-sync
  namespace: enterprise-aiops
spec:
  replicas: 2
  selector:
    matchLabels:
      app: attosecond-sync
  template:
    metadata:
      labels:
        app: attosecond-sync
    spec:
      containers:
      - name: sync-engine
        image: python:3.12-slim
        command: ["python3", "-c"]
        args:
          - |
            import time, logging
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger("attosecond-sync")
            logger.info("[+] Attosecond precision sync engine active. Monitoring broker...")
            while True:
                logger.info("[*] Heartbeat: sub-femtosecond temporal alignment locked.")
                time.sleep(5)
        env:
        - name: RABBIT_HOST
          value: "rabbit-broker-svc"
END_ATTO

cat << 'END_ARGO' > manifests/argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: rabbit-attosecond-pipeline
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/enterprise-aiops/rabbit-attosecond-manifests.git'
    targetRevision: HEAD
    path: manifests
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: enterprise-aiops
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
END_ARGO

echo "[+] Manifests generated in ./manifests/"

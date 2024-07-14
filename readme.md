## Kubernetes Webhooks on Minikube

This project demonstrates setting up mutating and validating webhooks on a local Kubernetes cluster using Minikube.

### Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

### Setup Instructions

#### 1. Start Minikube

Start your Minikube cluster:

```bash
minikube start
```

#### 2. Configure Docker to Use Minikube's Docker Daemon

Configure your shell to use Minikube's Docker daemon:

```bash
eval $(minikube -p minikube docker-env)
```

#### 3. Build the Docker Image

Build the Docker image for the webhook server:

```bash
docker build -t webhook-server:latest .
```

#### 4. Verify the Image

Ensure the image is available in Minikube's Docker registry:

```bash
docker images | grep webhook-server
```

#### 5. Generate Certificates

Generate the CA and server certificates with SANs:

```bash
# Create CA
openssl genpkey -algorithm RSA -out ca-key.pem
openssl req -x509 -new -nodes -key ca-key.pem -days 365 -out ca-cert.pem -subj "/CN=Webhook CA"

# Create OpenSSL Configuration File for SANs
cat <<EOF > webhook-csr.conf
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name

[req_distinguished_name]
countryName = Country Name (2 letter code)
countryName_default = US
stateOrProvinceName = State or Province Name (full name)
stateOrProvinceName_default = California
localityName = Locality Name (eg, city)
localityName_default = San Francisco
organizationName = Organization Name (eg, company)
organizationName_default = MyCompany
commonName = Common Name (e.g. server FQDN or YOUR name)
commonName_default = webhook-service.default.svc

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = webhook-service.default.svc
DNS.2 = webhook-service.default.svc.cluster.local
EOF

# Create server certificate
openssl genpkey -algorithm RSA -out server-key.pem
openssl req -new -key server-key.pem -out server.csr -config webhook-csr.conf
openssl x509 -req -in server.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 365 -extensions v3_req -extfile webhook-csr.conf
```

#### 6. Create a Kubernetes Secret for TLS Certificates

Create a secret to store the TLS certificates:

```bash
kubectl create secret tls webhook-server-tls --cert=server-cert.pem --key=server-key.pem
```

#### 7. Deploy the Webhook Server

Create the deployment and service for the webhook server:

```bash
kubectl apply -f webhook-deployment.yaml
kubectl apply -f webhook-service.yaml
```

#### 8. Base64 Encode the CA Certificate

Encode the CA certificate in base64 and remove any newline characters:

```bash
cat ca-cert.pem | base64 | tr -d '\n' > ca-cert-base64.txt
```

#### 9. Create and Apply Webhook Configurations

Replace `<base64_encoded_ca_cert>` in your webhook configurations with the content of `ca-cert-base64.txt`.

Apply the webhook configurations:

```bash
kubectl apply -f mutating-webhook-configuration.yaml
kubectl apply -f validating-webhook-configuration.yaml
```

#### 10. Test the Webhooks

Create a test Pod to verify the webhooks:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: nginx
    image: nginx
```

Apply the test Pod:

```bash
kubectl apply -f test-pod.yaml
```

Check the Pod to ensure the `env: production` label has been added by the mutating webhook and that the Pod is rejected if resource requests and limits are not defined:

```bash
kubectl get pod test-pod -o yaml
```

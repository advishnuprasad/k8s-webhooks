from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/mutate', methods=['POST'])
def mutate():
    request_info = request.get_json()
    pod = request_info['request']['object']
    uid = request_info['request']['uid']

    patch = []

    if 'metadata' in pod and 'labels' in pod['metadata']:
        labels = pod['metadata']['labels']
        if 'env' not in labels:
            patch.append({
                "op": "add",
                "path": "/metadata/labels/env",
                "value": "production"
            })
    else:
        patch.append({
            "op": "add",
            "path": "/metadata/labels",
            "value": {"env": "production"}
        })

    admission_response = {
        "response": {
            "uid": uid,
            "allowed": True,
            "patch": json.dumps(patch),
            "patchType": "JSONPatch"
        }
    }

    return jsonify(admission_response)

@app.route('/validate', methods=['POST'])
def validate():
    request_info = request.get_json()
    pod = request_info['request']['object']
    uid = request_info['request']['uid']

    allowed = True
    reason = ""

    for container in pod.get('spec', {}).get('containers', []):
        if not container.get('resources', {}).get('requests') or not container.get('resources', {}).get('limits'):
            allowed = False
            reason = "All containers must have resource requests and limits defined."
            break

    admission_response = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": uid,
            "allowed": allowed
        }
    }

    if not allowed:
        admission_response["response"]["status"] = {
            "reason": reason
        }

    return jsonify(admission_response)

if __name__ == '__main__':
    context = ('/app/server-cert.pem', '/app/server-key.pem')
    print(context)
    app.run(host='0.0.0.0', port=443, ssl_context=context)


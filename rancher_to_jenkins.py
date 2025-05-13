import os
import requests
import jenkins
import base64
import urllib3
from urllib.parse import quote
from requests.auth import HTTPBasicAuth

# Suppress HTTPS warnings (Rancher with self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Environment config
RANCHER_URL = os.environ.get('RANCHER_URL')
RANCHER_ACCESS_KEY = os.environ.get('RANCHER_ACCESS_KEY')
RANCHER_SECRET_KEY = os.environ.get('RANCHER_SECRET_KEY')
JENKINS_URL = os.environ.get('JENKINS_URL')
JENKINS_USER = os.environ.get('JENKINS_USER')
JENKINS_TOKEN = os.environ.get('JENKINS_TOKEN')

# Use HTTP Basic Auth for Rancher
auth = HTTPBasicAuth(RANCHER_ACCESS_KEY, RANCHER_SECRET_KEY)

def get_clusters():
    print(f"[INFO] Connecting to Rancher at {RANCHER_URL}")
    url = f"{RANCHER_URL}/v3/clusters"
    response = requests.get(url, auth=auth, verify=False)
    response.raise_for_status()
    return response.json()["data"]

def get_kubeconfig(cluster_id):
    encoded_id = quote(cluster_id, safe='')
    url = f"{RANCHER_URL}/v3/clusters/{encoded_id}?action=generateKubeconfig"
    response = requests.post(url, auth=auth, verify=False)
    response.raise_for_status()
    return response.json()["config"]

def create_file_credential(server, cluster_name, kubeconfig):
    credential_id = f"kubeconfig-{cluster_name}"
    encoded_content = base64.b64encode(kubeconfig.encode()).decode()

    xml = f"""<com.cloudbees.plugins.credentials.impl.FileCredentialsImpl>
  <scope>GLOBAL</scope>
  <id>{credential_id}</id>
  <description>Kubeconfig for Rancher cluster {cluster_name}</description>
  <fileName>config</fileName>
  <secretBytes>{encoded_content}</secretBytes>
</com.cloudbees.plugins.credentials.impl.FileCredentialsImpl>"""

    try:
        server.get_credentials_xml('system', '::', credential_id)
        print(f"[SKIP] Credential '{credential_id}' already exists.")
    except:
        server.create_credentials('system', '::', xml)
        print(f"[ADD] Credential '{credential_id}' created.")

def main():
    print(f"[INFO] Connecting to Jenkins at {JENKINS_URL} as {JENKINS_USER}")
    server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_TOKEN)

    try:
        clusters = get_clusters()
    except Exception as e:
        print(f"[ERROR] Failed to retrieve clusters: {e}")
        return

    print(f"[INFO] Found {len(clusters)} cluster(s).")

    for cluster in clusters:
        cluster_id = cluster["id"]
        cluster_name = cluster.get("name", cluster_id)
        print(f"[INFO] Processing cluster: {cluster_name} ({cluster_id})")
        try:
            kubeconfig = get_kubeconfig(cluster_id)
            create_file_credential(server, cluster_name, kubeconfig)
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] Rancher error for {cluster_name}: {e}")
        except Exception as e:
            print(f"[ERROR] General failure for {cluster_name}: {e}")

if __name__ == "__main__":
    main()

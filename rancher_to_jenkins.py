import os
import requests
import jenkins

# Required environment variables
RANCHER_URL = os.environ.get('RANCHER_URL')
RANCHER_TOKEN = os.environ.get('RANCHER_TOKEN')
JENKINS_URL = os.environ.get('JENKINS_URL')
JENKINS_USER = os.environ.get('JENKINS_USER')
JENKINS_TOKEN = os.environ.get('JENKINS_TOKEN')

def get_clusters():
    print(f"[INFO] Connecting to Rancher at {RANCHER_URL}")
    headers = {"Authorization": f"Bearer {RANCHER_TOKEN}"}
    url = f"{RANCHER_URL}/v3/clusters"
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()["data"]

def get_kubeconfig(cluster_id):
    headers = {"Authorization": f"Bearer {RANCHER_TOKEN}"}
    url = f"{RANCHER_URL}/v3/clusters/{cluster_id}?action=generateKubeconfig"
    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()["config"]

def create_jenkins_credential(server, cluster_id, kubeconfig):
    credential_id = f"kubeconfig-{cluster_id}"
    xml = f"""<com.cloudbees.plugins.credentials.impl.StringCredentialsImpl>
  <scope>GLOBAL</scope>
  <id>{credential_id}</id>
  <description>Kubeconfig for Rancher cluster {cluster_id}</description>
  <secret>{kubeconfig}</secret>
</com.cloudbees.plugins.credentials.impl.StringCredentialsImpl>"""

    try:
        server.get_credentials_xml('system', '::', credential_id)
        print(f"[SKIP] Credential '{credential_id}' already exists.")
    except:
        server.create_credentials('system', '::', xml)
        print(f"[ADD] Credential '{credential_id}' created.")

def main():
    print(f"[INFO] Connecting to Jenkins at {JENKINS_URL} as {JENKINS_USER}")
    server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_TOKEN)

    clusters = get_clusters()
    print(f"[INFO] Found {len(clusters)} cluster(s).")

    for cluster in clusters:
        cluster_id = cluster["id"]
        name = cluster.get("name", cluster_id)
        print(f"[INFO] Processing cluster: {name} ({cluster_id})")
        try:
            kubeconfig = get_kubeconfig(cluster_id)
            create_jenkins_credential(server, cluster_id, kubeconfig)
        except Exception as e:
            print(f"[ERROR] Failed for cluster {cluster_id}: {e}")

if __name__ == "__main__":
    main()

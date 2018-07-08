from eksauth import auth
from kubernetes import client, config

# Get EKS auth token
eks = auth.EKSAuth('TestBed')
token = eks.get_token()

# Load kubernetes configuration
config.load_kube_config()
configuration = client.Configuration()
configuration.api_key['authorization'] = token
configuration.api_key_prefix['authorization'] = 'Bearer'


api = client.ApiClient(configuration)
v1 = client.CoreV1Api(api)

ret = v1.list_pod_for_all_namespaces(watch=False)

for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


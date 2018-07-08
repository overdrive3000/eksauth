import base64
import boto3
import string
import random
from botocore.signers import RequestSigner

class EKSAuth(object):

    METHOD = 'GET'
    EXPIRES = 60
    EKS_HEADER = 'x-k8s-aws-id'
    EKS_PREFIX = 'k8s-aws-v1.'
    STS_URL = 'sts.amazonaws.com'
    STS_ACTION = 'Action=GetCallerIdentity&Version=2011-06-15'

    def __init__(self, cluster_id, region='us-east-1', role_arn=None):
        self.cluster_id = cluster_id
        self.region = region
        self.role_arn = role_arn
    
    def __get_random_session_name(self):
        """
        Return an unique session name for EKS Auth module
        https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
        """
        chars=string.ascii_uppercase + string.digits
        suffix = ''.join(random.choice(chars) for _ in range(6))
        return 'EKSAUTH_' + suffix

    def __get_session(self):
        """
        Return session object
        """
        if self.role_arn is None:
            return boto3.Session(region_name=self.region)
    
        session_name = self.__get_random_session_name()
        client = boto3.client('sts')
        response = client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=session_name
        )
        return boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken']
        )
    
    def get_token(self):
        """
        Return bearer token
        """
        sess = self.__get_session()
        signer = RequestSigner(
            'sts',
            sess.region_name,
            'sts',
            'v4',
            sess.get_credentials(),
            sess.events
        )

        params = {
            'method': self.METHOD,
            'url': 'https://' + self.STS_URL + '/?' + self.STS_ACTION,
            'body': {},
            'headers': {
                self.EKS_HEADER: self.cluster_id
            },
            'context': {}
        }

        signed_url = signer.generate_presigned_url(
            params,
            region_name=sess.region_name,
            expires_in=self.EXPIRES,
            operation_name=''
        )

        return (
            self.EKS_PREFIX +
            base64.urlsafe_b64encode(
                signed_url.encode('utf-8')
            ).decode('utf-8')
        )
from eksauth import auth

eks = auth.EKSAuth('TestBed')
print(eks.get_token())
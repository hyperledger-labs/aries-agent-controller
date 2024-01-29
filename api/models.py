# from __future__ import annotations
from django.db import models
from typing import List
from pydantic import BaseModel
from django.core.exceptions import ObjectDoesNotExist
import uuid

# Create your models here.
class User(models.Model):
    # attributes
    did = models.CharField(max_length=500, default=None)
    userId = models.CharField(max_length=500, default=None)
    walletId = models.CharField(max_length=500, default=None)
    email = models.CharField(max_length=500, default=None)
    verkey = models.CharField(max_length=500, default=None)
    role = models.CharField(max_length=500, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    label = models.UUIDField(default=uuid.uuid4)
    issuer_to_holder_conn = models.CharField(max_length=500, default=None, null=True)
    holder_to_issuer_conn = models.CharField(max_length=500, default=None, null=True)
    verifier_to_holder_conn = models.CharField(max_length=500, default=None, null=True)
    holder_to_verifier_conn = models.CharField(max_length=500, default=None, null=True)
    mspId = models.CharField(max_length=500, default='Org1MSP', null=True)

    def __str__(self):
        return self.did + ' ' + self.email

    @classmethod
    def create_and_save(cls, did, userId, email, verkey, walletId, role, label, mspId):
        new_user = cls(did=did, userId=userId, email=email, verkey=verkey, walletId=walletId,role=role, label=label, mspId=mspId)
        new_user.save()
        return new_user
    
    @classmethod
    def update_issuer_connection(cls, issuer_to_holder_conn=None, did=None, userId=None, label=None ):
        if label is None and did is None and userId is None: 
            raise ValueError("Either did or userId must be provided")
        try :
            if label:
                connection = cls.objects.get(label=label)
            elif did:
                connection = cls.objects.get(did=did)
            else: 
                connection = cls.objects.get(userId=userId)
            
            connection.issuer_to_holder_conn = issuer_to_holder_conn

            connection.save()
            return connection
        
        except ObjectDoesNotExist : 
            raise ValueError("Did or userId does not exist")
        
    @classmethod
    def update_holder_connection(cls, holder_to_issuer_conn=None, did=None, userId=None, label=None ):
        if label is None and userId is None and did is None: 
            raise ValueError("Either did or userId must be provided")
        try : 
            if label:
                connection = cls.objects.get(label=label)
            elif did:
                connection = cls.objects.get(did=did)
            else: 
                connection = cls.objects.get(userId=userId)
            
            connection.holder_to_issuer_conn = holder_to_issuer_conn

            connection.save()
            return connection
        
        except ObjectDoesNotExist : 
            raise ValueError("Did or userId does not exist")
        
    @classmethod
    def update_verifier_holder_connection(cls, verifier_to_holder_conn=None, did=None, userId=None, label=None ):
        if label is None and did is None and userId is None: 
            raise ValueError("Either did or userId must be provided")
        try :
            if label:
                connection = cls.objects.get(label=label)
            elif did:
                connection = cls.objects.get(did=did)
            else: 
                connection = cls.objects.get(userId=userId)
            
            connection.verifier_to_holder_conn = verifier_to_holder_conn

            connection.save()
            return connection
        
        except ObjectDoesNotExist : 
            raise ValueError("Did or userId does not exist")
        
    @classmethod
    def update_holder_verifier_connection(cls, holder_to_verifier_conn=None, did=None, userId=None, label=None ):
        if label is None and userId is None and did is None: 
            raise ValueError("Either did or userId must be provided")
        try : 
            if label:
                connection = cls.objects.get(label=label)
            elif did:
                connection = cls.objects.get(did=did)
            else: 
                connection = cls.objects.get(userId=userId)
            
            connection.holder_to_verifier_conn = holder_to_verifier_conn

            connection.save()
            return connection
        
        except ObjectDoesNotExist : 
            raise ValueError("Did or userId does not exist")

        
    @classmethod
    def get_did_by_userId(cls, userId):
        try:
            user = cls.objects.get(userId=userId)
            return user.did
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_did_by_walletId(cls, walletId):
        try:
            user = cls.objects.get(walletId=walletId)
            return user.did
        except cls.DoesNotExist:
            return None
        
    @classmethod
    def get_connections_by_did(cls, did):
        try:
            user = cls.objects.get(did=did)
            resp = {"issuer_to_holder_conn": user.issuer_to_holder_conn,
                    "holder_to_issuer_conn": user.holder_to_issuer_conn,
                    "verifier_to_holder_conn": user.verifier_to_holder_conn,
                    "holder_to_verifier_conn": user.holder_to_verifier_conn
                    }
            return resp
        except cls.DoesNotExist:
            return None
    @classmethod
    def get_label_by_did(cls, did):
        try:
            user = cls.objects.get(did=did)
            return user.label
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_walletId_by_did(cls, did):
        try:
            user = cls.objects.get(did=did)
            return user.walletId
        except cls.DoesNotExist:
            return None
    @classmethod
    def get_walletId_by_userId(cls, userId):
        try:
            user = cls.objects.get(userId=userId)
            return user.walletId
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_mspId_by_did(cls, did):
        try:
            user = cls.objects.get(did=did)
            return user.mspId
        except cls.DoesNotExist:
            return None

class Schema(models.Model):
    # attributes
    org_name = models.CharField(max_length=500, default=None)
    schema_name = models.CharField(max_length=500, default=None)
    schema_id = models.CharField(max_length=500, default=None)
    cred_def_id = models.CharField(max_length=500, default=None)
    attributes = models.JSONField(default=None)
    version = models.CharField(max_length=500, default=None)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.schema_id + ' ' + self.cred_def_id
    
    @classmethod
    def save_schema_details(cls, org_name, schema_name, schema_id, cred_def_id, attributes, version):
        new_schema = cls(org_name=org_name, schema_name=schema_name, schema_id=schema_id, cred_def_id=cred_def_id, attributes=attributes, version=version)
        new_schema.save()
        return new_schema
    
    @classmethod
    def get_schema_by_name_and_version(cls, name, version):
        try:
            schema = cls.objects.get(schema_name=name, version=version)
            return schema
        except cls.DoesNotExist:
            return None
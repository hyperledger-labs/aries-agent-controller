
from rest_framework import serializers
from .models import User, Schema

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ('__all__') 

class SchemaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Schema
        fields = ('__all__') 


#========Register ====================================

class RegisterRequestSerializer(serializers.Serializer):
    userId = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    creator = serializers.CharField(required=True)
    mspId = serializers.CharField(required=True)

class RegisterResponseSerializer(serializers.Serializer):
    did = serializers.CharField(required=True)
    userId = serializers.CharField(required=True)
    verkey = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class WalletSettingsSerializer(serializers.Serializer):
    wallet_type = serializers.CharField(source='wallet.type')
    wallet_name = serializers.CharField(source='wallet.name')
    wallet_webhook_urls = serializers.ListField(
        child=serializers.URLField(),
        source='wallet.webhook_urls'
    )
    wallet_dispatch_type = serializers.CharField(source='wallet.dispatch_type')
    default_label = serializers.CharField()
    wallet_id = serializers.UUIDField(source='wallet.id')

class GetUserResponseSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    wallet_id = serializers.UUIDField()
    key_management_mode = serializers.CharField()
    settings = WalletSettingsSerializer()

#========Schema ====================================

class CreateSchemaSerializer(serializers.Serializer):
    org_name = serializers.CharField(max_length=100)
    attributes = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )
    schema_name = serializers.CharField(max_length=100)
    schema_version = serializers.CharField(max_length=10)
    registry_size = serializers.IntegerField()
    revocation = serializers.BooleanField()

class CreateSchemaResponseSerializer(serializers.Serializer):
    schema_id = serializers.CharField(max_length=100)
    cred_def_id = serializers.CharField(max_length=100)

class SchemaSerializer(serializers.Serializer):
    schema_ids = serializers.ListField(
        child=serializers.CharField()
    )

class CredentialDefinitionSerializer(serializers.Serializer):
    credential_definition_ids = serializers.ListField(
        child=serializers.CharField()
    )

class GetSchemaResponseSerializer(serializers.Serializer):
    schemas = SchemaSerializer()
    credential_definitions = CredentialDefinitionSerializer()

#========Agents ====================================

class ConnectAgents(serializers.Serializer):
    userId = serializers.CharField(required=True)

class ConnectionSerializer(serializers.Serializer):
    state = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    connection_id = serializers.CharField()
    my_did = serializers.CharField()
    their_label = serializers.CharField()
    their_role = serializers.CharField()
    connection_protocol = serializers.CharField()
    rfc23_state = serializers.CharField()
    invitation_key = serializers.CharField()
    invitation_msg_id = serializers.CharField()
    request_id = serializers.CharField()
    accept = serializers.CharField()
    invitation_mode = serializers.CharField()

class ConnectionListResponse(serializers.ListSerializer):
    child = ConnectionSerializer()    

class AgentConnectionsRequest(serializers.Serializer):
    userId = serializers.CharField(required=True)

class AgentConnectionsResponse(serializers.Serializer):
    issuer_to_holder_conn = serializers.CharField(max_length=100)
    holder_to_issuer_conn = serializers.CharField(max_length=100)
    verifier_to_holder_conn = serializers.CharField(max_length=100)
    holder_to_verifier_conn = serializers.CharField(max_length=100)


#========Issue ====================================

class AttributeSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()

class CredentialPreviewSerializer(serializers.Serializer):
    type = serializers.CharField(source='@type')
    attributes = AttributeSerializer(many=True)

class FormatSerializer(serializers.Serializer):
    attach_id = serializers.CharField()
    format = serializers.CharField()

class DataSerializer(serializers.Serializer):
    base64 = serializers.CharField()

class FilterAttachSerializer(serializers.Serializer):
    id = serializers.CharField(source='@id')
    mime_type = serializers.CharField()
    data = DataSerializer()

class CredentialProposalSerializer(serializers.Serializer):
    type = serializers.CharField(source='@type')
    id = serializers.CharField(source='@id')
    comment = serializers.CharField()
    credential_preview = CredentialPreviewSerializer()
    formats = FormatSerializer(many=True)
    filters_attach = FilterAttachSerializer(many=True, source='filters~attach')

# class ThreadSerializer(serializers.Serializer):
#     # Add fields as necessary

class CredentialOfferSerializer(serializers.Serializer):
    type = serializers.CharField(source='@type')
    id = serializers.CharField(source='@id')
    # thread = ThreadSerializer()
    comment = serializers.CharField()
    credential_preview = CredentialPreviewSerializer()
    formats = FormatSerializer(many=True)
    offers_attach = FilterAttachSerializer(many=True, source='offers~attach')

class IndyFormatSerializer(serializers.Serializer):
    cred_def_id = serializers.CharField()
    schema_id = serializers.CharField()
    issuer_did = serializers.CharField()

class ByFormatSerializer(serializers.Serializer):
    indy = IndyFormatSerializer()

class CredentialExchangeSerializer(serializers.Serializer):
    state = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    cred_ex_id = serializers.CharField()
    connection_id = serializers.CharField()
    thread_id = serializers.CharField()
    initiator = serializers.CharField()
    role = serializers.CharField()
    cred_preview = CredentialPreviewSerializer()
    cred_proposal = CredentialProposalSerializer()
    cred_offer = CredentialOfferSerializer()
    by_format = ByFormatSerializer()
    auto_offer = serializers.BooleanField()
    auto_remove = serializers.BooleanField()

class IssueRequestSerializer(serializers.Serializer):
    attributes = serializers.DictField(required=True)
    name = serializers.CharField(required=True)
    version = serializers.CharField(required=True)
    userId = serializers.CharField(required=True)

    def get_dynamic_fields(self):
        dynamic_fields = []
        for key in self.initial_data.get('attributes', {}):
            dynamic_fields.append(key)
        return dynamic_fields

#========Proof ====================================


class ProofRequestSerializer(serializers.Serializer):
    userId = serializers.CharField(max_length=100)
    schema_name = serializers.CharField(max_length=100)
    version = serializers.CharField(max_length=10)

class RestrictionsSerializer(serializers.Serializer):
    schema_name = serializers.CharField(max_length=100)
    schema_version = serializers.CharField(max_length=10)
    issuer_did = serializers.CharField(max_length=100)

class RequestedAttributeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    restrictions = RestrictionsSerializer(many=True)

class IndySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    requested_attributes = serializers.DictField(child=RequestedAttributeSerializer())
    requested_predicates = serializers.DictField()  
    version = serializers.CharField(max_length=10)
    nonce = serializers.CharField(max_length=100)

class PresentationRequestSerializer(serializers.Serializer):
    _type = serializers.CharField(max_length=100, source="@type")
    _id = serializers.CharField(max_length=100, source="@id")
    will_confirm = serializers.BooleanField()
    formats = serializers.ListField(child=serializers.DictField())
    request_presentations_attach = serializers.ListField(child=serializers.DictField(), source="request_presentations~attach")

class ProofRequestPostResponseSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    trace = serializers.BooleanField()
    pres_ex_id = serializers.CharField(max_length=100)
    connection_id = serializers.CharField(max_length=100)
    thread_id = serializers.CharField(max_length=100)
    initiator = serializers.CharField(max_length=50)
    role = serializers.CharField(max_length=50)
    pres_request = PresentationRequestSerializer()
    by_format = serializers.DictField(child=IndySerializer())
    auto_present = serializers.BooleanField()
    auto_remove = serializers.BooleanField()


#========Credential ====================================

class CredentialResponseSerializer(serializers.Serializer):
    attributes = serializers.DictField(required=True)

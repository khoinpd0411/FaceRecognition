from src.app import ma
from src.app.models import Role, Identity, Access
from marshmallow import fields, validate

class RoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Role
    
    id = fields.Integer(dump_only = True)                                                                                                 # skip this value during serialization
    name = fields.String(required = True)                               # raise a "ValidationError" if field value is not supplied
    access_right = fields.Boolean(required = True)

class IdentitySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Identity
    
    id = fields.Integer(dump_only = True)
    name = fields.String(required = True)
    anchor_path = fields.String(required = True)
    embedding_path = fields.String(required = True)
    role_id = fields.Integer(required = True)

class AccessSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Access

    time = fields.DateTime(required = True)
    key = fields.String(required = True)
    query_path = fields.String(required = True)
    identity_id = fields.Integer(required = True)
    conf_score = fields.Float(required = True)
    permission_status = fields.Boolean(required = True)
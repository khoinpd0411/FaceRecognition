from marshmallow import Schema, fields, INCLUDE

class FeatureExtractorValidator(Schema):
    class Meta:
        unknown = INCLUDE
    
    image = fields.String(required = True)

class FaceSearchValidator(Schema):
    class Meta:
        unknown = INCLUDE
    
    image = fields.String(required = True)
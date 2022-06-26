from flask import make_response, request, Blueprint
from ...models import Identity, Role, Access
from ...validators import IdentitySchema, RoleSchema, AccessSchema
from ...handlers import response_with
from ...handlers import responses as resp
from ....app import db

database_routes = Blueprint('database_routes', __name__)

@database_routes.route('/<table>/create', methods = ['POST'])
def create(table):
    data = request.get_json()['data']
    if table == 'role':
        schema = RoleSchema()          
    elif table == 'identity':
        schema = IdentitySchema()
    else:
        return response_with(resp.SERVER_ERROR_404)
    
    try:
        samples, error = schema.load(data)
        db.session.add_all(samples)
    except:
        return response_with(resp.INVALID_INPUT_422)

    return response_with(resp.SUCCESS_201)

@database_routes.route('/<table>/retrieve/<id>', methods = ['GET'])
def retrieve_id(table, id):
    if table == 'role':
        query_target = Role.query.get(int(id))
        schema = RoleSchema()     
    elif table == 'identity':
        query_target = Identity.query.get(int(id))
        schema = IdentitySchema()
    
    query_target = schema.dump(query_target)
    return response_with(resp.SUCCESS_200, value = query_target)

@database_routes.route('/<table>/retrieve/<name>', methods = ['GET'])
def retrieve_name(table, name):
    if table == 'role':
        try:
            query_target = Role.query.get(name)
            schema = RoleSchema()
        except:
            return response_with(resp.SERVER_ERROR_404)
    elif table == 'identity':
        try:
            query_target = Identity.query.filter_by(name = name).all()
            schema = IdentitySchema()
        except:
            return response_with(resp.SERVER_ERROR_404)
    else:
        return response_with(resp.SERVER_ERROR_404)
    
    query_target = schema.dump(query_target)
    return response_with(resp.SUCCESS_200, value = query_target)  

@database_routes.route('/access/retrieve/<key>', methods = ['GET'])
def retrieve_key(key):
    try:
        query_target = Access.query.get(key)
        schema = AccessSchema()     
    except:
        return response_with(resp.SERVER_ERROR_404)
    
    query_target = schema.dump(query_target)
    return response_with(resp.SUCCESS_200, value = query_target) 

@database_routes.route('/<table>/retrieve/<key>', methods = ['GET'])
def retrieve_path(table, path):
    if table == 'identity':
        try:
            query_target = Identity.query.filter_by(anchor_path = path).first()
            schema = IdentitySchema()
        except:
            return response_with(resp.SERVER_ERROR_404)
    elif table == 'access':
        try:
            query_target = Access.query.filter_by(query_path = path).first()
            schema = AccessSchema()    
        except:
            return response_with(resp.SERVER_ERROR_404)  
    else:
        return response_with(resp.SERVER_ERROR_404)
    
    query_target = schema.dump(query_target)
    return response_with(resp.SUCCESS_200, value = query_target)

@database_routes.route('/<table>/update/<id>', methods = ['PUT'])
def update_id(table, id):
    data = request.get_json()['data']
    if table == 'role':
        query_target = Role.query.get(int(id))
        if data.get['access_right']:
            query_target.access_right = data.get['access_right']
        if data.get['name']:
            query_target.name = data.get['name']

    elif table == 'identity':
        query_target = Identity.query.get(int(id))
        if data.get['anchor_path']:
            query_target.anchor_path = data.get['anchor_path']
        if data.get['name']:
            query_target.name = data.get['name']
        if data.get['role_id']:
            query_target.role_id = data.get['role_id']
        if data.get['embedding']:
            query_target.embedding = data.get['embedding']
        db.session.add(query_target)
        db.session.commit()
    else:
        return response_with(resp.SERVER_ERROR_404)
    
    return response_with(resp.SUCCESS_200, value = query_target)

@database_routes.route('/access/update/<key>', methods = ['PUT'])
def update_permission(key):
    data = request.get_json()['data']
    if data.get['admin_password']:
        try:
            query_target = Access.query.get(key)
            if data.get['permission_status']:
                query_target.permission_status = data.get['permission_status']
            db.session.add(query_target)
            db.session.commit()
        except:
            return response_with(resp.SERVER_ERROR_404)
        
        return response_with(resp.SUCCESS_200, value = query_target)
    else:
        return response_with(resp.HTTP_401_UNAUTHORIZED)

@database_routes.route('/<table>/delete/<id>', methods = ['DELETE'])
def delete_id(table, id):
    if table == 'role':
        query_target = Role.query.get(int(id))
    elif table == 'identity':
        query_target = Identity.query.get(int(id))
    else:
        return response_with(resp.SERVER_ERROR_404)
    db.session.delete(query_target)
    db.session.commit()
    
    return response_with(resp.SUCCESS_204, value = query_target)
from flask import make_response, jsonify

def response_with(response, value = None, message = None, error = None, headers = {}, pagination = None):
    
    result = {}
    
    if value is not None:
        result.update(value)

    if message is not None:
        result.update({'message': message})
    elif response.get('message', None) is not None:
        result.update({'message': response['message']})
    
    result.update({'code': response['code']})

    if error is not None:
        result.update({'error': error})
    
    if pagination is not None:
        result.update({'pagination': pagination})
    
    headers.update({'Access-Control-Allow-Origin': '*'})
    headers.update({'server': 'Flask REST API'})

    return make_response(jsonify(result), response['http_code'], headers)

SUCCESS_200 = {
    'http_code': 200, 
    'code': 'success'
}

SUCCESS_201 = {
    'http_code': 201,
    'code': 'success'
}

SUCCESS_204 = {
    'http_code': 204,
    'code': 'success'
}

BAD_REQUEST_400 = {
    'http_code': 400,
    'code': 'badRequest',
    'message': 'Bad request'
}

HTTP_401_UNAUTHORIZED = {
    'http_code': 401,
    'code': 'unauthorized',
    'message': 'Unauthorized'
}

SERVER_ERROR_404 = {
    'http_code': 404,
    'code': 'notFound',
    'message': 'Resource not found'
}

INVALID_INPUT_422 = {
    'http_code': 422,
    'code': 'invalidInput',
    'message': 'Invalid Input'
}

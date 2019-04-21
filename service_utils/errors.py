import sys

import http.client

from flask import jsonify


GENERAL_ERRORS = {
    'BAD_REQUEST': "The application sent a request that this server could not understand.",
    'BAD_GATEWAY': "The server encountered a temporary error and could not complete your request",
    'INTERNAL_SERVER_ERROR': "Internal server error.",
    'NOT_FOUND': "Resource does not exist.",
    'JSON_PARSE_ERROR': "Unable to parse JSON.",
    'MISSING_PARAMETER': "Query parameter '{field_name}' is required.",
    'MISSING_REPRESENTATION': "Resource representation is missing.",
    'MISSING_PERMISSIONS': "You do not have permissions to access this endpoint.",
    'INVALID_AUTHORIZATION_HEADER': "The request contains an invalid Authorization header.",
    'MISSING_AUTHORIZATION_HEADER': "Request requires a JWT Authorization header.",
    'EXPIRED_AUTHORIZATION_HEADER': "The request contains an expired Authorization header.",
    'INELIGIBLE': "The member is not eligible to perform this transaction.",
    'PRECONDITION_FAILED': "Precondition failed."
}

VALIDATION_ERRORS = {
    'ALL_SCHEMAS_MUST_MATCH': "'{field_name}' must match all referenced schemas.",
    'DEPENDENCY_NOT_SATISFIED': "Dependency not satisfied for '{field_name}'.",
    'ELEMENTS_NOT_UNIQUE': "Elements not unique in '{field_name}'.",
    'INCORRECT_TYPE': "'{field_name}' is incorrect type.",
    'INVALID_FORMAT': "Format error for '{field_name}'.",
    'INVALID_PROPERTY': "Invalid property in '{field_name}'.",
    'INVALID_VALUE': "'{field_name}' has an invalid value.",
    'MATCHES_SCHEMA': "'{field_name}' must not match schema.",
    'MISSING_FIELD': "'{field_name}' is required.",
    'MUST_MATCH_ONE_SCHEMA': "'{field_name}' must match exactly one schema.",
    'NO_ENUM_MATCH': "'{field_name}' does not match any of the specified values.",
    'NO_MATCH': "'{field_name}' does not match regular expression {pattern}.",
    'NO_MATCH_ON_PROPERTY': "Property in '{field_name}' does not match regular expression {pattern}.",
    'NO_SCHEMAS_MATCH': "'{field_name}' does not match at least one referenced schema.",
    'NOT_MULTIPLE': "'{field_name}' is not a multiple.",
    'REQUEST_PARAMETER_MISSING': "Parameter '{field_name}' is missing.",
    'TOO_FEW_ITEMS': "Too few items in array '{field_name}'",
    'TOO_FEW_PROPERTIES': "Too few properties in array '{field_name}'",
    'TOO_MANY_ITEMS': "Too many items in array '{field_name}'",
    'TOO_MANY_PROPERTIES': "Too many items in array '{field_name}'",
    'UNEXPECTED_ITEM': "Unexpected item in '{field_name}'.",
    'UNEXPECTED_PROPERTY': "Unexpected property: '{field_name}'.",
    'VALUE_NOT_UNIQUE': "'{field_name}' must be unique.",
    'VALUE_OUT_OF_RANGE': "The value for '{field_name}' is out of range.",
    'VALUE_TOO_LONG': "The value for '{field_name}' is too long.",
    'VALUE_TOO_SHORT': "The value for '{field_name}' is too short.",
}

ALL_ERRORS = dict(VALIDATION_ERRORS)
ALL_ERRORS.update(GENERAL_ERRORS)
for error in ALL_ERRORS:
    setattr(sys.modules[__name__], error, error)


def create_error(error_code, error_description):
    return {'errors': [{'code': error_code, 'description': error_description}]}


def error_response(http_status_code, error_code, field_name=None, error_map=None):
    error_map = error_map if error_map else ALL_ERRORS
    description = error_map[error_code].format(field_name=field_name)
    response = jsonify(create_error(error_code, description))
    response.status_code = http_status_code
    return response


def get_errors_list_json(errors):
    error_response_list = jsonify(errors=errors)
    error_response_list.status_code = http.client.BAD_REQUEST
    return error_response_list

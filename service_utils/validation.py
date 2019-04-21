import jsonschema
import logging

from service_utils import errors


logger = logging.getLogger(__name__)

ERRORS_BY_JSON_SCHEMA_VALIDATOR = {
    'additionalItems': errors.UNEXPECTED_ITEM,
    'additionalProperties': errors.UNEXPECTED_PROPERTY,
    'allOf': errors.ALL_SCHEMAS_MUST_MATCH,
    'anyOf': errors.NO_SCHEMAS_MATCH,
    'dependencies': errors.DEPENDENCY_NOT_SATISFIED,
    'enum': errors.NO_ENUM_MATCH,
    'format': errors.INVALID_FORMAT,
    'items': errors.TOO_MANY_ITEMS,
    'maximum': errors.VALUE_OUT_OF_RANGE,
    'maxItems': errors.TOO_MANY_ITEMS,
    'maxLength': errors.VALUE_TOO_LONG,
    'maxProperties': errors.TOO_MANY_PROPERTIES,
    'minimum': errors.VALUE_OUT_OF_RANGE,
    'minItems': errors.TOO_FEW_ITEMS,
    'minLength': errors.VALUE_TOO_SHORT,
    'minProperties': errors.TOO_FEW_PROPERTIES,
    'multipleOf': errors.NOT_MULTIPLE,
    'not': errors.MATCHES_SCHEMA,
    'oneOf': errors.MUST_MATCH_ONE_SCHEMA,
    'pattern': errors.NO_MATCH,
    'patternProperties': errors.NO_MATCH_ON_PROPERTY,
    'properties': errors.INVALID_PROPERTY,
    'required': errors.MISSING_FIELD,
    'type': errors.INCORRECT_TYPE,
    'uniqueItems': errors.ELEMENTS_NOT_UNIQUE
}


def _required(validator, required, instance, schema):
    if not validator.is_type(instance, 'object'):
        return
    for field in required:
        if field not in instance:
            e = jsonschema.ValidationError('%r is a required field' % field)
            e.path.append(field)
            yield e


def _additionalProperties(validator, aP, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    extras = set(jsonschema._utils.find_additional_properties(instance, schema))

    if validator.is_type(aP, "object"):
        for extra in extras:
            for error in validator.descend(instance[extra], aP, path=extra):
                yield error
    elif not aP and extras:
        for extra in extras:
            error = "Additional properties are not allowed (%s was unexpected)"
            e = jsonschema.ValidationError(error % extra)
            e.path.append(extra)
            yield e


class MoreSpecificValidator(jsonschema.Draft4Validator):
    VALIDATORS = dict(jsonschema.Draft4Validator.VALIDATORS)
    _already_checked_schemata_max_cache_size = 1000
    _already_checked_schemata = set()

    @classmethod
    def check_schema(cls, schema):
        schema_str = str(schema)
        if schema_str not in cls._already_checked_schemata:
            super(MoreSpecificValidator, cls).check_schema(schema)
            cache_full = (
                len(cls._already_checked_schemata) >=
                cls._already_checked_schemata_max_cache_size)
            if cache_full:
                cls._already_checked_schemata.clear()
            cls._already_checked_schemata.add(schema_str)

    VALIDATORS['required'] = _required
    VALIDATORS['additionalProperties'] = _additionalProperties


def _get_field_name(validation_error):
    if len(validation_error.path) > 0:
        field_name = u'.'.join(map(str, validation_error.path))
    else:
        field_name = None

    return field_name


def validate_against_schema(json_dict, schema):
    errors_list = []
    MoreSpecificValidator.check_schema(schema)
    validator = MoreSpecificValidator(schema)
    for error in validator.iter_errors(json_dict):
        error_code = ERRORS_BY_JSON_SCHEMA_VALIDATOR[error.validator]
        error_description = errors.ALL_ERRORS[error_code]

        field_name = _get_field_name(error)
        pattern = error.schema.get('pattern', '')
        multiple_of = error.schema.get('multipleOf', '')

        if field_name is None:
            description = errors.GENERAL_ERRORS[errors.BAD_REQUEST]
            logger.warning('JSON schema validator \'%s\' did not specify field name.' % error.validator)
        else:
            description = error_description.format(
                field_name=field_name,
                pattern=pattern,
                multiple_of=multiple_of)

        errors_list.append({
            'code': error_code,
            'description': description,
            'field': field_name
        })
    return errors_list

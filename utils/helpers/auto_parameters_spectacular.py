import logging
from typing import Any, Literal, Tuple, Type, Union

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from drf_spectacular.types import (
    OPENAPI_TYPE_MAPPING,
    PYTHON_TYPE_MAPPING,
    OpenApiTypes,
)
from drf_spectacular.utils import OpenApiParameter
from service_objects.services import Service

logger = logging.getLogger("django")

FIELDS_PARAMETERS_MAPPER: dict[Type[forms.Field], Type[OpenApiTypes]] = {
    forms.CharField: OpenApiTypes.STR,
    forms.IntegerField: OpenApiTypes.INT,
    forms.DateField: OpenApiTypes.DATE,
    forms.TimeField: OpenApiTypes.TIME,
    forms.DateTimeField: OpenApiTypes.DATETIME,
    forms.DurationField: OpenApiTypes.DURATION,
    forms.RegexField: OpenApiTypes.REGEX,
    forms.EmailField: OpenApiTypes.EMAIL,
    forms.FileField: OpenApiTypes.BINARY,
    forms.ImageField: OpenApiTypes.BINARY,
    forms.URLField: OpenApiTypes.URI,
    forms.BooleanField: OpenApiTypes.BOOL,
    forms.NullBooleanField: OpenApiTypes.STR,  # might need reconsideration
    forms.ComboField: OpenApiTypes.STR,
    forms.FloatField: OpenApiTypes.FLOAT,
    forms.DecimalField: OpenApiTypes.DECIMAL,
    forms.GenericIPAddressField: OpenApiTypes.STR,
    forms.FilePathField: OpenApiTypes.STR,
    forms.JSONField: OpenApiTypes.OBJECT,
    forms.SlugField: OpenApiTypes.STR,
    forms.UUIDField: OpenApiTypes.UUID,
}

try:
    from phonenumber_field.formfields import PhoneNumberField
except ImportError:
    pass
else:
    FIELDS_PARAMETERS_MAPPER.update({PhoneNumberField: OpenApiTypes.STR})

CHOICE_FIELDS: list[Type[forms.Field]] = [
    forms.ChoiceField,
    forms.TypedChoiceField,
]

MULTIPLE_CHOICE_FIELDS: list[Type[forms.Field]] = [
    forms.MultipleChoiceField,
    forms.TypedMultipleChoiceField,
]

ARRAY_FORMS_FIELDS: list[Type[forms.Field]] = [
    forms.MultiValueField,
    forms.SplitDateTimeField,
]

SPECIAL_DESCRIPTIONS: dict[str, str] = {
    "page": "Number of desired page from the list of paginated results; 1 by default",
    "per_page": "Number of objects to show on each page; 10 by default",
    "sort_field": "Field by which values of the response list will be sorted",
    "sort_direction": "Direction for sorting",
}

PARAMETER_LOCATION_MAPPER: dict[str, str] = {
    "query": OpenApiParameter.QUERY,
    "path": OpenApiParameter.PATH,
}


def prepare_parameters_for_docs(
    service_cls: Type[Service],
    exclude: tuple[str, ...] = (),
    only: tuple[str, ...] = (),
    path_parameters: tuple[str, ...] = (),
    default_location: Literal["query", "path"] = "query",
) -> list[OpenApiParameter]:

    parameter_data: dict[str, Any] = dict()

    parameters_list: list[OpenApiParameter] = list()

    fields_to_parameters: dict[str, Union[forms.Field, SimpleArrayField]] = (
        get_dict_of_fields_for_parameters(service_cls, exclude, only)
    )

    for attr_name, attr in fields_to_parameters.items():
        parameter_data["name"] = attr_name
        parameter_data["required"] = attr.required

        if attr_name in path_parameters:
            parameter_data["location"] = PARAMETER_LOCATION_MAPPER["path"]
        else:
            parameter_data["location"] = PARAMETER_LOCATION_MAPPER[default_location]

        if attr_name in SPECIAL_DESCRIPTIONS.keys():
            parameter_data["description"] = SPECIAL_DESCRIPTIONS[attr_name]
        else:
            parameter_data["description"] = attr.help_text

        parameter_type, choices = determine_parameter_type(attr)
        parameter_data["type"] = parameter_type
        if type(attr) in MULTIPLE_CHOICE_FIELDS or type(attr) in ARRAY_FORMS_FIELDS:
            parameter_data["many"] = True

        if isinstance(attr, SimpleArrayField):
            parameter_data["type"]["items"] = OPENAPI_TYPE_MAPPING[
                parameter_data["type"]["items"]["type"]
            ]
            parameter_data["many"] = True
            if choices:
                parameter_data["description"] += f" One or several of: {choices}"
        else:
            if choices:
                parameter_data["enum"] = choices
        parameters_list.append(OpenApiParameter(**parameter_data))
        parameter_data = dict()
    return parameters_list


def get_dict_of_fields_for_parameters(
    service_cls: Type[Service],
    exclude: tuple[str, ...] = (),
    only: tuple[str, ...] = (),
) -> dict[str, Union[forms.Field, SimpleArrayField]]:
    """
    Filter all fields given in Service object with respect to
    'exclude' and 'only' parameters
    """

    if all([exclude, only]):
        raise AttributeError(
            "It is prohibited to set 'exclude' and 'only' simultaneously"
        )

    fields_to_parameters: dict[str, Union[forms.Field, SimpleArrayField]] = dict()

    if only:
        for field_name in only:
            try:
                fields_to_parameters[field_name] = service_cls.declared_fields[
                    field_name
                ]
            except KeyError:
                logger.info(
                    f"""Field with name '{field_name}' was not added to auto parameters generation
                 because this field is not present in service '{service_cls.__name__}'"""
                )
    else:
        fields_to_parameters.update(service_cls.declared_fields)

    for field_name in exclude:
        try:
            del fields_to_parameters[field_name]
        except KeyError:
            logger.info(
                f"""Field with name '{field_name}' was not excluded from auto parameters generation
             because this field is not present in service '{service_cls.__name__}'"""
            )

    return fields_to_parameters


def determine_parameter_type(
    field_obj: Union[Type[forms.Field], SimpleArrayField]
) -> tuple[Union[Type[OpenApiTypes], dict], Union[list, None]]:
    """
    Most of the form's fields can be simply cast into OpenApiParameter types by
    using the FIELDS_PARAMETERS_MAPPER defined above.
    Special cases are as follows:
    1) ChoiceFields (see CHOICE_FIELDS list above), which type can be determined by the type of provided
    choices values; we suppose here, that all values in choices must be of the same type.
    2) MultipleChoiceFields (MULTIPLE_CHOICE_FIELDS above), which type basically corresponds to 'array';
    for now we suppose, that this array might include elements of a different types
    3) MultiValueFields (and particular case forms.SplitDateTimeField) - here a list of values
    of different types can be provided, allowed types are specified in 'fields' parameter
    4) SimpleArrayField, which type can be got by respective base_field's type
    5) forms.ComboField can accept a single value, but this value can be one of types,
    provided with 'fields' parameter

    :param field_obj: field for which we need to determine an OpenApi type
    :return: (parameter_type, choices) - tuple with OpenApi type and optional choices
    """

    choices: Union[list, None] = None
    if type(field_obj) in CHOICE_FIELDS:
        if getattr(field_obj, "_choices", None):
            choices = [choice[0] for choice in field_obj._choices]
            choices_types: list[Type[OpenApiTypes]] = determine_choices_types(choices)
            if len(choices_types) == 1:
                parameter_type: Union[Type[OpenApiTypes], dict] = choices_types[0]
            else:
                raise ValueError("""Provided choices are of different types!""")
        else:
            raise AttributeError(
                f"You have to provide choices for '{field_obj.label}' field"
            )
    elif type(field_obj) in MULTIPLE_CHOICE_FIELDS:
        if getattr(field_obj, "_choices", None):
            choices = [choice[0] for choice in field_obj._choices]
            choices_types = determine_choices_types(choices)
            if len(choices_types) == 1:
                parameter_type = choices_types[0]
            else:
                parameter_type = {
                    "type": "array",
                    "items": {
                        "type": "/".join(
                            [choice_type.name for choice_type in choices_types]
                        )
                    },
                }
        else:
            raise AttributeError(
                f"You have to provide choices for '{field_obj.label}' field"
            )
    elif type(field_obj) in ARRAY_FORMS_FIELDS:
        array_choices_types: list[Union[Type[OpenApiTypes], dict]] = list()
        for field in field_obj.fields:
            array_choices_types.append(determine_parameter_type(field)[0])
        if len(array_choices_types) == 1:
            parameter_type = array_choices_types[0]
        else:
            array_items_types: list[str] = list()
            for choice_type in array_choices_types:
                if type(choice_type) is OpenApiTypes:
                    array_items_types.append(choice_type.name)
                else:
                    if choice_type["type"] == "array":
                        array_items_types += [
                            item_type["type"] for item_type in choice_type["items"]
                        ]
                    else:
                        array_items_types.append(choice_type["type"])
            parameter_type = {
                "type": "array",
                "items": {"type": "/".join(array_items_types)},
            }
    elif isinstance(field_obj, SimpleArrayField):
        parameter_type = {
            "type": "array",
            "min_items": field_obj.min_length,
            "max_items": field_obj.max_length,
            "items": {"type": determine_parameter_type(field_obj.base_field)[0]},
        }  # add anyOf / oneOf if we have choices
    elif isinstance(field_obj, forms.ComboField):
        array_choices_types = list()
        for field in field_obj.fields:
            array_choices_types.append(determine_parameter_type(field)[0])
        array_items_types = list()
        for choice_type in array_choices_types:
            if type(choice_type) is OpenApiTypes:
                array_items_types.append(choice_type.name)
            else:
                if choice_type["type"] == "array":
                    array_items_types += [
                        item_type["type"] for item_type in choice_type["items"]
                    ]
                else:
                    array_items_types.append(choice_type["type"])
        parameter_type = {
            "type": "AnyValue",
            "items": {"type": "/".join(array_items_types)},
        }
    else:
        try:
            parameter_type = FIELDS_PARAMETERS_MAPPER[type(field_obj)]
        except KeyError:
            raise NotImplementedError(
                f"Please, add {type(field_obj)} field type to the mapper"
            )
    return parameter_type, choices


def determine_choices_types(choices: list[Any]) -> list[Type[OpenApiTypes]]:
    python_types: set[type] = determine_list_elements_python_types(choices)
    openapi_types: set[Type[OpenApiTypes]] = set()
    for elem in python_types:
        try:
            openapi_types.add(PYTHON_TYPE_MAPPING[elem])
        except KeyError:
            raise NotImplementedError(
                f"Type of the provided choices '{elem}' is not currently supported"
            )
    return list(openapi_types)


def determine_list_elements_python_types(list_of_elements: list[Any]) -> set[type]:
    elements_types: set[type] = set()
    for elem in list_of_elements:
        elements_types.add(type(elem))
    return elements_types


def prepare_request_body_for_docs(
    service_cls: Type[Service],
    exclude: Tuple[str, ...] = (),
    body_data_types: tuple[str, ...] = ("application/json",),
) -> dict:

    fields_to_parameters = get_dict_of_fields_for_parameters(service_cls, exclude)
    required_parameters_set: set = set()
    request_body: dict = dict()

    for data_type in body_data_types:
        request_body[data_type] = {
            "type": "object",
            "properties": {},
        }

        for attr_name, attr in fields_to_parameters.items():
            raw_parameter_type: Union[Type[OpenApiTypes], dict] = (
                determine_parameter_type(attr)[0]
            )
            if type(raw_parameter_type) is OpenApiTypes:
                parameter_type = OPENAPI_TYPE_MAPPING[raw_parameter_type]
            else:
                if "items" in raw_parameter_type.keys():
                    parameter_type = raw_parameter_type
                    parameter_type["items"] = OPENAPI_TYPE_MAPPING[
                        raw_parameter_type["items"]["type"]
                    ]
                else:
                    parameter_type = raw_parameter_type["type"]

            request_body[data_type]["properties"][attr_name] = parameter_type
            # if attr_name == "role":
            #     request_body[data_type]["properties"][attr_name]['enum'] = ['Change', 'Read']
            if attr.required:
                required_parameters_set.add(attr_name)
        request_body[data_type]["required"] = list(required_parameters_set)
    return request_body

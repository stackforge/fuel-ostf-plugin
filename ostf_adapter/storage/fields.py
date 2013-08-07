import json

from sqlalchemy.types import TypeDecorator, VARCHAR


class JsonField(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class ListField(JsonField):
    def process_bind_param(self, value, dialect):
        value = list(value) if value else []
        super(ListField, self).process_bind_param(value, dialect)


    def process_result_value(self, value, dialect):
        value = super(ListField, self).process_bind_param(value, dialect)
        return list(value) if value else []
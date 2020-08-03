from drf_yasg.inspectors import SwaggerAutoSchema


class NameAsOperationIDAutoSchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys):
        operation_id = super(NameAsOperationIDAutoSchema, self).get_operation_id(operation_keys)
        # print(operation_id, operation_keys)
        # operation_id = operation_keys[len(operation_keys) - 2]
        operation_id = operation_id.replace('_create', '_query')
        operation_id = operation_id.replace('_list', '_get')
        return operation_id
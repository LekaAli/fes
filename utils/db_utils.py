from models.users import User
from models.transactions import db


def perform_db_operation(model_cls_name, data=None, operation="add"):
    if isinstance(model_cls_name, type) and issubclass(model_cls_name, User):
        password = data.pop("password")
        model_instance = model_cls_name(**data)
        model_instance.set_password(password)
    else:
        if operation not in ["update", "delete"]:
            model_instance = model_cls_name(**data)
        else:
            model_instance = model_cls_name

    if operation == "add":
        db.session.add(model_instance)
    elif operation == "delete":
        db.session.delete(model_instance)
    elif operation == "update":
        for field_name, field_value in data.items():
            setattr(model_instance, field_name, field_value)
    db.session.commit()

from functools import wraps
from flask import Flask, jsonify, request, abort
from json_validator import (
    JSONValidator,
    IntValidator,
    FloatValidator,
    BooleanValidator,
    StringValidator,
    ArrayValidator,
    ArrayOfValidator
)

app = Flask(__name__)

def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON."""
    handle_http_exception = app.handle_http_exception
    @wraps(handle_http_exception)
    def ret_val(exception):
        exc = handle_http_exception(exception)    
        return jsonify({'code':exc.code, 'message':exc.description}), exc.code
    return ret_val


# Override the HTTP exception handler.
app.handle_http_exception = get_http_exception_handler(app)

def args_check(validator):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not validator.validate(request.json):
                return abort(400)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class JSONCheck(JSONValidator):
    validators = {
        "name"    : StringValidator(max=15, min=2, nullable=False),
        "age"     : IntValidator(min=13, nullable=False),
        "hobbies" : ArrayOfValidator(validator=StringValidator(min=2,max=15, nullable=False))
    }


users = []


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/users", methods=["POST"])
@args_check(JSONCheck())
def add_user():
    global users
    
    user = dict(
        name=request.json.get("name"),
        age=request.json.get("age"),
        hobbies=request.json.get("hobbies")
    )
    users.append(user)
    return jsonify(user)

if __name__ == "__main__":
    app.run(debug=True)
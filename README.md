# flask_jsonvalidator

**flask_jsonvalidator** is a library for validating request JSON data or pratically any json data, such as those obtained from external services or command-line parsing, converted in JSON format.

# Example

Here is a quick example to using `flask_jsonvalidator`, validating a request JSON data:\

**All neccessary imports**
```python
from flask_jsonvalidator import (
    JSONValidator,
    IntValidator,
    StringValidator,
    ArrayOfValidator
)
```

**A simple validator class**

```python
class JSONCheck(JSONValidator):
    validators = {
        "name"    : StringValidator(max=15, min=2, nullable=False),
        "age"     : IntValidator(min=13, nullable=False),
        "hobbies" : ArrayOfValidator(validator=StringValidator(min=2,max=15, nullable=False))
    }
```

#### A simple decorator for the JSON data check 

```python
from functools import wraps
from flask import request, abort

def args_check(validator):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not validator.validate(request.json):
                return abort(400)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

#### Use case

```python
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

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
    
```

See [full code](https://github.com/keosariel/flask_jsonvalidator/blob/main/app.py)

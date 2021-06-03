Flask JSONvalidator
====

**Flask_jsonvalidator** is a little library for validating request JSON data or pratically any json data, such as those obtained from external services or command-line parsing or even JSON data from a request to your api. All errors would be returned in JSON format too.

Installing
----------
Install and update using `pip` :

.. code-block:: text

    $ pip install flask-jsonvalidator

..
Example
-------
Here is a quick example to using `flask_jsonvalidator`, validating a request JSON data:\

**All neccessary imports**

.. code-block:: python
    
    # validators.py
    
    from flask_jsonvalidator import (
        JSONValidator,
        IntValidator,
        StringValidator,
        ArrayOfValidator
    )

**A simple validator class**

.. code-block:: python

    # validators.py

    class JSONCheck(JSONValidator):
        validators = {
            "name"    : StringValidator(max=15, min=2, nullable=False),
            "age"     : IntValidator(min=13, nullable=False),
            "hobbies" : ArrayOfValidator(validator=StringValidator(min=2,max=15, nullable=False))
        }

A simple decorator for the JSON data check 
------------------------------------------
.. code-block:: python

    from functools import wraps
    from flask import request, abort, jsonify
    
    def response_data(data, error_code=None, description="", error_data=None, status_code=200):
        data = data
        has_error   = True if error_code else False

        if not description:
                # ERRORS_DESCRIPTION is a Dictionary containing error-codes as keys and their 
                # description as the value

            description = ERRORS_DESCRIPTION.get(error_code,"")

        if has_error and error_code:
                # ERRORS_STATUS_CODE is a Dictionary containing error-codes as keys and their 
                # corresponding status code as the value

            status_code = ERRORS_STATUS_CODE.get(error_code, BAD_REQUEST)

        ret_json = {
            "data" : data,
            "error_code"  : error_code,
            "has_error"   : has_error,
            "description" : description,
            "error_data"  : error_data,
            "status_code" : status_code
        }

        return jsonify(ret_json), status_code

    def args_check(validator):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                json_data = request.json if request.json else {}
                no_err, msg = validator.validate(json_data)

                if not no_err:
                    # E002 = Invalid Request JSON
                    res = response_data(
                        data=None, 
                        error_code=E002,
                        error_data=msg
                    )

                    return res

                return f(*args, **kwargs)
            return decorated_function
        return decorator

Use case
--------
.. code-block:: python

    from flask import (
        Flask, 
        jsonify, 
        request, 
        abort
    )
    from validators import JSONCheck

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
            name   = request.json.get("name"),
            age    = request.json.get("age"),
            hobbies= request.json.get("hobbies")
        )
        users.append(user)
        return jsonify(user)

    if __name__ == "__main__":
        app.run(debug=True)


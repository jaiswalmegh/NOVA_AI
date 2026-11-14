
import copy
import inspect
import threading
import time


class ToolRegistry:

    def __init__(self):

        self.tools = {}
        self._lock = threading.RLock()

    # =========================================
    # REGISTER TOOL
    # =========================================

    def register_tool(
        self,
        name,
        function,
        description="",
        parameters=None
    ):

        if not isinstance(name, str) or not name.strip():
            return False

        if not callable(function):
            return False

        name = name.strip().lower()

        if not name.replace("_", "").isalnum():
            return False

        if not isinstance(description, str):
            return False

        if parameters is None:
            parameters = {
                "type": "object",
                "properties": {}
            }

        if not isinstance(parameters, dict):
            return False

        if parameters.get("type", "object") != "object":
            return False

        properties = parameters.get("properties", {})
        required = parameters.get("required", [])

        if not isinstance(properties, dict):
            return False

        if not isinstance(required, list):
            return False

        if any(key not in properties for key in required):
            return False

        with self._lock:

            if name in self.tools:
                return False

            self.tools[name] = {
                "name": name,
                "function": function,
                "description": description.strip(),
                "parameters": copy.deepcopy(parameters)
            }

        return True

    # =========================================
    # UNREGISTER TOOL
    # =========================================

    def unregister_tool(self, name):

        if not isinstance(name, str):
            return False

        name = name.strip().lower()

        with self._lock:

            if name not in self.tools:
                return False

            del self.tools[name]

        return True

    # =========================================
    # GET TOOL
    # =========================================

    def get_tool(self, name):

        if not isinstance(name, str):
            return None

        with self._lock:

            tool = self.tools.get(name.strip().lower())

            if tool is None:
                return None

            return {
                "name": tool["name"],
                "function": tool["function"],
                "description": tool["description"],
                "parameters": copy.deepcopy(tool["parameters"])
            }

    # =========================================
    # GET ALL TOOLS
    # =========================================

    def get_all_tools(self):

        with self._lock:

            return [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": copy.deepcopy(
                        tool["parameters"]
                    )
                }
                for tool in self.tools.values()
            ]

    # =========================================
    # TOOL INFORMATION
    # =========================================

    def get_tool_names(self):

        with self._lock:
            return list(self.tools.keys())

    def get_tool_count(self):

        with self._lock:
            return len(self.tools)

    def has_tool(self, name):

        if not isinstance(name, str):
            return False

        with self._lock:
            return name.strip().lower() in self.tools

    # =========================================
    # TYPE VALIDATION
    # =========================================

    def _check_type(self, value, expected):

        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }

        if expected == "null":
            return value is None

        expected_type = type_map.get(expected)

        if expected_type is None:
            return True

        if expected in ("integer", "number"):
            if isinstance(value, bool):
                return False

        return isinstance(value, expected_type)

    # =========================================
    # PROPERTY VALIDATION
    # =========================================

    def _validate_property(self, key, value, schema):

        if not isinstance(schema, dict):
            return False, f"Invalid schema for parameter '{key}'."

        expected = schema.get("type")

        if expected:

            if isinstance(expected, list):

                valid_type = any(
                    self._check_type(value, item)
                    for item in expected
                )

            else:

                valid_type = self._check_type(
                    value,
                    expected
                )

            if not valid_type:

                return False, (
                    f"Parameter '{key}' has an invalid type. "
                    f"Expected {expected}."
                )

        # Enum validation
        allowed_values = schema.get("enum")

        if (
            allowed_values is not None
            and value not in allowed_values
        ):

            return False, (
                f"Parameter '{key}' must be one of: "
                f"{allowed_values}"
            )

        # String validation
        if isinstance(value, str):

            min_length = schema.get("minLength")
            max_length = schema.get("maxLength")

            if min_length is not None and len(value) < min_length:
                return False, f"Parameter '{key}' is too short."

            if max_length is not None and len(value) > max_length:
                return False, f"Parameter '{key}' is too long."

        # Number validation
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        ):

            minimum = schema.get("minimum")
            maximum = schema.get("maximum")

            if minimum is not None and value < minimum:
                return False, f"Parameter '{key}' is below the minimum."

            if maximum is not None and value > maximum:
                return False, f"Parameter '{key}' exceeds the maximum."

        # Array validation
        if isinstance(value, list):

            min_items = schema.get("minItems")
            max_items = schema.get("maxItems")

            if min_items is not None and len(value) < min_items:
                return False, f"Parameter '{key}' has too few items."

            if max_items is not None and len(value) > max_items:
                return False, f"Parameter '{key}' has too many items."

        return True, None

    # =========================================
    # ARGUMENT VALIDATION
    # =========================================

    def _validate_arguments(self, tool, arguments):

        parameters = tool["parameters"]

        if not isinstance(arguments, dict):
            return False, "Tool arguments must be a dictionary."

        properties = parameters.get("properties", {})
        required = parameters.get("required", [])

        if not isinstance(properties, dict):
            return False, "Invalid tool parameter configuration."

        if not isinstance(required, list):
            return False, "Invalid required parameter configuration."

        # Required parameters
        for key in required:

            if key not in arguments:

                return False, (
                    f"Missing required parameter: {key}"
                )

        # Unexpected parameters
        allow_extra = parameters.get(
            "additionalProperties",
            False
        )

        if allow_extra is False:

            unexpected = set(arguments) - set(properties)

            if unexpected:

                return False, (
                    "Unexpected parameters: "
                    + ", ".join(sorted(unexpected))
                )

        # Validate each supplied parameter
        for key, value in arguments.items():

            if key not in properties:
                continue

            valid, error = self._validate_property(
                key,
                value,
                properties[key]
            )

            if not valid:
                return False, error

        return True, None

    # =========================================
    # EXECUTE TOOL
    # =========================================

    def execute_tool(self, name, arguments=None):

        tool = self.get_tool(name)

        if tool is None:

            return {
                "success": False,
                "message": "Requested tool is not registered.",
                "result": None,
                "execution_time": 0
            }

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):

            return {
                "success": False,
                "message": "Tool arguments must be a dictionary.",
                "result": None,
                "execution_time": 0
            }

        valid, error_message = self._validate_arguments(
            tool,
            arguments
        )

        if not valid:

            return {
                "success": False,
                "message": error_message,
                "result": None,
                "execution_time": 0
            }

        start_time = time.perf_counter()

        try:

            function = tool["function"]

            signature = inspect.signature(function)

            signature.bind(**arguments)

            result = function(**arguments)

            execution_time = round(
                time.perf_counter() - start_time,
                4
            )

            return {
                "success": True,
                "message": "Tool executed successfully.",
                "result": result,
                "execution_time": execution_time
            }

        except TypeError as error:

            return {
                "success": False,
                "message": f"Invalid tool arguments: {error}",
                "result": None,
                "execution_time": round(
                    time.perf_counter() - start_time,
                    4
                )
            }

        except Exception as error:

            execution_time = round(
                time.perf_counter() - start_time,
                4
            )

            print(f"Tool Execution Error: {error}")

            return {
                "success": False,
                "message": str(error),
                "result": None,
                "execution_time": execution_time
            }

    # =========================================
    # CLEAR REGISTRY
    # =========================================

    def clear_registry(self):

        with self._lock:
            self.tools.clear()

        return True

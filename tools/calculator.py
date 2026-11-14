
import ast
import math
import operator


class Calculator:

    MAX_EXPRESSION_LENGTH = 300
    MAX_EXPONENT = 1000
    MAX_RESULT_SIZE = 10**100

    def __init__(self):

        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.UAdd: operator.pos,
            ast.USub: operator.neg
        }

        self.functions = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "exp": math.exp,
            "factorial": math.factorial,
            "ceil": math.ceil,
            "floor": math.floor,
            "fabs": math.fabs,
            "abs": abs,
            "degrees": math.degrees,
            "radians": math.radians
        }

        self.constants = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau
        }

    def calculate(self, expression):

        if not isinstance(expression, str) or not expression.strip():

            return {
                "success": False,
                "result": None,
                "message": "Please provide a mathematical expression."
            }

        expression = expression.strip()

        if len(expression) > self.MAX_EXPRESSION_LENGTH:

            return {
                "success": False,
                "result": None,
                "message": "Expression is too long."
            }

        try:

            tree = ast.parse(expression, mode="eval")

            result = self._evaluate(tree.body)

            if isinstance(result, bool):
                raise ValueError("Boolean results are not allowed.")

            if not isinstance(result, (int, float)):
                raise ValueError("Invalid calculation result.")

            if not math.isfinite(result):
                raise ValueError("Result is not finite.")

            if abs(result) > self.MAX_RESULT_SIZE:
                raise ValueError("Result exceeds the allowed limit.")

            return {
                "success": True,
                "result": result,
                "message": f"Result: {result}"
            }

        except ZeroDivisionError:

            message = "Division by zero is not allowed."

        except OverflowError:

            message = "The calculation result is too large."

        except (ValueError, TypeError):

            message = "Invalid mathematical operation or arguments."

        except (SyntaxError, KeyError):

            message = "Invalid mathematical expression."

        except Exception as error:

            print(f"Calculator Error: {error}")
            message = "Could not process this calculation."

        return {
            "success": False,
            "result": None,
            "message": message
        }

    def _evaluate(self, node):

        if isinstance(node, ast.Constant):

            if isinstance(node.value, bool):
                raise ValueError("Boolean values are not allowed.")

            if isinstance(node.value, (int, float)):

                if abs(node.value) > self.MAX_RESULT_SIZE:
                    raise ValueError("Number exceeds the allowed limit.")

                return node.value

            raise ValueError("Invalid constant.")

        if isinstance(node, ast.BinOp):

            operation = self.operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported operator.")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow):

                if abs(right) > self.MAX_EXPONENT:
                    raise ValueError("Exponent is too large.")

                if abs(left) > 1 and right > 100:
                    raise ValueError("Calculation exceeds the allowed limit.")

            result = operation(left, right)

            if isinstance(result, (int, float)):

                if abs(result) > self.MAX_RESULT_SIZE:
                    raise ValueError("Result exceeds the allowed limit.")

            return result

        if isinstance(node, ast.UnaryOp):

            operation = self.operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported unary operator.")

            return operation(self._evaluate(node.operand))

        if isinstance(node, ast.Name):

            if node.id in self.constants:
                return self.constants[node.id]

            raise ValueError("Unknown mathematical constant.")

        if isinstance(node, ast.Call):

            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function.")

            function = self.functions.get(node.func.id)

            if function is None or node.keywords:
                raise ValueError("Unsupported function.")

            arguments = [
                self._evaluate(argument)
                for argument in node.args
            ]

            if function is math.factorial:

                if len(arguments) != 1:
                    raise ValueError("Factorial requires one argument.")

                number = arguments[0]

                if not isinstance(number, int) or number < 0 or number > 1000:
                    raise ValueError("Invalid factorial argument.")

            result = function(*arguments)

            return result

        raise ValueError("Unsupported expression.")

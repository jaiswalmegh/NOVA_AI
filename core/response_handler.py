
class ResponseHandler:

    def __init__(self):
        self.last_response = ""

    def process_response(self, response):
        if response is None:
            return "I couldn't generate a response."

        if not isinstance(response, str):
            response = str(response)

        response = response.strip()

        if not response:
            return "I couldn't generate a response."

        self.last_response = response
        return response

    def process(self, response):
        return self.process_response(response)

    def get_last_response(self):
        return self.last_response

    def clear_last_response(self):
        self.last_response = ""

    def format_error(self, error):
        print(f"NOVA Error: {error}")

        return (
            "Something went wrong while processing your request. "
            "Please try again."
        )

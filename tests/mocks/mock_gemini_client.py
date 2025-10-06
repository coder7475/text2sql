from unittest.mock import Mock

class MockGeminiClient:
    """
    A mock Gemini API client that simulates `client.models.generate_content`.
    """

    def __init__(self, fake_response_text="SELECT * FROM cities;"):
        # Create a mock response object with `.text`
        self.fake_response = Mock()
        self.fake_response.text = fake_response_text

        # Mock the models attribute
        self.models = Mock()
        self.models.generate_content = Mock(return_value=self.fake_response)

    def set_response(self, text):
        """Change the mock response text dynamically."""
        self.fake_response.text = text
        self.models.generate_content.return_value = self.fake_response

    def set_exception(self, exception):
        """Make generate_content raise an exception."""
        self.models.generate_content.side_effect = exception

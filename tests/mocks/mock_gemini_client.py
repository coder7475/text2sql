from unittest.mock import Mock

class MockGeminiClient:
    """
    A mock Gemini API client that simulates `client.models.generate_content`.
    """

    def __init__(self, fake_response_text="SELECT * FROM cities;"):
        # Create a mock response object with `.text`
        """
        Initialize the mock Gemini client with a configurable fake response text.
        
        Creates `self.fake_response` (a Mock whose `.text` is set to `fake_response_text`) and `self.models` (a Mock) where `self.models.generate_content` returns the `fake_response`.
        
        Parameters:
            fake_response_text (str): Initial value for the mock response's `.text`. Defaults to "SELECT * FROM cities;".
        """
        self.fake_response = Mock()
        self.fake_response.text = fake_response_text

        # Mock the models attribute
        self.models = Mock()
        self.models.generate_content = Mock(return_value=self.fake_response)

    def set_response(self, text):
        """
        Update the mock response text and ensure future generate_content calls return it.
        
        Parameters:
            text (str): New value to set on the mock response's `text` attribute.
        """
        self.fake_response.text = text
        self.models.generate_content.return_value = self.fake_response

    def set_exception(self, exception):
        """
        Configure the mock so `models.generate_content` raises the given exception when called.
        
        Parameters:
            exception (Exception or callable): The exception instance or callable to be used as `side_effect` for `models.generate_content`.
        """
        self.models.generate_content.side_effect = exception
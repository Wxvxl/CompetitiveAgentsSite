import unittest
import json
from app import app   # imports the Flask app object

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_agents(self):
        response = self.app.get('/agents/group1')
        
        self.assertEqual(response.status_code, 200) # Status OK

        data = json.loads(response.data.decode())
        print("Response JSON:", data)

        self.assertIsInstance(data, list) 

if __name__ == '__main__':
    unittest.main()
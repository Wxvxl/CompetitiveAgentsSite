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
        
    def test_group_vs_testing(self):
        # /play/run_tests/<groupname>/<game>
        response = self.app.get('/play/run_tests/group1/conn4')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode())
        print("Play Response JSON:", data)

        # Verify structure
        self.assertIn("group", data)
        self.assertIn("agent", data)
        self.assertIn("matches", data)
        self.assertIsInstance(data["matches"], list)

if __name__ == '__main__':
    unittest.main()
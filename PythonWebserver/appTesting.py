import unittest
import json
from app import app   # imports the Flask app object

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
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

    def test_group_vs_group(self):
        # /play/group_vs_group/<group1>/<group2>/<game>
        response = self.app.get('/play/group_vs_group/group1/group2/conn4')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode())
        print("Group vs Group Response JSON:", data)

        # Verify structure
        self.assertIn("group1", data)
        self.assertIn("group2", data)
        self.assertIn("winner", data)

        self.assertIn("name", data["group1"])
        self.assertIn("agent", data["group1"])
        self.assertIn("name", data["group2"])
        self.assertIn("agent", data["group2"])

if __name__ == '__main__':
    unittest.main()
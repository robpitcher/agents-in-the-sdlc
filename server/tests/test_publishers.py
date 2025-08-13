import unittest
import json
from flask import Flask
from models import Publisher, db, init_db
from routes.publishers import publishers_bp

class TestPublishersRoutes(unittest.TestCase):
    # Test data
    TEST_PUBLISHERS = [
        {"name": "DevGames Inc"},
        {"name": "Scrum Masters"}
    ]
    
    # API paths
    PUBLISHERS_API_PATH = '/api/publishers'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.app.register_blueprint(publishers_bp)
        self.client = self.app.test_client()
        
        init_db(self.app, testing=True)
        
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        publishers = [Publisher(**data) for data in self.TEST_PUBLISHERS]
        db.session.add_all(publishers)
        db.session.commit()

    def test_get_publishers_success(self) -> None:
        """Test successful retrieval of publishers"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_PUBLISHERS))
        
        for i, publisher in enumerate(data):
            self.assertEqual(publisher['name'], self.TEST_PUBLISHERS[i]['name'])
            self.assertIn('id', publisher)

    def test_get_publishers_structure(self) -> None:
        """Test the response structure for publishers"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        
        required_fields = ['id', 'name']
        for field in required_fields:
            self.assertIn(field, data[0])

if __name__ == '__main__':
    unittest.main()

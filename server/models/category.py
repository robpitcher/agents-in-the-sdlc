from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Category(BaseModel):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one category has many games
    games = relationship("Game", back_populates="category")
    
    @validates('name')
    def validate_name(self, key, name):
        """
        Validate the category name field.
        
        Args:
            key (str): The field name being validated
            name (str): The category name value to validate
            
        Returns:
            str: The validated category name
            
        Raises:
            ValueError: If name is invalid (too short, empty, or wrong type)
        """
        return self.validate_string_length('Category name', name, min_length=2)
        
    @validates('description')
    def validate_description(self, key, description):
        """
        Validate the category description field.
        
        Args:
            key (str): The field name being validated
            description (str): The description value to validate
            
        Returns:
            str: The validated description
            
        Raises:
            ValueError: If description is invalid (too short when provided)
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)
    
    def __repr__(self):
        """
        Return a string representation of the Category object.
        
        Returns:
            str: String representation showing category name
        """
        return f'<Category {self.name}>'
        
    def to_dict(self):
        """
        Convert the Category object to a dictionary representation.
        
        Returns:
            dict: Dictionary containing category data including game count
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }
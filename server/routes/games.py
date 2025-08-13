from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from sqlalchemy.exc import IntegrityError

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    """
    Create a base SQL query for games with joined publisher and category data.
    
    Returns:
        Query: SQLAlchemy query object with Game, Publisher, and Category joined
    """
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    """
    Get all games with their publisher and category information.
    
    Returns:
        Response: JSON response containing a list of all games with their details
    """
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    Returns:
        Response: JSON list of games matching the filter criteria
    """
    from flask import request
    
    
    # Start with base query
    games_query = get_games_base_query()
    
    # Apply category filter if provided
    category_id = request.args.get('category_id', type=int)
    if category_id is not None:
        games_query = games_query.filter(Game.category_id == category_id)
    
    # Apply publisher filter if provided
    publisher_id = request.args.get('publisher_id', type=int)
    if publisher_id is not None:
        games_query = games_query.filter(Game.publisher_id == publisher_id)
    
    # Execute query and convert results
    games_list = [game.to_dict() for game in games_query.all()]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    """
    Get a specific game by its ID with publisher and category information.
    
    Args:
        id (int): The unique identifier of the game
        
    Returns:
        tuple[Response, int] | Response: JSON response with game data, or 404 error if not found
    """
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    try:
        # Get JSON data from request
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate JSON data exists
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'category_id', 'publisher_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate publisher exists
        publisher = db.session.query(Publisher).filter(Publisher.id == data['publisher_id']).first()
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 400
        
        # Validate category exists
        category = db.session.query(Category).filter(Category.id == data['category_id']).first()
        if not category:
            return jsonify({"error": "Category not found"}), 400
        
        # Create new game
        new_game = Game(
            title=data['title'],
            description=data['description'],
            category_id=data['category_id'],
            publisher_id=data['publisher_id'],
            star_rating=data.get('star_rating')  # Optional field
        )
        
        # Add to database
        db.session.add(new_game)
        db.session.commit()
        
        # Return the created game with full details
        created_game = get_games_base_query().filter(Game.id == new_game.id).first()
        return jsonify(created_game.to_dict()), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int] | Response:
    try:
        # Find the game to update
        game = db.session.query(Game).filter(Game.id == id).first()
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Get JSON data from request
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate JSON data exists
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Update fields if provided
        if 'title' in data:
            game.title = data['title']
        
        if 'description' in data:
            game.description = data['description']
        
        if 'star_rating' in data:
            game.star_rating = data['star_rating']
        
        if 'publisher_id' in data:
            # Validate publisher exists
            publisher = db.session.query(Publisher).filter(Publisher.id == data['publisher_id']).first()
            if not publisher:
                return jsonify({"error": "Publisher not found"}), 400
            game.publisher_id = data['publisher_id']
        
        if 'category_id' in data:
            # Validate category exists
            category = db.session.query(Category).filter(Category.id == data['category_id']).first()
            if not category:
                return jsonify({"error": "Category not found"}), 400
            game.category_id = data['category_id']
        
        # Commit changes
        db.session.commit()
        
        # Return the updated game with full details
        updated_game = get_games_base_query().filter(Game.id == id).first()
        return jsonify(updated_game.to_dict())
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    try:
        # Find the game to delete
        game = db.session.query(Game).filter(Game.id == id).first()
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Delete the game
        db.session.delete(game)
        db.session.commit()
        
        return jsonify({"message": "Game deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

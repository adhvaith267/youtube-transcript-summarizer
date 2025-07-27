import logging
from flask import Flask
from services.gemini import configure_gemini
from routes.main import main_routes

def create_app():
    """
    Creates and configures a new Flask application.
    
    This function acts as an application factory. It initializes the Flask app,
    configures services like Gemini, registers the blueprints for routes,
    and sets up basic logging.
    
    Returns:
        The configured Flask app instance.
    """
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize Gemini API
    try:
        configure_gemini()
        logging.info("Gemini API configured successfully.")
    except ValueError as e:
        logging.critical(f"Failed to configure Gemini API: {e}")
        # In a real-world scenario, you might exit or handle this more gracefully
        # For this app, we'll let it raise the error to alert the user.
        raise

    # Create and configure the Flask app
    app = Flask(__name__)
    
    # Register the blueprint for the main routes
    app.register_blueprint(main_routes)
    
    return app

if __name__ == '__main__':
    # Create the app using the factory
    app = create_app()
    # Run the app in debug mode
    # For production, use a proper WSGI server like Gunicorn or Waitress
    app.run(debug=True)

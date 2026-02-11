from app import *
import os

if __name__ == "__main__":
    app = create_app()

    host = os.getenv("HOST")
    port = os.getenv("PORT")
    
    app.run(host=host, port=port)
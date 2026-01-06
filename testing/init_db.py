import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.database import engine, Base
# Import models so they are registered with Base.metadata
import src.data.models


print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done!")




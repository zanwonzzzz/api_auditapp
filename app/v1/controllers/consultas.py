from databases import Database
from dotenv import load_dotenv

load_dotenv()

database = Database(
    db_database = os.getenv('DB_DATABASE')
    db_host = os.getenv('DB_HOST')
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
)

await database.connect()

def consulta():
    query = "SELECT * FROM copes"
    rows = await database.fetch_all(query=query)
    return ('Copes:', rows)
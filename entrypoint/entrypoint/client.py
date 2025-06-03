from dotenv import load_dotenv
from globus_compute_sdk import Client

load_dotenv()
# assert "GLOBUS_COMPUTE_CLIENT_ID" in os.environ, "GLOBUS_COMPUTE_CLIENT_ID not set"
# assert "GLOBUS_COMPUTE_CLIENT_SECRET" in os.environ, "GLOBUS_COMPUTE_CLIENT_SECRET not set"


client = Client()

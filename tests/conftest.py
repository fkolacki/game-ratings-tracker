from dotenv import load_dotenv
import os

os.environ["ENV_FILE"] = ".env.test"
load_dotenv("../.env.test", override=True)
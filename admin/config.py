import dotenv
import yaml
from pathlib import Path
from passlib.handlers.sha2_crypt import sha512_crypt as crypto

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load yaml config
with open(config_dir / "config.yml", 'r') as f:
    config_yaml = yaml.safe_load(f)

# load .env config
config_env = dotenv.dotenv_values(config_dir / "config.env")

username = config_yaml["username"]
hashed_password = crypto.hash(config_yaml["password_for_user"])

mongodb_uri = f"mongodb://mongo:{config_env['MONGODB_PORT']}"

# from pydantic_settings import BaseSettings
# import json
# from pathlib import Path

# class Settings(BaseSettings):
#     court_base_url: str = "https://delhihighcourt.nic.in"
#     captcha_selector: str = "img#captcha"
#     selectors_file: Path = Path(__file__).parent / "selectors.json"

#     def load_selectors(self):
#         return json.loads(self.selectors_file.read_text())

# settings = Settings()

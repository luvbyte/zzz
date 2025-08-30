from typing import Optional, List, Literal
from pydantic import BaseModel, Field

# config.json
class ZzzCliModel(BaseModel):
  intro: bool = True
  clear: bool = False

class ZzzConfigModel(BaseModel):
  cli: ZzzCliModel = Field(default_factory=ZzzCliModel)

class ZzzScriptOptionsModel(BaseModel):
  require: list[str] = []
  precompile: bool = True

  platform: list[Literal["linux", "windows", "darwin"]] = []


from pydantic import BaseModel
from typing import Literal


class Capabilities(BaseModel):
    dom: bool
    ocr: bool
    vision: bool
    local_redaction: bool


class PrivacyPolicy(BaseModel):
    allow_remote_context: bool
    allow_images: bool
    allow_text: bool


class ClientRequest(BaseModel):
    client_version: str
    browser: Literal["chrome", "firefox", "safari", "edge"]
    capabilities: Capabilities
    privacy_policy: PrivacyPolicy
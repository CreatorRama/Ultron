from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from enum import Enum


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


# -------------------------------
# Observation API
# -------------------------------

class BBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class URLInfo(BaseModel):
    origin: str
    path: str


class Viewport(BaseModel):
    width: int
    height: int


class Page(BaseModel):
    title: str
    viewport: Viewport


class Element(BaseModel):
    id: str
    tag: str
    role: str
    label: Optional[str] = None
    value: Optional[str] = None
    bbox: BBox
    text: Optional[str] = None


class DOM(BaseModel):
    elements: List[Element]


class TextBlock(BaseModel):
    text: str
    bbox: BBox


class OCR(BaseModel):
    text_blocks: List[TextBlock]


class ImageData(BaseModel):
    format: str
    encoding: str
    sanitized: bool
    width: int
    height: int
    data: str


class DetectedType(str, Enum):
    EMAIL = "EMAIL"
    ACCOUNT = "ACCOUNT"
    PHONE = "PHONE"


class Privacy(BaseModel):
    redaction_applied: bool

    detected_types: List[DetectedType] = Field(
        min_length=1
    )

    redaction_count: int
    raw_context_discarded: bool


class ObservationRequest(BaseModel):
    observation_id: str
    url: URLInfo
    page: Page
    dom: DOM
    ocr: OCR

    
    image: Optional[ImageData] = None

    privacy: Privacy
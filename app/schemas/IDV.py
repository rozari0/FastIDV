from pydantic import BaseModel


class VerificationResult(BaseModel):
    verified: bool
    is_spoofed: bool

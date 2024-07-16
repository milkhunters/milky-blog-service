from dataclasses import dataclass


@dataclass
class PreSignedPostUrl:
    url: str
    fields: dict

from uuid import uuid4


class AttachmentHolder:

    def __init__(self) -> None:
        self.attachments = []

    def create_attachment(self, body, file_name, container_id, *args, **kwargs):
        self.attachments.append(body)
        return {"hash": str(uuid4()), "succeeded": True}

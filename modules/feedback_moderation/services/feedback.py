from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService
from app.core.serializer import serialize
from app.core.services import exposed_action
from app.core.context import get_current_user_id

class TagService(BaseService):
    from ..models.feedback import Tag

class SuggestionService(BaseService):
    from ..models.feedback import Suggestion

    def create(self, obj):  
        if not isinstance(obj, dict): return super().create(obj)
        payload = dict(obj)
        payload["status"] = "pending"
        payload["is_public"] = False
        return super().create(payload)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def publish(self, id: int, note: str | None = None, pin: bool = False) -> dict:
        rec = self.repo.session.get(self.Suggestion, int(id))
        if not rec: raise HTTPException(404, "Sugerencia no encontrada")
        rec.status = "published"
        rec.is_public = True
        rec.published_at = dt.datetime.now(dt.timezone.utc)
        rec.reviewed_by_id = get_current_user_id()
        if note: rec.moderation_note = note
        # Nota Senior: 'pin' podría guardarse en un campo futuro, por ahora lo recibimos.
        self.repo.session.add(rec)
        self.repo.session.commit()
        return serialize(rec)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reject(self, id: int, note: str) -> dict:
        rec = self.repo.session.get(self.Suggestion, int(id))
        if not rec: raise HTTPException(404, "Sugerencia no encontrada")
        rec.status = "rejected"
        rec.is_public = False
        rec.reviewed_by_id = get_current_user_id()
        rec.moderation_note = note
        self.repo.session.add(rec)
        self.repo.session.commit()
        return serialize(rec)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def merge(self, id: int, target_id: int, note: str | None = None) -> dict:
        if int(id) == int(target_id): raise HTTPException(400, "No puedes fusionar consigo misma")
        rec = self.repo.session.get(self.Suggestion, int(id))
        target = self.repo.session.get(self.Suggestion, int(target_id))
        if not rec or not target: raise HTTPException(404, "Sugerencias no encontradas")
        
        rec.status = "merged"
        rec.is_public = False
        rec.moderation_note = f"Fusionada con #{target_id}. {note or ''}".strip()
        self.repo.session.add(rec)
        self.repo.session.commit()
        return serialize(rec)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reopen(self, id: int) -> dict:
        rec = self.repo.session.get(self.Suggestion, int(id))
        if not rec: raise HTTPException(404, "No encontrada")
        rec.status = "pending"
        rec.is_public = False
        self.repo.session.add(rec)
        self.repo.session.commit()
        return serialize(rec)

class CommentService(BaseService):
    from ..models.feedback import Comment

    def create(self, obj):  # type: ignore[override]
        if not isinstance(obj, dict): return super().create(obj)
        payload = dict(obj)
        payload["status"] = "pending"
        payload["is_public"] = False
        return super().create(payload)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def publish_comment(self, id: int, note: str | None = None) -> dict:
        rec = self.repo.session.get(self.Comment, int(id))
        if not rec: raise HTTPException(404, "Comentario no encontrado")
        rec.status = "published"
        rec.is_public = True
        rec.published_at = dt.datetime.now(dt.timezone.utc)
        self.repo.session.add(rec)
        self.repo.session.commit()
        return serialize(rec)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reject_comment(self, id: int, note: str | None = None) -> dict:
        rec = self.repo.session.get(self.Comment, int(id))
        if not rec: raise HTTPException(404, "Comentario no encontrado")
        rec.status = "rejected"
        rec.is_public = False
        self.repo.session.add(rec)
        self.repo.session.commit()
        return serialize(rec)
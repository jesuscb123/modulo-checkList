from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService
from app.core.serializer import serialize
from app.core.services import exposed_action

class SessionService(BaseService):
    from ..models.events import Session

class EventService(BaseService):
    from ..models.events import Event

    def sanitize_dates(self, payload: dict) -> dict:
        import datetime as dt
        for date_field in ["start_at", "end_at"]:
            val = payload.get(date_field)
            if val and isinstance(val, str) and "/" in val:
                try:
                    parsed = dt.datetime.strptime(val.split()[0], "%d/%m/%Y")
                    payload[date_field] = parsed.replace(tzinfo=dt.timezone.utc)
                except ValueError:
                    pass 
        return payload

    def create(self, obj):  # type: ignore[override]
        if not isinstance(obj, dict):
            return super().create(obj)
        payload = self.sanitize_dates(dict(obj))
        return super().create(payload)

    def update(self, id: int, obj):  # type: ignore[override]
        if not isinstance(obj, dict):
            return super().update(id, obj)
        payload = self.sanitize_dates(dict(obj))
        return super().update(id, payload)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def publish_event(self, id: int, note: str | None = None) -> dict:
        event = self.repo.session.get(self.Event, int(id))
        if not event: raise HTTPException(404, "Evento no encontrado")
        
        event.status = "published"
        event.is_public = True
        self.repo.session.add(event)
        self.repo.session.commit()
        return serialize(event)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def close_registration(self, id: int, reason: str | None = None) -> dict:
        event = self.repo.session.get(self.Event, int(id))
        if not event: raise HTTPException(404, "Evento no encontrado")
        
        event.status = "closed"
        self.repo.session.add(event)
        self.repo.session.commit()
        return serialize(event)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def cancel_event(self, id: int, reason: str) -> dict:
        event = self.repo.session.get(self.Event, int(id))
        if not event: raise HTTPException(404, "Evento no encontrado")
        
        event.status = "cancelled"
        event.is_public = False
        self.repo.session.add(event)
        self.repo.session.commit()
        return serialize(event)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def reopen_event(self, id: int) -> dict:
        event = self.repo.session.get(self.Event, int(id))
        if not event: raise HTTPException(404, "Evento no encontrado")
        
        event.status = "published"
        event.is_public = True
        self.repo.session.add(event)
        self.repo.session.commit()
        return serialize(event)


class RegistrationService(BaseService):
    from ..models.events import Registration

    def create(self, obj): 
        """Interceptor: Asignamos la fecha de registro automáticamente."""
        if not isinstance(obj, dict): return super().create(obj)
        payload = dict(obj)
        payload["registered_at"] = dt.datetime.now(dt.timezone.utc)
        if "status" not in payload:
            payload["status"] = "pending"
        return super().create(payload)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def confirm(self, id: int, note: str | None = None) -> dict:
        reg = self.repo.session.get(self.Registration, int(id))
        if not reg: raise HTTPException(404, "Inscripción no encontrada")
        reg.status = "confirmed"
        if note: reg.notes = f"{reg.notes or ''} | {note}".strip()
        self.repo.session.add(reg)
        self.repo.session.commit()
        return serialize(reg)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def move_waitlist(self, id: int, note: str | None = None) -> dict:
        reg = self.repo.session.get(self.Registration, int(id))
        if not reg: raise HTTPException(404, "Inscripción no encontrada")
        reg.status = "waitlist"
        self.repo.session.add(reg)
        self.repo.session.commit()
        return serialize(reg)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def checkin(self, id: int, source: str = "manual") -> dict:
        reg = self.repo.session.get(self.Registration, int(id))
        if not reg: raise HTTPException(404, "Inscripción no encontrada")
        if reg.status not in ["confirmed", "pending"]:
            raise HTTPException(400, "Solo puedes hacer check-in a usuarios confirmados o pendientes.")
            
        reg.checkin_at = dt.datetime.now(dt.timezone.utc)
        reg.notes = f"{reg.notes or ''} [Checkin: {source}]".strip()
        self.repo.session.add(reg)
        self.repo.session.commit()
        return serialize(reg)
    
    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def bulk_checkin(self, ids: list[int]) -> dict:
        count = 0
        for reg_id in ids:
            reg = self.repo.session.get(self.Registration, int(reg_id))
            if reg and reg.status in ["confirmed", "pending"] and not reg.checkin_at:
                reg.checkin_at = dt.datetime.now(dt.timezone.utc)
                reg.notes = f"{reg.notes or ''} [Bulk Checkin]".strip()
                self.repo.session.add(reg)
                count += 1
        self.repo.session.commit()
        return {"message": f"{count} asistentes validados correctamente."}
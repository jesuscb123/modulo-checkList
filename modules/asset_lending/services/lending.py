from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService
from app.core.serializer import serialize
from app.core.services import exposed_action
from ..models.lending import Location, Asset, Loan

class LocationService(BaseService):
    from ..models.lending import Location

class AssetService(BaseService):
    from ..models.lending import Asset

    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def mark_maintenance(self, id: int, note: str | None = None) -> dict:
        asset = self.repo.session.get(Asset, int(id))
        if not asset: raise HTTPException(404, "Asset not found")
        asset.status = "maintenance"
        if note:
            asset.notes = f"{(asset.notes or '').strip()}\n[Mantenimiento]: {note}".strip()
        self.repo.session.add(asset)
        self.repo.session.commit()
        return serialize(asset)

    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def release_maintenance(self, id: int) -> dict:
        asset = self.repo.session.get(Asset, int(id))
        if not asset: raise HTTPException(404, "Asset not found")
        asset.status = "available"
        self.repo.session.add(asset)
        self.repo.session.commit()
        return serialize(asset)

class AssetLoanService(BaseService):
    from ..models.lending import Loan

    def create(self, obj): 

        if not isinstance(obj, dict):
            return super().create(obj)
            
        payload = dict(obj)
        asset_id = payload.get("asset_id")
        
        if not asset_id:
            raise HTTPException(400, "Se requiere especificar un recurso (asset_id)")

        due_at = payload.get("due_at")
        if due_at and isinstance(due_at, str):
            try:
    
                if "/" in due_at:
                    parsed_date = dt.datetime.strptime(due_at.split()[0], "%d/%m/%Y")
                    payload["due_at"] = parsed_date.replace(tzinfo=dt.timezone.utc)
            except ValueError:
                pass 

        asset = self.repo.session.get(Asset, int(asset_id))
        if not asset:
            raise HTTPException(404, "Recurso no encontrado")
        if asset.status != "available":
            raise HTTPException(400, f"El recurso no está disponible (Estado: {asset.status})")

        asset.status = "loaned"
        self.repo.session.add(asset)

        payload["status"] = "open"
        payload["checkout_at"] = dt.datetime.now(dt.timezone.utc)

        return super().create(payload)

    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def return_asset(self, id: int, note: str | None = None) -> dict:
        loan = self.repo.session.get(Loan, int(id))
        if not loan: raise HTTPException(404, "Loan not found")
        if loan.status != "open": raise HTTPException(400, "El préstamo no está abierto")
        
        loan.status = "returned"
        loan.returned_at = dt.datetime.now(dt.timezone.utc)
        if note: loan.return_note = note
        
    
        asset = self.repo.session.get(Asset, loan.asset_id)
        if asset: asset.status = "available"
        
        self.repo.session.add(loan)
        self.repo.session.add(asset)
        self.repo.session.commit()
        return serialize(loan)
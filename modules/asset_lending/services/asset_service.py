from datetime import datetime
from app.core.services import CRUDService as BaseService
from app.core.exceptions import ValidationError
from modules.asset_lending.models.asset import Asset
from modules.asset_lending.models.loan import AssetLoan

class AssetService(BaseService):
    __model__ = Asset

    def mark_maintenance(self, asset_id, note=""):
        asset = self.get(asset_id)
        asset.status = 'maintenance'
        asset.notes = note
        return self.save(asset)

    def release_maintenance(self, asset_id):
        asset = self.get(asset_id)
        if not asset:
            raise ValidationError("El recurso no existe.")
        if asset.status != 'maintenance':
            raise ValidationError("El recurso no está en mantenimiento.")
        asset.status = 'available'
        return self.save(asset)

class LoanService(BaseService):
    __model__ = AssetLoan

    def checkout(self, asset_id, borrower_id, due_at, note=""):
        # Usamos self.db para acceder a otros modelos si es necesario
        asset_service = AssetService(self.db)
        asset = asset_service.get(asset_id)
        
        if asset.status != 'available':
            raise ValidationError("El activo no está disponible.")

        loan_data = {
            "asset_id": asset_id,
            "borrower_user_id": borrower_id,
            "checkout_at": datetime.now(),
            "due_at": due_at,
            "status": "open",
            "checkout_note": note
        }
        loan = self.create(loan_data)

        asset.status = 'loaned'
        asset_service.save(asset)
        return loan

    def return_asset(self, loan_id, note=""):
        loan = self.get(loan_id)
        if loan.status != 'open':
            raise ValidationError("Este préstamo ya no está activo.")
        
        loan.returned_at = datetime.now()
        loan.status = 'returned'
        loan.return_note = note

        asset_service = AssetService(self.db)
        asset = asset_service.get(loan.asset_id)
        asset.status = 'available'
        
        self.save(loan)
        asset_service.save(asset)
        return True
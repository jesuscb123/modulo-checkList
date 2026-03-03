from __future__ import annotations
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UUID
from sqlalchemy.orm import backref, relationship
from app.core.base import Base
from app.core.fields import field

class Location(Base):
    __tablename__ = "asset_lending_location"
    __abstract__ = False
    __model__ = "location"
    __service__ = "modules.asset_lending.services.lending.LocationService"
    __selector_config__ = {
        "label_field": "name",
        "search_fields": ["name", "code"],
        "columns": [
            {"field": "name", "label": "Nombre"},
            {"field": "code", "label": "Código"},
        ],
    }

    name = field(String(100), required=True, public=True, editable=True)
    code = field(String(20), required=True, public=True, editable=True)
    is_active = field(Boolean, default=True, required=True, public=True, editable=True)

class Asset(Base):
    __tablename__ = "asset_lending_asset"
    __abstract__ = False
    __model__ = "asset"
    __service__ = "modules.asset_lending.services.lending.AssetService"
    
    __selector_config__ = {"label_field": "name", "columns": [{"field": "name", "label": "Recurso"}]}

    name = field(String(180), required=True, public=True, editable=True)
    asset_code = field(String(50), required=True, public=True, editable=True)
    status = field(
        String(20), required=True, default="available", public=True, editable=True,
        info={"choices": [
            {"label": "Disponible", "value": "available"},
            {"label": "Prestado", "value": "loaned"},
            {"label": "Mantenimiento", "value": "maintenance"}
        ]}
    )
    location_id = field(Integer, ForeignKey("asset_lending_location.id"), required=True, public=True, editable=True)
    responsible_user_id = field(UUID, ForeignKey("core_user.id"), required=False, public=True, editable=True)
    notes = field(Text, required=False, public=True, editable=True)

class Loan(Base):
    __tablename__ = "asset_lending_loan"
    __abstract__ = False
    __model__ = "loan"
    __service__ = "modules.asset_lending.services.lending.AssetLoanService"

    asset_id = field(Integer, ForeignKey("asset_lending_asset.id"), required=True, public=True, editable=True)
    borrower_user_id = field(UUID, ForeignKey("core_user.id"), required=True, public=True, editable=True)
    checkout_at = field(DateTime(timezone=True), required=False, public=True, editable=False)
    due_at = field(DateTime(timezone=True), required=True, public=True, editable=True)
    returned_at = field(DateTime(timezone=True), required=False, public=True, editable=False)
    status = field(
        String(20), required=True, default="open", public=True, editable=True,
        info={"choices": [
            {"label": "Abierto", "value": "open"},
            {"label": "Devuelto", "value": "returned"},
            {"label": "Atrasado", "value": "overdue"}
        ]}
    )
    checkout_note = field(Text, required=False, public=True, editable=True)
    return_note = field(Text, required=False, public=True, editable=True)
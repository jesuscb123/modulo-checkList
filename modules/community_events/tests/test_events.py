import pytest
import datetime as dt
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

# Importamos nuestros servicios y modelos
from modules.community_events.services.events import EventService, RegistrationService
from modules.community_events.models.events import Event, Registration

# --- FIXTURES (Preparación del entorno) ---

@pytest.fixture
def mock_event_service():
    """Crea un EventService con la base de datos simulada"""
    service = EventService(MagicMock())
    service.repo = MagicMock()
    service.repo.session = MagicMock()
    return service

@pytest.fixture
def mock_registration_service():
    """Crea un RegistrationService con la base de datos simulada"""
    service = RegistrationService(MagicMock())
    service.repo = MagicMock()
    service.repo.session = MagicMock()
    return service

# --- TESTS DE EVENTOS ---

@patch("modules.community_events.services.events.serialize")
def test_publish_event_changes_status_and_visibility(mock_serialize, mock_event_service):
    """Prueba que publicar un evento lo hace público y cambia su estado."""
    # 1. Preparamos el dato falso (un evento en borrador)
    fake_event = Event(id=1, status="draft", is_public=False)
    mock_event_service.repo.session.get.return_value = fake_event
    mock_serialize.side_effect = lambda obj: {"status": obj.status, "is_public": obj.is_public}

    # 2. Ejecutamos la acción
    result = mock_event_service.publish_event(id=1)

    # 3. Comprobamos los resultados (Asserts)
    assert result["status"] == "published"
    assert result["is_public"] is True
    mock_event_service.repo.session.commit.assert_called_once()


@patch("modules.community_events.services.events.serialize")
def test_cancel_event_hides_it_from_public(mock_serialize, mock_event_service):
    """Prueba que cancelar un evento lo oculta del público."""
    fake_event = Event(id=2, status="published", is_public=True)
    mock_event_service.repo.session.get.return_value = fake_event
    mock_serialize.side_effect = lambda obj: {"status": obj.status, "is_public": obj.is_public}

    result = mock_event_service.cancel_event(id=2, reason="Lluvia extrema")

    assert result["status"] == "cancelled"
    assert result["is_public"] is False
    mock_event_service.repo.session.commit.assert_called_once()


# --- TESTS DE INSCRIPCIONES (CHECK-IN) ---

@patch("modules.community_events.services.events.serialize")
def test_checkin_success_for_confirmed_user(mock_serialize, mock_registration_service):
    """Prueba que un usuario confirmado puede entrar al evento."""
    fake_reg = Registration(id=10, status="confirmed", checkin_at=None)
    mock_registration_service.repo.session.get.return_value = fake_reg
    mock_serialize.side_effect = lambda obj: {"checkin_at": obj.checkin_at}

    result = mock_registration_service.checkin(id=10, source="scanner")

    assert result["checkin_at"] is not None
    mock_registration_service.repo.session.commit.assert_called_once()


def test_checkin_fails_for_cancelled_user(mock_registration_service):
    """Prueba de SEGURIDAD: Un usuario cancelado NO puede hacer check-in."""
    fake_reg = Registration(id=11, status="cancelled", checkin_at=None)
    mock_registration_service.repo.session.get.return_value = fake_reg

    # Esperamos que el sistema lance un error HTTP 400
    with pytest.raises(HTTPException) as exc_info:
        mock_registration_service.checkin(id=11)
    
    assert exc_info.value.status_code == 400
    assert "Solo puedes hacer check-in a usuarios confirmados" in exc_info.value.detail
    # Nos aseguramos de que NUNCA se llame a guardar en base de datos
    mock_registration_service.repo.session.commit.assert_not_called()
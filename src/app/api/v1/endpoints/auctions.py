from app.api.dependencies.auctions import get_auction_service
from app.api.dependencies.auth import get_current_user
from app.api.v1.schemas.auction import AuctionCreate, AuctionResponse
from app.application.services.auction_service import AuctionService
from app.domain.exceptions import AuctionCreationError
from app.domain.models.auction import Auction
from app.domain.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated
from uuid import UUID


router = APIRouter(prefix = "/auctions")

# Alias para dependencias
ServiceDep = Annotated[AuctionService, Depends(get_auction_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

@router.post("/", response_model = Auction, status_code = 201) # El 201 es el estándar para 'Created'
async def create_auction(
    auction_in: AuctionCreate,
    current_user: CurrentUserDep,
    service: ServiceDep
):
    try:
        return await service.create_auction(auction_in, seller_id = current_user.id)
    except AuctionCreationError as e:
        service.logger.error(f"Error: {e}")
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))


@router.get("/{auction_id}", response_model = AuctionResponse)
async def get_auction(
    auction_id: UUID, 
    service: ServiceDep
):
    try:
        return await service.get_auction(auction_id)
    except ValueError as e:
        service.logger.error(f"Error: {e}")
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Subasta no encontrada.")
    

@router.patch("/{auction_id}/details", response_model = AuctionResponse)
async def update_auction_details(
    auction_id: UUID,
    current_user: CurrentUserDep,
    service: ServiceDep,
    title: str | None = Query(None),
    description: str | None = Query(None)
):
    try:
        return await service.update_details(auction_id, current_user.id, title, description)
    except PermissionError as e:
        service.logger.error(f"Error: {e}")
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"No eres el dueño de esta subasta: {e}")
    except ValueError as e:
        service.logger.error(f"Error: {e}")
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))


@router.post("/{auction_id}/cancel", response_model = AuctionResponse)
async def cancel_auction(
    auction_id: UUID, 
    current_user: CurrentUserDep, 
    service: ServiceDep
):
    try:
        return await service.cancel_auction(auction_id, current_user.id)
    except PermissionError as e:
        service.logger.error(f"Error: {e}")
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "No tienes permiso")
    except ValueError as e:
        service.logger.error(f"Error: {e}")
        raise HTTPException(status_code = status.HTTP_400, detail = str(e))

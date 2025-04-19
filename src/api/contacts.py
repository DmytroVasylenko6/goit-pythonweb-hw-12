from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.database.models import User
from src.schemas.contacts import ContactModel, ContactResponse
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter()


@router.post("/contacts/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact for an authenticated user.

    Args:
        body (ContactModel): The contact data to create.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The created contact details.
    """
    service = ContactService(db)
    return await service.create_contact(body, user)


@router.get("/contacts/", response_model=List[ContactResponse])
async def read_contacts(
    name: str = Query(None),
    surname: str = Query(None),
    email: str = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts for the authenticated user.

    Supports filtering by name, surname, and email.

    Args:
        name (str, optional): Filter by contact's name.
        surname (str, optional): Filter by contact's surname.
        email (str, optional): Filter by contact's email.
        skip (int, optional): Number of contacts to skip (pagination).
        limit (int, optional): Maximum number of contacts to return.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.

    Returns:
        List[ContactResponse]: A list of contact details.
    """
    service = ContactService(db)
    return await service.get_contacts(name, surname, email, skip, limit, user)


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve details of a specific contact by its ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The contact details.
    """
    service = ContactService(db)
    return await service.get_contact(contact_id, user)


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing contact's details.

    Args:
        contact_id (int): The ID of the contact to update.
        body (ContactModel): The updated contact data.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The updated contact details.
    """
    service = ContactService(db)
    return await service.update_contact(contact_id, body, user)


@router.delete("/contacts/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The deleted contact details.
    """
    service = ContactService(db)
    return await service.remove_contact(contact_id, user)


@router.get("/contacts/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve contacts with upcoming birthdays within a specified number
    of days.

    Args:
        days (int, optional): Number of days to look ahead for upcoming
        birthdays. Defaults to 7.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    service = ContactService(db)
    return await service.get_upcoming_birthdays(days, user)

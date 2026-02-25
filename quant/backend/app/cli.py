"""CLI utilities for admin tasks."""

import asyncio
import sys
from typing import Optional

import typer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.core.logging import setup_logging, get_logger
from app.models.user import User

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Create CLI app
cli = typer.Typer(help="Quant Analytics Platform CLI")


async def get_db_session() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        return session


@cli.command()
def create_superuser(
    username: str = typer.Option(..., prompt=True, help="Username"),
    email: str = typer.Option(..., prompt=True, help="Email address"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True, help="Password"),
):
    """Create a new superuser."""

    async def _create():
        async with AsyncSessionLocal() as session:
            # Check if user already exists
            query = select(User).where(
                (User.username == username) | (User.email == email)
            )
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                if existing_user.username == username:
                    typer.secho(f"Error: Username '{username}' already exists", fg=typer.colors.RED)
                else:
                    typer.secho(f"Error: Email '{email}' already exists", fg=typer.colors.RED)
                sys.exit(1)

            # Create superuser
            hashed_password = get_password_hash(password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True,
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            typer.secho(f"✓ Superuser '{username}' created successfully!", fg=typer.colors.GREEN)
            typer.echo(f"  ID: {user.id}")
            typer.echo(f"  Email: {user.email}")

    asyncio.run(_create())


@cli.command()
def list_users(
    limit: int = typer.Option(10, help="Maximum number of users to display"),
    active_only: bool = typer.Option(False, "--active-only", help="Show only active users"),
):
    """List all users."""

    async def _list():
        async with AsyncSessionLocal() as session:
            query = select(User).order_by(User.created_at.desc()).limit(limit)

            if active_only:
                query = query.where(User.is_active == True)

            result = await session.execute(query)
            users = result.scalars().all()

            if not users:
                typer.echo("No users found.")
                return

            typer.echo(f"\nFound {len(users)} user(s):\n")

            for user in users:
                status = "✓" if user.is_active else "✗"
                role = "SUPERUSER" if user.is_superuser else "USER"

                typer.echo(f"{status} {user.username} ({user.email})")
                typer.echo(f"  ID: {user.id}")
                typer.echo(f"  Role: {role}")
                typer.echo(f"  Created: {user.created_at}")
                if user.last_login:
                    typer.echo(f"  Last Login: {user.last_login}")
                typer.echo()

    asyncio.run(_list())


@cli.command()
def activate_user(
    username: str = typer.Argument(..., help="Username to activate"),
):
    """Activate a user account."""

    async def _activate():
        async with AsyncSessionLocal() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                typer.secho(f"Error: User '{username}' not found", fg=typer.colors.RED)
                sys.exit(1)

            if user.is_active:
                typer.secho(f"User '{username}' is already active", fg=typer.colors.YELLOW)
                return

            user.is_active = True
            await session.commit()

            typer.secho(f"✓ User '{username}' activated successfully!", fg=typer.colors.GREEN)

    asyncio.run(_activate())


@cli.command()
def deactivate_user(
    username: str = typer.Argument(..., help="Username to deactivate"),
):
    """Deactivate a user account."""

    async def _deactivate():
        async with AsyncSessionLocal() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                typer.secho(f"Error: User '{username}' not found", fg=typer.colors.RED)
                sys.exit(1)

            if not user.is_active:
                typer.secho(f"User '{username}' is already inactive", fg=typer.colors.YELLOW)
                return

            user.is_active = False
            await session.commit()

            typer.secho(f"✓ User '{username}' deactivated successfully!", fg=typer.colors.GREEN)

    asyncio.run(_deactivate())


@cli.command()
def change_password(
    username: str = typer.Argument(..., help="Username"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True, help="New password"),
):
    """Change a user's password."""

    async def _change_password():
        async with AsyncSessionLocal() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                typer.secho(f"Error: User '{username}' not found", fg=typer.colors.RED)
                sys.exit(1)

            user.hashed_password = get_password_hash(password)
            await session.commit()

            typer.secho(f"✓ Password changed successfully for '{username}'!", fg=typer.colors.GREEN)

    asyncio.run(_change_password())


@cli.command()
def delete_user(
    username: str = typer.Argument(..., help="Username to delete"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Delete a user account."""

    async def _delete():
        async with AsyncSessionLocal() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                typer.secho(f"Error: User '{username}' not found", fg=typer.colors.RED)
                sys.exit(1)

            if not confirm:
                confirmed = typer.confirm(
                    f"Are you sure you want to delete user '{username}' ({user.email})?"
                )
                if not confirmed:
                    typer.echo("Cancelled.")
                    return

            await session.delete(user)
            await session.commit()

            typer.secho(f"✓ User '{username}' deleted successfully!", fg=typer.colors.GREEN)

    asyncio.run(_delete())


@cli.command()
def db_init():
    """Initialize the database (create all tables)."""

    async def _init():
        from app.core.database import engine, Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        typer.secho("✓ Database initialized successfully!", fg=typer.colors.GREEN)

    asyncio.run(_init())


@cli.command()
def db_migrate():
    """Run database migrations."""
    import subprocess

    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )
        typer.echo(result.stdout)
        typer.secho("✓ Database migrations completed successfully!", fg=typer.colors.GREEN)
    except subprocess.CalledProcessError as e:
        typer.secho(f"Error running migrations: {e.stderr}", fg=typer.colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    cli()

"""CLI utils."""

import click


@click.group(help="CLI utils for the app.")
def cli():
    pass


@cli.command(help="Create new users from JSONL file.")
@click.argument("file", type=click.Path(exists=True))
def create_users(file: str) -> None:
    """Create new users from JSONL file."""
    from app.auth.auth_service import AuthService

    AuthService().create_users(file)


if __name__ == "__main__":
    cli()

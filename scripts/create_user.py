import typer
from app.core.security import get_password_hash

app = typer.Typer()


@app.command()
def main(
    username: str = typer.Option(..., prompt="Digite o nome de usuário"),
    password: str = typer.Option(
        ..., prompt="Digite a senha", hide_input=True, confirmation_prompt=True
    ),
):
    hashed_password = get_password_hash(password)

    print("\n--- Usuário para Inserção no Banco ---")
    print(f"Username: {username}")
    print(f"Hashed Password: {hashed_password}")
    print("\nCopie o hash da senha para usar no comando SQL.")
    print("--------------------------------------")


if __name__ == "__main__":
    app()

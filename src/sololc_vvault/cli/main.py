import typer
import time
from typing import Annotated, Optional, List, Tuple
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.status import Status
from pyzbar.pyzbar import decode
from PIL import Image
import pyperclip
from sololc_vvault.core import storage, totp, vault, crypto

app = typer.Typer(help="vlt - Minimalist Secure Vault (Vvault CLI)", add_completion=False)
console = Console()

# --- 🔑 核心安全辅助函数 ---

def unlock_vault() -> Tuple[str, List[dict]]:
    """
    统一的解密入口：提示输入密码并返回 (密码, 解密后的账号列表)
    """
    if not storage.vault_exists():
        console.print("[red]✘ 金库尚未初始化。请先运行 'vlt init'。[/red]")
        raise typer.Exit(1)

    password = typer.prompt("🔑 输入主密码 (Master Password)", hide_input=True)
    
    try:
        # 读取加密的原始字符串
        raw_encrypted = storage.read_vault_raw()
        # 解密
        decrypted_json = crypto.decrypt_data(raw_encrypted, password)
        # 解析为列表
        accounts = vault.parse_vault_data(decrypted_json)
        return password, accounts
    except Exception:
        console.print("[bold red]✘ 拒绝访问:[/bold red] 密码错误或数据已损坏。")
        raise typer.Exit(1)

# --- 🔒 (Security) ---

@app.command(help="Initialize Vvault: Set the master password and create encrypted storage")
def init():
    """Initialize Vvault: Set the master password and create encrypted storage"""
    if storage.vault_exists():
        console.print("[yellow]⚠️  The vault already exists ~/.vlt/ [/yellow]")
        if not typer.confirm("Confirm reset? This will delete all existing accounts! "):
            raise typer.Exit()

    console.print(Panel.fit(
        "🔒 [bold]Vvault Initialize[/bold]\n"
        "Please set a strong master password. It will be used to protect all your 2FA keys.",
        border_style="blue"
    ))

    password = typer.prompt("Set master password", hide_input=True, confirmation_prompt=True)
    
    # Initial empty vault structure
    initial_accounts = []

    with console.status("[bold blue]Encrypting and creating secure storage..."):
        try:
            storage.ensure_storage_path()
            # Serialize and encrypt
            raw_json = vault.serialize_vault_data(initial_accounts)
            encrypted_data = crypto.encrypt_data(raw_json, password)
            # Physical write
            storage.write_vault_raw(encrypted_data)
            
            console.print("\n[bold green]✔ Vvault Initialization successful and locked.[/bold green]")
        except Exception as e:
            console.print(f"[red]Initialization failed: {e}[/red]")
            raise typer.Exit(1)

# @app.command()
# def lock():
#     """Immediately lock the current session (clear temporary keys in memory)."""
#     console.print("[bold blue]🔒 The session is locked. You will need to re-enter your master password for the next operation. [/bold blue]")

# --- 🛡️ (Account Management) ---

@app.command(help="Add account. e.g.: vlt add github --secret KHR2UEJ33JJG... --issuer GitHub --category Dev")
def add(
    name: str, 
    secret: Annotated[str, typer.Option("--secret", "-s", help="OTP Key")], 
    issuer: str = "Unknown", 
    category: str = "General"
):
    password, accounts = unlock_vault()
    
    updated = vault.add_account_to_list(accounts, name, secret, issuer, category)
    
    new_raw = vault.serialize_vault_data(updated)
    storage.write_vault_raw(crypto.encrypt_data(new_raw, password))
    
    console.print(f"[green]✔[/green] Account [bold]{name}[/bold] Already deposited [blue]{category}[/blue]")

@app.command(name="list", help="List all saved account names (without displaying verification codes).")
def list_accounts():
    _, accounts = unlock_vault()
    
    if not accounts:
        console.print("[yellow]The vault was empty. [/yellow]")
        return

    table = Table(title="vlt account list")
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Issuer", style="magenta")
    table.add_column("Category", style="green")

    for idx, acc in enumerate(accounts, 1):
        table.add_row(str(idx), acc['name'], acc.get('issuer', 'N/A'), acc.get('category', 'General'))
    
    console.print(table)

@app.command(help="Remove account. e.g.: vlt remove name")
def remove(name: str):
    password, accounts = unlock_vault()
    
    updated = [a for a in accounts if a['name'] != name]
    if len(updated) == len(accounts):
        console.print(f"[red]✘ Account not found: {name}[/red]")
    else:
        new_raw = vault.serialize_vault_data(updated)
        storage.write_vault_raw(crypto.encrypt_data(new_raw, password))
        console.print(f"[green]✔ Account {name} It has been removed from the vault. [/green]")

# --- 🔑 (Code Generation) ---

@app.command(help="Get the current verification code for the specified account. e.g.: vlt get name")
def get(name: str, copy: bool = typer.Option(False, "--copy", "-c", help="Automatically copy to clipboard")):
    _, accounts = unlock_vault()
    account = next((a for a in accounts if a['name'] == name), None)
    
    if not account:
        console.print(f"[red]✘ Account not found: {name}[/red]")
        return

    code = totp.generate_code(account['secret'])
    if copy:
        pyperclip.copy(code)
        msg = " [Copy to clipboard]"
    else:
        msg = ""

    console.print(Panel(f"[bold cyan]{code[:3]} {code[3:]}[/bold cyan]{msg}", title=f"{account['name']} ({account.get('issuer')})", expand=False))

@app.command(help="Dashboard mode. e.g.: vlt dash")
def dash():
    password, _ = unlock_vault()

    def generate_table():
        # The dashboard needs to be read in real time to prevent data modification by other terminal instances.
        raw_encrypted = storage.read_vault_raw()
        accounts = vault.parse_vault_data(crypto.decrypt_data(raw_encrypted, password))
        
        table = Table(title="vlt Live Dashboard", header_style="bold magenta")
        table.add_column("Category", style="green")
        table.add_column("Issuer")
        table.add_column("Account", style="cyan")
        table.add_column("Code", justify="center", style="bold green")
        table.add_column("Remains", justify="right")

        for acc in accounts:
            code = totp.generate_code(acc['secret'])
            rem = totp.get_remaining_seconds()
            color = "green" if rem > 10 else "red"
            table.add_row(
                acc.get('category', 'General'), 
                acc.get('issuer', 'N/A'), 
                acc['name'], 
                f"{code[:3]} {code[3:]}", 
                f"[{color}]{rem}s[/{color}]"
            )
        return table

    with Live(generate_table(), refresh_per_second=1) as live:
        try:
            while True:
                time.sleep(1)
                live.update(generate_table())
        except KeyboardInterrupt:
            pass

# --- 📂 (Import & Backup) ---

@app.command(name="import", help="Import data. e.g.: vlt import --qr ./path/to/qr_code.png or vlt import --url otpauth://totp/Service:User?secret=XYZ...")
def import_data(
    qr: Annotated[Optional[Path], typer.Option("--qr", help="QR code image path")] = None,
    url: Annotated[Optional[str], typer.Option("--url", help="Import via link")] = None
):
    """Import account from QR code (OpenCV) or URL"""
    password, current_accounts = unlock_vault()
    new_accs: List[dict] = []
    
    try:
        if qr:
            if not qr.exists():
                console.print(f"[red]✘ File not found: {qr}[/red]")
                return

            # Open the image using Pillow and decode it using pyzbar.
            with Image.open(qr) as img:
                decoded_objects = decode(img)
                
            if not decoded_objects:
                console.print(f"[yellow]⚠ No QR code detected in: {qr}[/yellow]")
                return
            
            # Get the data of the first recognized QR code
            data = decoded_objects[0].data.decode("utf-8")
            if data:
                new_accs.append(vault.parse_otpauth_url(data))

        elif url:
            new_accs.append(vault.parse_otpauth_url(url))
        
        if new_accs:
            updated = vault.merge_accounts(current_accounts, new_accs)
            new_raw = vault.serialize_vault_data(updated)
            storage.write_vault_raw(crypto.encrypt_data(new_raw, password))
            console.print(f"[green]✔ Successfully imported {len(new_accs)} account(s).[/green]")
        else:
            console.print("[yellow]⚠ No valid data to import.[/yellow]")

    except Exception as e:
        console.print(f"[red]✘ Import failed: {e}[/red]")

@app.command(help="Backup file save path. e.g.: vlt backup ./my_backup.yaml")
def backup(path: Annotated[Path, typer.Argument(help="Backup file save path. e.g.: vlt backup ./my_backup.yaml")]):
    _, accounts = unlock_vault()
    try:
        data_yaml = vault.serialize_vault_data(accounts)
        path.write_text(data_yaml, encoding="utf-8")
        console.print(f"[green]✔ Export successful! Backup file (plaintext): [bold]{path}[/bold][/green]")
        console.print("[dim]⚠️ Warning: This file contains a sensitive private key. Please ensure it is stored in a safe place. [/dim]")
    except Exception as e:
        console.print(f"[red]✘ Backup failed: {e}[/red]")

if __name__ == "__main__":
    app()
import requests
import random
import string
import time
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from pyfiglet import figlet_format
import keyboard

console = Console()

def hacker_banner(text):
    banner = figlet_format(text, font="slant")
    console.print(f"[bold green]{banner}[/bold green]")

def generate_random_username(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_temp_account():
    username = generate_random_username()
    domain_resp = requests.get("https://api.mail.tm/domains")
    domain = domain_resp.json()["hydra:member"][0]["domain"]
    email = f"{username}@{domain}"
    password = "TempPass123!"

    payload = {
        "address": email,
        "password": password
    }

    requests.post("https://api.mail.tm/accounts", json=payload)
    token_resp = requests.post("https://api.mail.tm/token", json=payload)
    token = token_resp.json()["token"]

    return email, password, token

def get_messages(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get("https://api.mail.tm/messages", headers=headers)
    return resp.json().get("hydra:member", [])

def read_message(token, message_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.mail.tm/messages/{message_id}"
    resp = requests.get(url, headers=headers)
    return resp.json()

def delete_message(token, message_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.mail.tm/messages/{message_id}"
    requests.delete(url, headers=headers)

def save_message_to_file(message):
    with open("saved_emails.txt", "a", encoding="utf-8") as f:
        f.write(f"From: {message['from']['address']}\n")
        f.write(f"Subject: {message['subject']}\n")
        f.write(f"Message:\n{message['text']}\n")
        f.write("-" * 50 + "\n")

def print_message_table(messages):
    table = Table(title="📥 Inbox", box=box.DOUBLE_EDGE, show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("From", style="green")
    table.add_column("Subject", style="magenta")

    for msg in messages:
        table.add_row(msg["id"][:8], msg["from"]["address"], msg["subject"])
    console.print(table)

def print_account_info(email, password):
    table = Table(title="Account Info", box=box.DOUBLE_EDGE, show_lines=True)
    table.add_column("Email", style="green")
    table.add_column("Password", style="red")
    table.add_row(email, password)
    console.print(table)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    clear()
    hacker_banner("TEMP MAIL")
    console.print("[yellow]Initializing temp mail system...[/yellow]")
    email, password, token = create_temp_account()

    while True:
        console.print("[cyan]Press 'r' to refresh, 'q' to quit, 'd' to delete, 's' to save email, 'a' to show account info[/cyan]")
        messages = get_messages(token)

        if messages:
            print_message_table(messages)
            console.print("[bold green]You have message(s)![/bold green]\n")

            for msg in messages:
                full_msg = read_message(token, msg["id"])
                console.print(Panel(f"[bold]From:[/bold] {full_msg['from']['address']}\n"
                                    f"[bold]Subject:[/bold] {full_msg['subject']}\n\n"
                                    f"{full_msg['text']}",
                                    title="📨 New Message", subtitle=f"ID: {msg['id'][:8]}"))
                time.sleep(1)

        else:
            console.print("[bold yellow]Inbox is empty. Waiting for new messages...[/bold yellow]")

        while True:
            if keyboard.is_pressed('r'):
                clear()
                hacker_banner("TEMP MAIL")
                break
            elif keyboard.is_pressed('q'):
                console.print("[bold red]Exiting...[/bold red]")
                exit()
            elif keyboard.is_pressed('d'):
                if messages:
                    delete_message(token, messages[0]["id"])
                    console.print("[red]Deleted first message.[/red]")
                    break
            elif keyboard.is_pressed('s'):
                if messages:
                    save_message_to_file(read_message(token, messages[0]["id"]))
                    console.print("[green]Message saved to file.[/green]")
                    break
            elif keyboard.is_pressed('a'):
                print_account_info(email, password)
                break

        time.sleep(2)

if __name__ == "__main__":
    main()

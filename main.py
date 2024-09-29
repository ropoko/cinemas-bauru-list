import json
import requests
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main(cinema_id: str, date: datetime):
	cinemas = json.load(open("config.json"))["cinemas"]
	cinema = next((c for c in cinemas if c["id"] == cinema_id), None)

	if not cinema:
		for cine in cinemas:
			response = requests.get(cine["url"])

			if response.status_code == 200:
				get_schedule(cine, response.json(), date)
			else:
				print(f"Erro ao obter dados do cinema {cine['name']}: {response.status_code}")

	else:
		response = requests.get(cinema["url"])
		if response.status_code == 200:
			get_schedule(cinema, response.json(), date)
		else:
			print(f"Erro ao obter dados do cinema {cinema['name']}: {response.status_code}")


def get_schedule(cinema, data: dict|str, date: datetime):
	cinema_id = cinema["id"]
	cinema_name = cinema["name"]

	eval(f"{cinema_id}(cinema_name, data, date)")


def boulevard_shopping(name, data: dict, date: datetime):
	response = json.loads(data["response"])
	date_str = date.strftime("%Y-%m-%d")
	filtered_data = next((day for day in response if day["data"] == date_str), None)

	if filtered_data:
		title = f"[bold cyan]{name}[/bold cyan]"
		subtitle = f"[yellow]Data:[/yellow] {filtered_data['dataFormatada']} ({filtered_data['diaSemana']}) | [yellow]Filmes em cartaz:[/yellow] {len(filtered_data['filmes'])}"
		console.print(Panel(f"{title}\n{subtitle}", expand=False, border_style="cyan"))

		table = Table(show_header=True, header_style="bold magenta")
		table.add_column("Filme", style="dim", width=40)
		table.add_column("Horários")

		for filme in filtered_data['filmes']:
			titulo = filme['titulo']
			horarios = []
			for sala in filme['salas']:
				for sessao in sala['sessoes']:
					horarios.append(sessao['horario']['hora'])
			horarios_str = ', '.join(sorted(set(horarios)))
			table.add_row(titulo, horarios_str)

		console.print(table)
	else:
		console.print(f"[red]Nenhum dado disponível para a data {date_str}[/red]")

def bauru_shopping(name, data: dict, date: datetime):
	date_str = date.strftime("%d/%m")
	filtered_data = next((day for day in data if day["data"] == date_str), None)

	if filtered_data:
		title = f"[bold cyan]{name}[/bold cyan]"
		subtitle = f"[yellow]Data:[/yellow] {filtered_data['data']} ({filtered_data['semana']}) | [yellow]Filmes em cartaz:[/yellow] {len(filtered_data['filmes'])}"
		console.print(Panel(f"{title}\n{subtitle}", expand=False, border_style="cyan"))

		table = Table(show_header=True, header_style="bold magenta")
		table.add_column("Filme", style="dim", width=40)
		table.add_column("Horários")

		for filme in filtered_data['filmes']:
			titulo = filme['titulo']
			horarios = []
			for programacao in filme['programacao']:
				for horario in programacao['horario']:
					horarios.append(horario[0])
			horarios_str = ', '.join(horarios)
			table.add_row(titulo, horarios_str)

		console.print(table)
	else:
		console.print(f"[red]Nenhum dado disponível para a data {date_str}[/red]")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="cine-bauru", description="Descubra os horários de filmes em cartórios de Bauru")
	parser.add_argument("--cinema", type=str, help="ID do cinema", choices=["boulevard_shopping", "bauru_shopping"])
	parser.add_argument("--date", type=str, help="Data no formato DD-MM-YYYY", default=datetime.now())

	args = vars(parser.parse_args())

	cinema_arg = args.get("cinema")
	date_arg = datetime.strptime(args.get("date"), "%d-%m-%Y") if isinstance(args.get("date"), str) else args.get("date")

	main(cinema_arg, date_arg)

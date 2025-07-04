from models import Obra, Usuario, Emprestimo
from core import Acervo
from datetime import datetime
from repositorio import salvar_obra, salvar_usuario, salvar_emprestimo, deletar_obra, deletar_user, deletar_emprestimos
from rich.console import Console

console = Console()
acervo = Acervo()
usuarios = {}
emprestimos_ativos = []

def menu_principal():
    """
    Exibe o menu principal do sistema, permitindo escolher entre as áreas
    do administrador, do usuário, ou sair do sistema.
    """
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("[1] Área do Administrador")
        print("[2] Área do Usuário")
        print("[0] Sair")
        opcao = input("Escolha: ")

        if opcao == '1':
            menu_admin()
        elif opcao == '2':
            menu_usuario()
        elif opcao == '0':
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")

def menu_admin():
    """
    Área do administrador: gerencia obras, usuários, empréstimos e relatórios.
    Opções disponíveis:
    1 - Cadastrar nova obra
    2 - Remover obra
    3 - Cadastrar novo usuário
    4 - Remover usuário
    5 - Remover todos empréstimos de uma obra
    6 - Ver relatório do inventário
    7 - Ver relatório de débitos
    0 - Voltar ao menu principal
    """
    while True:
        print("\n--- ÁREA DO ADMINISTRADOR ---")
        print("[1] Cadastrar nova obra")
        print("[2] Remover obra")
        print("[3] Cadastrar novo usuário")
        print("[4] Remover usuário")
        print("[5] Remover empréstimos de uma obra")
        print("[6] Ver relatório do inventário")
        print("[7] Ver relatório de débitos")
        print("[0] Voltar")
        opcao = input("Escolha: ")

        if opcao == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            try:
                ano = int(input("Ano: "))
                quantidade = int(input("Quantidade: "))
            except ValueError:
                print("Ano e quantidade devem ser números inteiros.")
                continue
            categoria = input("Categoria: ")
            obra = Obra(titulo, autor, ano, categoria, quantidade)
            acervo += obra
            salvar_obra(obra)
            print(f"Obra '{titulo}' cadastrada com sucesso!")
        elif opcao == '2':
            titulo = input("Título da obra a remover: ")
            obra = acervo.obras.get(titulo)
            if obra:
                acervo -= obra
                deletar_obra(obra.id)
                print(f"Obra '{titulo}' removida com sucesso.")
            else:
                print("Obra não encontrada.")
        elif opcao == '3':
            nome = input("Nome: ")
            email = input("Email: ")
            usuario = Usuario(nome, email)
            usuarios[usuario.id] = usuario
            salvar_usuario(usuario)
            print(f"Usuário '{nome}' cadastrado com sucesso!")
        elif opcao == '4':
            nome = input("Nome do usuário a remover: ")
            for u_id, u in list(usuarios.items()):
                if u.nome.lower() == nome.lower():
                    deletar_user(u.id)
                    del usuarios[u_id]
                    print(f"Usuário '{nome}' removido com sucesso.")
                    break
            else:
                print("Usuário não encontrado.")
        elif opcao == '5':
            titulo = input("Título da obra para remover empréstimos: ")
            obra = acervo.obras.get(titulo)
            if obra:
                deletar_emprestimos(obra.id)
                print(f"Empréstimos da obra '{titulo}' removidos.")
            else:
                print("Obra não encontrada.")
        elif opcao == '6':
            tabela = acervo.relatorio_inventario()
            console.print(tabela)
        elif opcao == '7':
            tabela = acervo.relatorio_debitos()
            console.print(tabela)
        elif opcao == '0':
            break
        else:
            print("Opção inválida! Tente novamente.")

def menu_usuario():
    """
    Área do usuário: permite realizar empréstimos, devoluções,
    renovações e consulta do histórico de empréstimos.
    Opções disponíveis:
    1 - Realizar empréstimo
    2 - Devolver obra
    3 - Renovar empréstimo
    4 - Ver histórico de empréstimos
    0 - Voltar ao menu principal
    """
    while True:
        print("\n--- ÁREA DO USUÁRIO ---")
        print("[1] Realizar empréstimo")
        print("[2] Devolver obra")
        print("[3] Renovar empréstimo")
        print("[4] Ver histórico de empréstimos")
        print("[0] Voltar")
        opcao = input("Escolha: ")

        if opcao == '1':
            nome = input("Nome do usuário: ")
            usuario = encontrar_usuario_por_nome(nome)
            if not usuario:
                print("Usuário não encontrado.")
                continue
            titulo = input("Título da obra: ")
            obra = acervo.obras.get(titulo)
            if not obra:
                print("Obra não encontrada.")
                continue
            try:
                dias = int(input("Quantos dias de empréstimo? "))
            except ValueError:
                print("Digite um número válido para os dias.")
                continue
            try:
                emprestimo = acervo.emprestar(obra, usuario, dias)
                salvar_emprestimo(emprestimo)
                emprestimos_ativos.append(emprestimo)
                print("Empréstimo realizado com sucesso!")
            except ValueError as e:
                print(f"Erro: {e}")
        elif opcao == '2':
            nome = input("Nome do usuário: ")
            usuario = encontrar_usuario_por_nome(nome)
            if not usuario:
                print("Usuário não encontrado.")
                continue
            emprestimos = [e for e in emprestimos_ativos if e.usuario == usuario and not e.data_devolucao]
            if not emprestimos:
                print("Nenhum empréstimo em aberto para este usuário.")
                continue
            for i, e in enumerate(emprestimos):
                print(f"[{i}] {e}")
            try:
                i = int(input("Escolha o índice do empréstimo a devolver: "))
                if i < 0 or i >= len(emprestimos):
                    print("Índice inválido.")
                    continue
            except ValueError:
                print("Digite um índice válido.")
                continue
            data_devol = input("Data da devolução (DD/MM/AAAA): ")
            try:
                data_devol = datetime.strptime(data_devol, "%d/%m/%Y").date()
            except ValueError:
                print("Formato de data inválido.")
                continue
            acervo.devolver(emprestimos[i], data_devol)
            print("Devolução registrada com sucesso!")
        elif opcao == '3':
            nome = input("Nome do usuário: ")
            usuario = encontrar_usuario_por_nome(nome)
            if not usuario:
                print("Usuário não encontrado.")
                continue
            emprestimos = [e for e in emprestimos_ativos if e.usuario == usuario and not e.data_devolucao]
            if not emprestimos:
                print("Nenhum empréstimo em aberto para este usuário.")
                continue
            for i, e in enumerate(emprestimos):
                print(f"[{i}] {e}")
            try:
                i = int(input("Escolha o índice do empréstimo a renovar: "))
                if i < 0 or i >= len(emprestimos):
                    print("Índice inválido.")
                    continue
            except ValueError:
                print("Digite um índice válido.")
                continue
            try:
                dias = int(input("Dias extras para renovação: "))
            except ValueError:
                print("Digite um número válido para os dias.")
                continue
            try:
                acervo.renovar(emprestimos[i], dias)
                print("Empréstimo renovado com sucesso!")
            except ValueError as e:
                print(f"Erro: {e}")
        elif opcao == '4':
            nome = input("Nome do usuário: ")
            usuario = encontrar_usuario_por_nome(nome)
            if usuario:
                tabela = acervo.historico_usuario(usuario)
                console.print(tabela)
            else:
                print("Usuário não encontrado.")
        elif opcao == '0':
            break
        else:
            print("Opção inválida! Tente novamente.")

def encontrar_usuario_por_nome(nome):
    """
    Busca um usuário pelo nome, ignorando maiúsculas/minúsculas.

    Args:
        nome (str): Nome do usuário a buscar.

    Returns:
        Usuario | None: Usuário encontrado ou None se não existir.
    """
    for u in usuarios.values():
        if u.nome.lower() == nome.lower():
            return u
    return None

if __name__ == "__main__":
    print("Bem-vindo ao Sistema de Acervo Bibliográfico 📚")
    menu_principal()
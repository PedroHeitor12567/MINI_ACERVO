from repositorio import salvar_obra, salvar_usuario, salvar_emprestimo, deletar_emeprestimos, deletar_obra, deletar_user, validar_email
from models import Usuario, Obra, Emprestimo

print("=================================")
print("=== Bem-vindo ao mini Acervo === ")
print("=================================")

while True:
    print("[1] - Cadastrar usuário")
    print("[2] - Entrar")
    opcao = int(input("Escolha uma das opções: "))
    
    match opcao:
        case 1:
            nome = input("Digite o seu nome: ")
            while True:
                email = input("Digite seu melhor email: ")
                if validar_email(email):
                    break
                else:
                    print("⚠️ Email inválido! Tente novamente.")
            
            novo_user = Usuario(nome, email)
            salvar_usuario(novo_user)
        
        case 2:
            pass
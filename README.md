# MINI_ACERVO 📚 Sistema de Gerenciamento de Empréstimos de Obras

Este projeto é um sistema de gerenciamento de empréstimos de obras, como livros, documentos ou mídias, com suporte a usuários e administradores. Desenvolvido em Python com conexão a banco de dados PostgreSQL, o sistema possui duas interfaces distintas: uma para o **usuário comum** e outra para o **administrador**.

---

## 🚀 Funcionalidades

### 👤 Área do Usuário

Usuários podem:

1. **Realizar empréstimo** de obras disponíveis  
2. **Devolver obras** emprestadas  
3. **Renovar empréstimos** ativos  
4. **Consultar histórico** de empréstimos realizados  
0. Voltar ao menu principal

### 🛠️ Área do Administrador

Administradores podem:

1. **Cadastrar nova obra** no acervo  
2. **Remover obra** existente  
3. **Cadastrar novo usuário**  
4. **Remover usuário** do sistema  
5. **Remover todos os empréstimos** relacionados a uma obra específica  
6. **Gerar relatório de inventário** (obras e disponibilidade)  
7. **Gerar relatório de débitos** (empréstimos atrasados ou pendentes)  
0. Voltar ao menu principal

---

## 🗂 Estrutura de Arquivos

O projeto está organizado em 6 arquivos principais:

| Arquivo                | Função                                                                 |
|------------------------|------------------------------------------------------------------------|
| `acervo/__init__.py`   | Arquivo de inicialização do pacote `acervo`. Pode conter metadados ou inicializações necessárias. |
| `acervo/core.py`       | Contém as funções de controle de menu principal, login e navegação entre as interfaces de usuário e admin, tem todas as interações entre o código e o banco de dados. |
| `acervo/models.py`     | Define as classes e estruturas de dados principais, como `Usuario`, `Obra`, `Emprestimo` etc. Usa POO. |
| `acervo/connect.py`    | Gerencia a conexão com o banco de dados PostgreSQL (função `conectar()`). |
| `main.py`              | Arquivo principal que inicia o sistema. Chama `menu_principal()` e integra todos os módulos. |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **PostgreSQL**
- **psycopg2** (para conexão com o banco de dados)
- **Rich** (para impressão de tabelas e saídas visuais no terminal)

---

## 📦 Requisitos

- Python instalado
- PostgreSQL configurado
- Biblioteca `psycopg2` instalada:
  ```bash
  pip install -r requeriments.txt
  ```
- Possuir pgAdmin e senha
---

## 🧪 Como Rodar o Projeto

1. Clone o repositório:

   ```bash
   https://github.com/PedroHeitor12567/MINI_ACERVO.git
   cd MINI_ACERVO
   ```

2. Crie o banco de dados PostgreSQL e configure a função `conectar()` no `connect.py` com as credenciais certas.

3. Execute o projeto:

   ```bash
   python main.py
   ```

---

## 📌 Observações

- O identificador dos usuários e obras é baseado em UUIDs.
- O sistema atualiza automaticamente o estoque de obras ao registrar uma devolução.
- O código é modular, usando programação orientada a objetos (POO).

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 👨‍💻 Desenvolvedores

- [@PedroHeitor12567](https://github.com/PedroHeitor12567) 
- [@Wallyson-fer](https://github.com/Wallyson-fer)
### Desenvolvedores Python & Backend 💻
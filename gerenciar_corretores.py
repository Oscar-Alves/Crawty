import argparse
import sys
from datetime import datetime, timezone
from backend.database import corretores_collection
from backend.auth import gerar_hash_senha


def _garantir_conexao_banco():
    if corretores_collection is None:
        print("ERRO: Banco de dados não conectado. Verifique o arquivo credentials.env.")
        sys.exit(1)


def comando_criar(args: argparse.Namespace) -> None:
    _garantir_conexao_banco()
    usuario = args.usuario.strip().lower()
    if len(usuario) < 2:
        print("ERRO: O nome de usuário deve ter pelo menos 2 caracteres.")
        sys.exit(1)

    existente = corretores_collection.find_one({"usuario": usuario})
    if existente:
        print(f"ERRO: Já existe um corretor cadastrado com o usuário '{usuario}'.")
        sys.exit(1)

    agora = datetime.now(timezone.utc)
    documento = {
        "usuario": usuario,
        "senha_hash": gerar_hash_senha(args.senha),
        "nome": args.nome.strip(),
        "imobiliaria": (args.imobiliaria or args.nome).strip(),
        "role": args.role,
        "creci": (args.creci or "").strip(),
        "whatsapp": (args.whatsapp or "").strip(),
        "telefone": (args.telefone or "").strip(),
        "email": (args.email or "").strip(),
        "site_externo": (args.site or "").strip(),
        "ativo": True,
        "creditos_impulsionamento": int(args.creditos or 0),
        "criado_em": agora,
        "atualizado_em": agora,
        "ultimo_login": None,
    }

    corretores_collection.insert_one(documento)
    print(f"Conta criada com sucesso! Usuário: '{usuario}' | Parceiro: '{documento['imobiliaria']}'")


def comando_listar(_args: argparse.Namespace) -> None:
    _garantir_conexao_banco()
    docs = list(corretores_collection.find({}, {"senha_hash": 0}).sort("usuario", 1))
    if not docs:
        print("Nenhuma conta de corretor cadastrada até o momento.")
        return

    print(f"\nTotal de parceiros cadastrados: {len(docs)}")
    print("-" * 95)
    print(f"{'USUÁRIO':<18} | {'NOME':<24} | {'IMOBILIÁRIA / MARCA':<24} | {'ROLE':<8} | {'STATUS'}")
    print("-" * 95)
    for d in docs:
        status_str = "ATIVO" if d.get("ativo", True) is not False else "SUSPENSO"
        print(
            f"{d.get('usuario', ''):<18} | "
            f"{d.get('nome', '')[:24]:<24} | "
            f"{d.get('imobiliaria', '')[:24]:<24} | "
            f"{d.get('role', 'corretor'):<8} | "
            f"{status_str}"
        )
    print("-" * 95)


def comando_alterar_senha(args: argparse.Namespace) -> None:
    _garantir_conexao_banco()
    usuario = args.usuario.strip().lower()
    res = corretores_collection.update_one(
        {"usuario": usuario},
        {
            "$set": {
                "senha_hash": gerar_hash_senha(args.senha),
                "atualizado_em": datetime.now(timezone.utc),
            }
        },
    )
    if res.matched_count == 0:
        print(f"ERRO: Usuário '{usuario}' não encontrado.")
        sys.exit(1)
    print(f"Senha do usuário '{usuario}' alterada com sucesso!")


def comando_status(args: argparse.Namespace) -> None:
    _garantir_conexao_banco()
    usuario = args.usuario.strip().lower()
    novo_ativo = args.ativo.strip().lower() in ("true", "1", "sim", "ativo")
    res = corretores_collection.update_one(
        {"usuario": usuario},
        {
            "$set": {
                "ativo": novo_ativo,
                "atualizado_em": datetime.now(timezone.utc),
            }
        },
    )
    if res.matched_count == 0:
        print(f"ERRO: Usuário '{usuario}' não encontrado.")
        sys.exit(1)
    estado_txt = "ATIVADA" if novo_ativo else "SUSPENSA"
    print(f"Conta do usuário '{usuario}' foi {estado_txt} com sucesso.")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gerenciador CLI de Contas B2B de Corretores e Imobiliárias (HubImóveis)"
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_criar = subparsers.add_parser("criar", help="Cria uma nova conta de corretor/imobiliária")
    p_criar.add_argument("--usuario", required=True, help="Login único do corretor (ex: joao.corretor)")
    p_criar.add_argument("--senha", required=True, help="Senha inicial de acesso")
    p_criar.add_argument("--nome", required=True, help="Nome completo do responsável")
    p_criar.add_argument("--imobiliaria", help="Nome comercial da imobiliária ou corretor autônomo")
    p_criar.add_argument("--creci", default="", help="Registro CRECI (ex: MG-12345)")
    p_criar.add_argument("--whatsapp", default="", help="WhatsApp para contato direto")
    p_criar.add_argument("--telefone", default="", help="Telefone secundário")
    p_criar.add_argument("--email", default="", help="E-mail comercial")
    p_criar.add_argument("--site", default="", help="URL do site externo (opcional)")
    p_criar.add_argument("--role", choices=["corretor", "admin"], default="corretor", help="Perfil de acesso")
    p_criar.add_argument("--creditos", type=int, default=0, help="Créditos iniciais de impulsionamento")
    p_criar.set_defaults(func=comando_criar)

    p_listar = subparsers.add_parser("listar", help="Lista todos os corretores cadastrados")
    p_listar.set_defaults(func=comando_listar)

    p_senha = subparsers.add_parser("alterar-senha", help="Redefine a senha de um corretor")
    p_senha.add_argument("--usuario", required=True, help="Login do corretor")
    p_senha.add_argument("--senha", required=True, help="Nova senha")
    p_senha.set_defaults(func=comando_alterar_senha)

    p_status = subparsers.add_parser("status", help="Ativa ou suspende a conta de um corretor")
    p_status.add_argument("--usuario", required=True, help="Login do corretor")
    p_status.add_argument("--ativo", required=True, choices=["true", "false"], help="true para ativar, false para suspender")
    p_status.set_defaults(func=comando_status)

    return parser


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()


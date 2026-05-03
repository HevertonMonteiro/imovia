from supabase import create_client, Client
from config import settings
import os

_supabase_client: Client = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if settings.supabase_url and settings.supabase_key:
            _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
        else:
            # Modo de desenvolvimento sem Supabase
            _supabase_client = None
    return _supabase_client


async def init_db():
    """Inicializa o banco de dados criando as tabelas se não existirem"""
    supabase = get_supabase()
    if supabase is None:
        print("⚠️ Modo de desenvolvimento: Supabase não configurado")
        return
    
    # Se você quiser aplicar o esquema Postgres / RLS via Supabase,
    # use o arquivo `backend/db/schema.sql` como fonte de migração.
    # Nota: Em produção, isso deve ser feito via migrações controladas.
    print("✅ Banco de dados inicializado")


async def create_user(email: str, password: str, name: str):
    """Cria um novo usuário no Supabase Auth"""
    supabase = get_supabase()
    if supabase is None:
        return None
    
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"name": name}}
        })
        return response.user
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return None


async def authenticate_user(email: str, password: str):
    """Autentica um usuário"""
    supabase = get_supabase()
    if supabase is None:
        return None
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        print(f"Erro ao autenticar: {e}")
        return None


async def get_user(user_id: str):
    """Obtém dados do usuário"""
    supabase = get_supabase()
    if supabase is None:
        return None
    
    try:
        response = supabase.auth.get_user(user_id)
        return response.user
    except Exception as e:
        print(f"Erro ao obter usuário: {e}")
        return None


# Armazenamento em memória para desenvolvimento
import bcrypt
from datetime import datetime

_in_memory_db = {
    "users": {},
    "imobiliarias": {},
    "properties": {},
    "clients": {},
    "client_preferences": {},  # ✅ NOVO: Preferências dos clientes
    "leads": {},
    "verification_codes": {},  # Códigos de verificação de email
    "property_views": {},  # Tracking de visualizações de imóveis
    "interactions": {},    # ✅ NOVO: Interações dos clientes
    "property_clicks": {},  # Tracking de cliques em imóveis

    "lead_events": {},  # Tracking de eventos de leads
    "favorites": {},     # Favoritos dos usuários
}


# Criar admin padrão se não existir
def init_default_admin():
    db = _in_memory_db
    admin_email = "admin@imovia.com"

    # Verificar se admin já existe
    for user in db["users"].values():
        if user.get("email") == admin_email:
            return

    # Criar admin padrão
    admin_id = "admin-001"
    hashed_password = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db["users"][admin_id] = {
        "id": admin_id,
        "email": admin_email,
        "name": "Administrador Master",
        "password": hashed_password,
        "tipo": "admin_master",
        "imobiliaria_id": None,
        "ativo": True,
        "email_verified": True,
        "created_at": str(datetime.now())
    }

    print(f"✅ Admin padrão criado: {admin_email} / 123456")


def seed_data():
    """Cria dados de teste completos"""
    db = _in_memory_db
    now = str(datetime.now())
    hashed_pass = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # =====================================
    # 1. ADMIN MASTER
    # =====================================
    admin_id = "admin-001"
    db["users"][admin_id] = {
        "id": admin_id, "email": "admin@imovia.com", "name": "Admin Master",
        "password": hashed_pass, "tipo": "admin_master", "imobiliaria_id": None,
        "ativo": True, "created_at": now
    }

    # =====================================
    # 2. IMOBILIÁRIAS (criadas pelo ADMIN_MASTER)
    # =====================================
    alpha_id = "alpha-001"
    db["imobiliarias"][alpha_id] = {
        "id": alpha_id, "nome": "Imobiliária Alpha", "email": "alpha@imovia.com",
        "status": "ativo", "plano": "free", "created_at": now
    }

    beta_id = "beta-001"
    db["imobiliarias"][beta_id] = {
        "id": beta_id, "nome": "Imobiliária Beta", "email": "beta@imovia.com",
        "status": "ativo", "plano": "free", "created_at": now
    }

    # =====================================
    # 3. ADMINS DAS IMOBILIÁRIAS (criados automaticamente)
    # =====================================
    # Admin Alpha
    alpha_admin_id = "alpha-admin-001"
    db["users"][alpha_admin_id] = {
        "id": alpha_admin_id, "name": "Admin Alpha", "email": "alpha@imovia.com",
        "password": hashed_pass, "tipo": "admin_imobiliaria", "imobiliaria_id": alpha_id,
        "ativo": True, "password_set": False, "created_at": now
    }

    # Admin Beta
    beta_admin_id = "beta-admin-001"
    db["users"][beta_admin_id] = {
        "id": beta_admin_id, "name": "Admin Beta", "email": "beta@imovia.com",
        "password": hashed_pass, "tipo": "admin_imobiliaria", "imobiliaria_id": beta_id,
        "ativo": True, "password_set": False, "created_at": now
    }

    # =====================================
    # 4. CORRETORES ALPHA
    # =====================================
    corretores_alpha = [
        ("João Silva", "joao@alpha.com"),
        ("Maria Santos", "maria@alpha.com")
    ]
    for i, (nome, email) in enumerate(corretores_alpha):
        cid = f"alpha-cor{i+1:03d}"
        db["users"][cid] = {
            "id": cid, "name": nome, "email": email, "phone": f"(81) 9{9999+i}-{(i+1)*111}",
            "password": hashed_pass, "tipo": "corretor", "imobiliaria_id": alpha_id,
            "ativo": True, "password_set": False, "created_at": now
        }

    # =====================================
    # 5. CORRETORES BETA
    # =====================================
    corretores_beta = [
        ("Carlos Oliveira", "carlos@beta.com"),
        ("Ana Costa", "ana@beta.com")
    ]
    for i, (nome, email) in enumerate(corretores_beta):
        cid = f"beta-cor{i+1:03d}"
        db["users"][cid] = {
            "id": cid, "name": nome, "email": email, "phone": f"(81) 9{8888+i}-{(i+1)*222}",
            "password": hashed_pass, "tipo": "corretor", "imobiliaria_id": beta_id,
            "ativo": True, "password_set": False, "created_at": now
        }

    # =====================================
    # 6. CLIENTE TESTE
    # =====================================
    client_id = "client-001"
    db["users"][client_id] = {
        "id": client_id, "email": "cliente@teste.com", "name": "Cliente Teste",
        "password": hashed_pass, "tipo": "cliente", "imobiliaria_id": None,
        "ativo": True, "created_at": now
    }

    # =====================================
    # 7. IMÓVEIS ALPHA (5)
    # =====================================
    imoveis_alpha = [
        {"title": "Apartamento Recife", "tipo_negocio": "venda", "city": "Recife", "value": 250000},
        {"title": "Casa Olinda", "tipo_negocio": "venda", "city": "Olinda", "value": 420000},
        {"title": "Apartamento Boa Viagem", "tipo_negocio": "aluguel", "city": "Boa Viagem", "value": 1800},
        {"title": "Casa Paulista", "tipo_negocio": "aluguel", "city": "Paulista", "value": 1200},
        {"title": "Cobertura Recife", "tipo_negocio": "venda", "city": "Recife", "value": 950000}
    ]
    for i, imovel in enumerate(imoveis_alpha):
        pid = f"alpha-prop{i+1:03d}"
        db["properties"][pid] = {
            "id": pid, "user_id": f"alpha-cor001", "title": imovel["title"],
            "tipo_negocio": imovel["tipo_negocio"], "city": imovel["city"],
            "value": imovel["value"], "property_type": "apartamento",
            "status": "disponível", "images": [], "views": 0, "leads": 0,
            "imobiliaria_id": alpha_id, "created_at": now, "updated_at": now
        }

    # =====================================
    # 8. IMÓVEIS BETA (5)
    # =====================================
    imoveis_beta = [
        {"title": "Apartamento Jaboatão", "tipo_negocio": "venda", "city": "Jaboatão", "value": 320000},
        {"title": "Casa Camaragibe", "tipo_negocio": "venda", "city": "Camaragibe", "value": 280000},
        {"title": "Flat Piedade", "tipo_negocio": "aluguel", "city": "Piedade", "value": 1400},
        {"title": "Sobrado Muribeca", "tipo_negocio": "aluguel", "city": "Muribeca", "value": 2200},
        {"title": "Loft Prazeres", "tipo_negocio": "venda", "city": "Prazeres", "value": 180000}
    ]
    for i, imovel in enumerate(imoveis_beta):
        pid = f"beta-prop{i+1:03d}"
        db["properties"][pid] = {
            "id": pid, "user_id": f"beta-cor001", "title": imovel["title"],
            "tipo_negocio": imovel["tipo_negocio"], "city": imovel["city"],
            "value": imovel["value"], "property_type": "casa",
            "status": "disponível", "images": [], "views": 0, "leads": 0,
            "imobiliaria_id": beta_id, "created_at": now, "updated_at": now
        }

    print("✅ SEED COMPLETO! Dados de teste criados:")
    print(f"   👑 Admin Master: admin@imovia.com / 123456")
    print(f"   🏢 Alpha: alpha@imovia.com / 123456 (admin_imobiliaria)")
    print(f"   🏢 Beta: beta@imovia.com / 123456 (admin_imobiliaria)")
    print(f"   👥 Corretores Alpha: joao@alpha.com, maria@alpha.com")
    print(f"   👥 Corretores Beta: carlos@beta.com, ana@beta.com")
    print(f"   👤 Cliente: cliente@teste.com / 123456")
    print(f"   🏠 10 imóveis criados (5 Alpha + 5 Beta)")
    
    # =====================================
    # 6. IMÓVEIS ALPHA (5)
    # =====================================
    imoveis_alpha = [
        {"title": "Apartamento Recife", "tipo_negocio": "venda", "city": "Recife", "value": 250000},
        {"title": "Casa Olinda", "tipo_negocio": "venda", "city": "Olinda", "value": 420000},
        {"title": "Apartamento Boa Viagem", "tipo_negocio": "aluguel", "city": "Boa Viagem", "value": 1800},
        {"title": "Casa Paulista", "tipo_negocio": "aluguel", "city": "Paulista", "value": 1200},
        {"title": "Cobertura Recife", "tipo_negocio": "venda", "city": "Recife", "value": 950000}
    ]
    for i, imovel in enumerate(imoveis_alpha):
        pid = f"alpha-prop{i+1:03d}"
        db["properties"][pid] = {
            "id": pid, "user_id": f"alpha-cor001", "title": imovel["title"],
            "tipo_negocio": imovel["tipo_negocio"], "city": imovel["city"], 
            "value": imovel["value"], "property_type": "apartamento",
            "status": "disponível", "images": [], "views": 0, "leads": 0,
            "created_at": now, "updated_at": now
        }
    
    # =====================================
    # 7. IMÓVEIS BETA (5)
    # =====================================
    imoveis_beta = [
        {"title": "Apartamento Jaboatão", "tipo_negocio": "venda", "city": "Jaboatão", "value": 320000},
        {"title": "Casa Camaragibe", "tipo_negocio": "venda", "city": "Camaragibe", "value": 280000},
        {"title": "Flat Piedade", "tipo_negocio": "aluguel", "city": "Piedade", "value": 1400},
        {"title": "Sobrado Muribeca", "tipo_negocio": "aluguel", "city": "Muribeca", "value": 2200},
        {"title": "Loft Prazeres", "tipo_negocio": "venda", "city": "Prazeres", "value": 180000}
    ]
    for i, imovel in enumerate(imoveis_beta):
        pid = f"beta-prop{i+1:03d}"
        db["properties"][pid] = {
            "id": pid, "user_id": f"beta-cor001", "title": imovel["title"],
            "tipo_negocio": imovel["tipo_negocio"], "city": imovel["city"],
            "value": imovel["value"], "property_type": "casa",
            "status": "disponível", "images": [], "views": 0, "leads": 0,
            "created_at": now, "updated_at": now
        }
    
    print("✅ SEED COMPLETO! Dados de teste criados:")
    print(f"   👑 Admin: admin@imovia.com / 123456")
    print(f"   🏢 Alpha: alpha@imovia.com / 123456") 
    print(f"   🏢 Beta: beta@imovia.com / 123456")
    print(f"   👥 8 corretores + 1 cliente + 10 imóveis")


# Executar seed na inicialização (apenas se não tiver dados)
def run_seed_if_empty():
    db = _in_memory_db
    if len(db["users"]) < 5 or len(db["properties"]) == 0:
        seed_data()
        print("🔥 SEED EXECUTADO - Dados de teste carregados!")


# Inicializar admin padrão
init_default_admin()
run_seed_if_empty()


def get_memory_db():
    return _in_memory_db


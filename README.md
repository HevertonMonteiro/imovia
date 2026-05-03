# 🚀 Imovia — Plataforma Inteligente para Gestão Imobiliária

## 📌 **Visão Geral**

O **Imovia** é uma plataforma SaaS **full-stack** para gestão imobiliária com **multi-tenant** e **RBAC** avançado. Foco em performance de corretores, conversão de leads e escalabilidade SaaS.

**Hierarquia:**
```
ADMIN MASTER
   └── IMOBILIÁRIAS (Alpha, Beta...)
         └── CORRETORES
               └── LEADS/IMÓVEIS
```

---

## 🛠 **Stack Técnica** (Profissional)

| Camada | Tecnologias | Versões |
|--------|-------------|---------|
| **Frontend** | React 18 + Vite + Tailwind + Framer Motion | 🚀 Hot Reload |
| **Backend** | FastAPI + Python 3.9 + Pydantic | ✅ RBAC + JWT |
| **Banco** | SQLite (in-memory) → PostgreSQL ready | Supabase compatível |
| **Auth** | JWT + Role-based (4 níveis) | Seguro |
| **DevOps** | npm scripts + VS Code | Deploy Vercel/Railway |

---

## 🔐 **RBAC Multi-nível**

| Role | Acesso | Usuário Teste |
|------|--------|---------------|
| **Admin Master** | Tudo | `admin@imovia.com` / `123456` |
| **Admin Imobiliária** | Seus corretores + imóveis | `alpha@imovia.com` / `123456` |
| **Corretor** | Seus imóveis/leads | `joao@alpha.com` / `123456` |
| **Cliente** | Catálogo público | `cliente@teste.com` / `123456` |

**Admin Imobiliária vê:**
- Corretores da empresa
- **Imóveis dos corretores** + nome do corretor
- Leads consolidados

---

## 🚀 **Como Executar** (2min)

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (nova aba)
cd frontend
npm install
npm run dev
```

**URLs:**
- Frontend: http://localhost:5175
- Backend API: http://localhost:8000/docs

---

## 📊 **Funcionalidades Implementadas**

### **Admin Master**
```
✅ Gerenciar imobiliárias
✅ CRUD corretores global
✅ Dashboard analytics
✅ RBAC total
```

### **Admin Imobiliária** (Alpha/Beta)
```
✅ CRUD corretores da empresa
✅ Ver imóveis dos corretores + 👤 NOME
✅ Leads consolidados
✅ Métricas por corretor
```

### **Corretor**
```
✅ CRUD imóveis
✅ IA anúncios + análise imagens
✅ Leads pessoais
✅ WhatsApp 1-click
```

### **Cliente**
```
✅ Catálogo filtrável
✅ Preferências salvas
✅ Detalhes imóveis públicos
```

---

## 🤖 **IA Integrada**
```
🔥 Títulos/descrições automáticas
📸 Análise de imagens
✨ Sugestões de melhoria
📊 Score leads por IA
```

---

## 🏗 **Estrutura Código**

```
imovia/
├── backend/           # FastAPI API
│   ├── main.py        # App + Seed dados
│   ├── routers/       # Endpoints RBAC
│   └── middleware/    # Role filtering
└── frontend/          # React SPA
    ├── pages/         # Por role
    ├── context/       # Auth global
    └── services/      # API typed
```

---

## 📈 **Roadmap Produção**

```
[✅] MVP com RBAC
[ ] PostgreSQL + Supabase
[ ] Docker + Railway deploy
[ ] Stripe SaaS billing
[ ] WhatsApp Business API
[ ] Mobile PWA
```

---

## 📄 **Licença**
MIT — Open Source com amor 🇧🇷

## 👨‍💻 **Autor**
**Heverton Monteiro**  
`hevertonmonteiro@email.com`

⭐ **Star** se curtiu! 🚀

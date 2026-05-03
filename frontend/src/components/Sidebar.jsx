import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { 
  Home, 
  Building2, 
  MessageSquare, 
  BarChart3,
  Settings,
  LogOut,
  Sparkles,
  UserCog,
  Building
} from 'lucide-react'

const baseNavItems = [
  { path: '/', icon: Home, label: 'Dashboard', roles: ['admin_master', 'admin_imobiliaria', 'corretor'] },
  { path: '/properties', icon: Building2, label: 'Imóveis', roles: ['admin_master', 'admin_imobiliaria', 'corretor'] },
  { path: '/leads', icon: MessageSquare, label: 'Leads', roles: ['admin_master', 'admin_imobiliaria', 'corretor'] },
{ path: '/corretores', icon: UserCog, label: 'Corretores', roles: ['admin_master', 'admin_imobiliaria'] },
  { path: '/imobiliarias', icon: Building, label: 'Imobiliárias', roles: ['admin_master'] },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200 flex flex-col z-50">
      {/* Logo */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
            <Building2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Imovia</h1>
            <p className="text-xs text-gray-500">Gestão Inteligente</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {baseNavItems
          .filter(item => item.roles.includes(user?.tipo || ''))
          .map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
      </nav>

      {/* AI Section */}
      <div className="p-4 mx-4 mb-4 bg-gradient-to-r from-primary-500 to-accent-500 rounded-xl">
        <div className="flex items-center gap-2 text-white mb-2">
          <Sparkles className="w-5 h-5" />
          <span className="font-semibold">IA Ativa</span>
        </div>
        <p className="text-xs text-white/80">
          Geração automática de anúncios e análise de imagens
        </p>
      </div>

      {/* User Section */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-700 font-semibold">
              {user?.name?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.name || 'Usuário'}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {user?.email || 'usuario@email.com'}
            </p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sair
        </button>
      </div>
    </aside>
  )
}

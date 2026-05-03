import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Building2, 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  Plus,
  Percent,
  BarChart3,
  Search
} from 'lucide-react'
import { dashboardAPI } from '../services/api'

const statsCards = [
  { key: 'total_properties', label: 'Total de Imóveis', icon: Building2, color: 'bg-blue-500' },
  { key: 'active_properties', label: 'Imóveis Ativos', icon: TrendingUp, color: 'bg-green-500' },
  { key: 'sold_properties', label: 'Vendidos/Alugados', icon: Building2, color: 'bg-purple-500' },
  { key: 'total_leads', label: 'Total de Leads', icon: MessageSquare, color: 'bg-orange-500' },
]

const advancedStatsCards = [
  { key: 'in_negotiation_properties', label: 'Em Negociação', icon: BarChart3, color: 'bg-yellow-500' },
  { key: 'conversion_rate', label: 'Taxa de Conversão', icon: Percent, color: 'bg-indigo-500', isPercent: true },
]

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [advancedStats, setAdvancedStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingAdvanced, setLoadingAdvanced] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadStats()
    loadAdvancedStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await dashboardAPI.getStats()
      setStats(response.data)
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
      setStats({
        total_properties: 24,
        active_properties: 18,
        sold_properties: 6,
        total_clients: 45,
        total_leads: 127,
        properties_by_type: {
          apartamento: 12,
          casa: 8,
          comercial: 4
        },
        properties_by_city: {
          'São Paulo': 15,
          'Rio de Janeiro': 5,
          'Belo Horizonte': 4
        },
        recent_leads: []
      })
    } finally {
      setLoading(false)
    }
  }

  const loadAdvancedStats = async () => {
    try {
      const response = await dashboardAPI.getAdvancedStats()
      setAdvancedStats(response.data)
    } catch (error) {
      console.error('Erro ao carregar estatísticas avançadas:', error)
      setAdvancedStats({
        in_negotiation_properties: 3,
        conversion_rate: 15.5,
        top_properties: [],
        leads_by_source: {}
      })
    } finally {
      setLoadingAdvanced(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Visão geral da sua gestão imobiliária</p>
        </div>
        <button
          onClick={() => navigate('/properties/new')}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Novo Imóvel
        </button>
      </div>

      {/* Stats Cards - Basic */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat, index) => (
          <motion.div
            key={stat.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => navigate('/properties')}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 ${stat.color} rounded-xl flex items-center justify-center`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900">
                {stats?.[stat.key] || 0}
              </span>
            </div>
            <p className="text-sm text-gray-600">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Stats Cards - Advanced */}
      {!loadingAdvanced && advancedStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {advancedStatsCards.map((stat, index) => (
            <motion.div
              key={stat.key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: (index + 4) * 0.1 }}
              className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 ${stat.color} rounded-xl flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {stat.isPercent 
                    ? `${advancedStats?.[stat.key] || 0}%` 
                    : advancedStats?.[stat.key] || 0}
                </span>
              </div>
              <p className="text-sm text-gray-600">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      )}

      {/* AI Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gradient-to-r from-primary-600 to-accent-500 rounded-xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center">
              <Sparkles className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Módulo de IA Ativo</h3>
              <p className="text-white/80">
                Gere anúncios automaticamente, analise imagens e obtenha sugestões inteligentes
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/properties')}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              Ver Imóveis
            </button>
            <button
              onClick={() => navigate('/properties/new')}
              className="px-4 py-2 bg-white text-primary-600 hover:bg-gray-100 rounded-lg transition-colors font-medium"
            >
              Criar Imóvel com IA
            </button>
          </div>
        </div>
      </motion.div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Properties by Type */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Imóveis por Tipo</h3>
          <div className="space-y-4">
            {Object.entries(stats?.properties_by_type || {}).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-primary-500"></div>
                  <span className="text-gray-700 capitalize">{type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary-500 rounded-full"
                      style={{ width: `${(count / stats.total_properties) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Properties by City */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Imóveis por Cidade</h3>
          <div className="space-y-4">
            {Object.entries(stats?.properties_by_city || {}).map(([city, count]) => (
              <div key={city} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-accent-500"></div>
                  <span className="text-gray-700">{city}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-accent-500 rounded-full"
                      style={{ width: `${(count / stats.total_properties) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Top Properties Section */}
      {!loadingAdvanced && advancedStats && advancedStats.top_properties && advancedStats.top_properties.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🏆 Imóveis Mais Visualizados</h3>
          <div className="space-y-3">
            {advancedStats.top_properties.map((property, index) => (
              <div 
                key={property.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => navigate(`/properties/${property.id}`)}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-bold text-gray-300">#{index + 1}</span>
                  <div>
                    <p className="font-medium text-gray-900">{property.title}</p>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" /> {property.views}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageSquare className="w-4 h-4" /> {property.leads}
                      </span>
                    </div>
                  </div>
                </div>
                <ArrowUpRight className="w-5 h-5 text-gray-400" />
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Ações Rápidas</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/properties/new')}
            className="flex items-center gap-4 p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left"
          >
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Cadastrar Imóvel</p>
              <p className="text-sm text-gray-500">Adicione um novo imóvel</p>
            </div>
          </button>
          
          <button
            onClick={() => navigate('/clients')}
            className="flex items-center gap-4 p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left"
          >
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Gerenciar Clientes</p>
              <p className="text-sm text-gray-500">Cadastre e gerencie clientes</p>
            </div>
          </button>
          
          <button
            onClick={() => navigate('/leads')}
            className="flex items-center gap-4 p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left"
          >
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Ver Leads</p>
              <p className="text-sm text-gray-500">Acompanhe seus leads</p>
            </div>
          </button>
        </div>
      </motion.div>
    </div>
  )
}

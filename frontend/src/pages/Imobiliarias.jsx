import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Building2, 
  Plus, 
  Search,
  MoreVertical,
  Mail,
  ToggleLeft,
  Crown,
  TrendingUp,
  Users,
  MessageSquare,
  Trash2
} from 'lucide-react'
import { api, imobiliariasAPI } from '../services/api'

const getStatusColor = (status) => {
  const colors = {
    ativo: 'bg-green-100 text-green-700',
    inativo: 'bg-red-100 text-red-700',
    trial: 'bg-yellow-100 text-yellow-700'
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}

const getPlanoBadge = (plano) => {
  const badges = {
    free: 'bg-gray-100 text-gray-700',
    premium: 'bg-purple-100 text-purple-700',
    enterprise: 'bg-blue-100 text-blue-700'
  }
  return badges[plano] || 'bg-gray-100 text-gray-700'
}

export default function Imobiliarias() {
  const [imobiliarias, setImobiliarias] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedImob, setSelectedImob] = useState(null)
  const [imobStats, setImobStats] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    nome: '',
    email: ''
  })

  useEffect(() => {
    loadImobiliarias()
  }, [])

const loadImobiliarias = async () => {
    try {
      const response = await imobiliariasAPI.list()
      setImobiliarias(response.data)
    } catch (error) {
      console.error('Erro ao carregar imobiliárias:', error)
      // Dados de exemplo
      setImobiliarias([
        {
          id: '1',
          nome: 'Imobiliária Teste',
          email: 'contato@imobiliaria.com',
          status: 'ativo',
          plano: 'free',
          created_at: new Date().toISOString()
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const loadImobStats = async (imobId) => {
    try {
      const response = await imobiliariasAPI.getStats(imobId)
      setImobStats(response.data)
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    }
  }

  const handleSelectImob = async (imob) => {
    setSelectedImob(imob)
    await loadImobStats(imob.id)
  }

  const handleDeleteImob = async (imobId) => {
    if (!window.confirm('Tem certeza que deseja deletar esta imobiliária?')) return
    
    try {
      await imobiliariasAPI.delete(imobId)
      setImobiliarias(imobiliarias.filter(i => i.id !== imobId))
      setSelectedImob(null)
    } catch (error) {
      console.error('Erro ao deletar imobiliária:', error)
      alert(error.response?.data?.detail || 'Erro ao deletar imobiliária')
    }
  }

const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await imobiliariasAPI.create(formData)
      setShowForm(false)
      setFormData({ nome: '', email: '' })
      loadImobiliarias()
    } catch (error) {
      console.error('Erro ao criar imobiliária:', error)
    }
  }

  const handleActivate = async (imobId) => {
    try {
      await imobiliariasAPI.activate(imobId)
      loadImobiliarias()
    } catch (error) {
      console.error('Erro ao ativar:', error)
    }
  }

  const handleDeactivate = async (imobId) => {
    try {
      await imobiliariasAPI.deactivate(imobId)
      loadImobiliarias()
    } catch (error) {
      console.error('Erro ao desativar:', error)
    }
  }

  const handleUpgrade = async (imobId, plano) => {
    try {
      await imobiliariasAPI.upgrade(imobId, plano)
      loadImobiliarias()
    } catch (error) {
      console.error('Erro ao fazer upgrade:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Imobiliárias</h1>
          <p className="text-gray-600 mt-1">{imobiliarias.length} imobiliárias cadastradas</p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nova Imobiliária
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar imobiliárias..."
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
        />
      </div>

      {/* Form */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Nova Imobiliária</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nome *
              </label>
              <input
                type="text"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                placeholder="Nome da imobiliária"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="email@imobiliaria.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                required
              />
            </div>

            <div className="md:col-span-2 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              >
                Criar Imobiliária
              </button>
            </div>
          </form>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Imobiliárias */}
        <div className="lg:col-span-1 space-y-4">
          {imobiliarias.map((imob) => (
            <motion.div
              key={imob.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => handleSelectImob(imob)}
              className={`bg-white rounded-xl p-4 border cursor-pointer transition-all ${
                selectedImob?.id === imob.id 
                  ? 'border-primary-500 shadow-md' 
                  : 'border-gray-100 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{imob.nome}</h3>
                    <p className="text-sm text-gray-500">{imob.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs ${getPlanoBadge(imob.plano)}`}>
                    {imob.plano}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(imob.status)}`}>
                    {imob.status}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}

          {imobiliarias.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-100">
              <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Nenhuma imobiliária</h3>
              <p className="text-gray-600">Cadastre a primeira imobiliária</p>
            </div>
          )}
        </div>

        {/* Detalhes da Imobiliária */}
        <div className="lg:col-span-2">
          {selectedImob ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-xl border border-gray-100 shadow-sm"
            >
              {/* Header */}
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-primary-100 rounded-xl flex items-center justify-center">
                      <Building2 className="w-8 h-8 text-primary-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{selectedImob.nome}</h2>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Mail className="w-4 h-4" />
                        {selectedImob.email}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {selectedImob.status === 'ativo' ? (
                      <button 
                        onClick={() => handleDeactivate(selectedImob.id)}
                        className="px-3 py-1 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        Desativar
                      </button>
                    ) : (
                      <button 
                        onClick={() => handleActivate(selectedImob.id)}
                        className="px-3 py-1 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        Ativar
                      </button>
                    )}
                    <button 
                      onClick={() => handleDeleteImob(selectedImob.id)}
                      className="px-3 py-1 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors flex items-center gap-1"
                    >
                      <Trash2 className="w-4 h-4" />
                      Deletar
                    </button>
                  </div>
                </div>
              </div>

              {/* Stats */}
              {imobStats && (
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Estatísticas
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-blue-600 mb-1">
                        <Users className="w-5 h-5" />
                        <span className="text-sm">Corretores</span>
                      </div>
                      <div className="text-2xl font-bold text-blue-900">
                        {imobStats.total_corretores}
                      </div>
                    </div>
                    <div className="bg-green-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-green-600 mb-1">
                        <Building2 className="w-5 h-5" />
                        <span className="text-sm">Imóveis</span>
                      </div>
                      <div className="text-2xl font-bold text-green-900">
                        {imobStats.total_imoveis}
                      </div>
                    </div>
                    <div className="bg-orange-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-orange-600 mb-1">
                        <MessageSquare className="w-5 h-5" />
                        <span className="text-sm">Leads</span>
                      </div>
                      <div className="text-2xl font-bold text-orange-900">
                        {imobStats.total_leads}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Planos */}
              <div className="p-6 border-t border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Planos
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <button
                    onClick={() => handleUpgrade(selectedImob.id, 'free')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      selectedImob.plano === 'free'
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-semibold">Free</div>
                    <div className="text-sm text-gray-500">Grátis</div>
                  </button>
                  <button
                    onClick={() => handleUpgrade(selectedImob.id, 'premium')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      selectedImob.plano === 'premium'
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Crown className="w-5 h-5 text-purple-600 mb-1" />
                    <div className="font-semibold">Premium</div>
                    <div className="text-sm text-gray-500">R$ 97/mês</div>
                  </button>
                  <button
                    onClick={() => handleUpgrade(selectedImob.id, 'enterprise')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      selectedImob.plano === 'enterprise'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <TrendingUp className="w-5 h-5 text-blue-600 mb-1" />
                    <div className="font-semibold">Enterprise</div>
                    <div className="text-sm text-gray-500">R$ 297/mês</div>
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="bg-gray-50 rounded-xl p-12 text-center">
              <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Selecione uma imobiliária
              </h3>
              <p className="text-gray-600">
                Clique em uma imobiliária na lista para ver seus detalhes
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

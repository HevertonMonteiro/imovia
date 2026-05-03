import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  Plus, 
  Building2, 
  MessageSquare, 
  TrendingUp,
  Search,
  MoreVertical,
  Mail,
  Phone,
  ToggleLeft,
  ToggleRight,
  Calendar,
  Trash2,
  Lock,
  Unlock
} from 'lucide-react'
import { dashboardAPI, corretoresAPI } from '../services/api'

export default function Corretores() {
  const [corretores, setCorretores] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCorretor, setSelectedCorretor] = useState(null)
  const [corretorStats, setCorretorStats] = useState(null)
  const [showMenu, setShowMenu] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [showNewCorretorModal, setShowNewCorretorModal] = useState(false)
  const [newCorretorForm, setNewCorretorForm] = useState({
    name: '',
    email: '',
    phone: ''
  })
  const [creatingCorretor, setCreatingCorretor] = useState(false)

  useEffect(() => {
    loadCorretores()
  }, [])

  const loadCorretores = async () => {
    try {
      const response = await dashboardAPI.listCorretores()
      setCorretores(response.data)
    } catch (error) {
      console.error('Erro ao carregar corretores:', error)
      // Dados de exemplo
      setCorretores([
        {
          id: '1',
          name: 'João Silva',
          email: 'joao@imobiliaria.com',
          ativo: true,
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Maria Santos',
          email: 'maria@imobiliaria.com',
          ativo: true,
          created_at: new Date().toISOString()
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const loadCorretorStats = async (corretorId) => {
    try {
      const response = await dashboardAPI.getCorretorStats(corretorId)
      setCorretorStats(response.data)
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    }
  }

  const handleSelectCorretor = async (corretor) => {
    setSelectedCorretor(corretor)
    await loadCorretorStats(corretor.id)
  }

  const handleDeleteCorretor = async (corretorId) => {
    if (!window.confirm('Tem certeza que deseja deletar este corretor?')) return
    
    setDeletingId(corretorId)
    try {
      await corretoresAPI.delete(corretorId)
      setCorretores(corretores.filter(c => c.id !== corretorId))
      setSelectedCorretor(null)
      setShowMenu(null)
    } catch (error) {
      console.error('Erro ao deletar corretor:', error)
      alert(error.response?.data?.detail || 'Erro ao deletar corretor')
    } finally {
      setDeletingId(null)
    }
  }

  const handleToggleCorretor = async (corretorId, currentStatus) => {
    try {
      if (currentStatus) {
        await corretoresAPI.deactivate(corretorId)
      } else {
        await corretoresAPI.activate(corretorId)
      }
      
      setCorretores(corretores.map(c => 
        c.id === corretorId ? { ...c, ativo: !c.ativo } : c
      ))
      setSelectedCorretor(prev => prev?.id === corretorId ? { ...prev, ativo: !prev.ativo } : prev)
      setShowMenu(null)
    } catch (error) {
      console.error('Erro ao alterar status do corretor:', error)
    }
  }

  const handleCreateCorretor = async (e) => {
    e.preventDefault()
    if (!newCorretorForm.name || !newCorretorForm.email || !newCorretorForm.phone) {
      alert('Preencha todos os campos')
      return
    }
    
    setCreatingCorretor(true)
    try {
      await corretoresAPI.create(newCorretorForm)
      setShowNewCorretorModal(false)
      setNewCorretorForm({name: '', email: '', phone: ''})
      loadCorretores()
      alert('✅ Corretor cadastrado com sucesso!\nSenha padrão: 123456')
    } catch (error) {
      console.error('Erro ao criar corretor:', error)
      alert(error.response?.data?.detail || 'Erro ao cadastrar corretor')
    } finally {
      setCreatingCorretor(false)
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
          <h1 className="text-2xl font-bold text-gray-900">Corretores</h1>
          <p className="text-gray-600 mt-1">{corretores.length} corretores cadastrados</p>
        </div>
        <button 
          onClick={() => setShowNewCorretorModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Cadastrar Corretor
        </button>

        {/* Modal Novo Corretor */}
        {showNewCorretorModal && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowNewCorretorModal(false)}
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} 
              animate={{ scale: 1, opacity: 1 }} 
              className="bg-white rounded-2xl p-8 max-w-md w-full max-h-[90vh] overflow-y-auto"
              onClick={e => e.stopPropagation()}
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Novo Corretor</h2>
              
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nome Completo *
                  </label>
                  <input
                    type="text"
                    value={newCorretorForm.name}
                    onChange={(e) => setNewCorretorForm({...newCorretorForm, name: e.target.value})}
                    placeholder="João Silva"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={newCorretorForm.email}
                    onChange={(e) => setNewCorretorForm({...newCorretorForm, email: e.target.value})}
                    placeholder="joao@imobiliaria.com"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Telefone *
                  </label>
                  <input
                    type="tel"
                    value={newCorretorForm.phone}
                    onChange={(e) => setNewCorretorForm({...newCorretorForm, phone: e.target.value})}
                    placeholder="(81) 99999-9999"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                    required
                  />
                </div>
                
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowNewCorretorModal(false)}
                    className="flex-1 px-6 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors text-gray-700 font-medium"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    onClick={handleCreateCorretor}
                    disabled={creatingCorretor}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl transition-colors font-medium disabled:opacity-50"
                  >
                    {creatingCorretor ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Criando...
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4" />
                        Cadastrar
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar corretores..."
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Corretores */}
        <div className="lg:col-span-1 space-y-4">
          {corretores.map((corretor) => (
            <motion.div
              key={corretor.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => handleSelectCorretor(corretor)}
              className={`bg-white rounded-xl p-4 border cursor-pointer transition-all ${
                selectedCorretor?.id === corretor.id 
                  ? 'border-primary-500 shadow-md' 
                  : 'border-gray-100 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-primary-700 font-bold text-lg">
                    {corretor.name.charAt(0)}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{corretor.name}</h3>
                  <p className="text-sm text-gray-500">{corretor.email}</p>
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  corretor.ativo ? 'bg-green-500' : 'bg-gray-300'
                }`} />
              </div>
            </motion.div>
          ))}

          {corretores.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-100">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Nenhum corretor encontrado</h3>
              <p className="text-gray-600">Cadastre corretores para gerenciar sua equipe</p>
            </div>
          )}
        </div>

        {/* Detalhes do Corretor */}
        <div className="lg:col-span-2">
          {selectedCorretor ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-xl border border-gray-100 shadow-sm"
            >
              {/* Header */}
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-primary-700 font-bold text-2xl">
                        {selectedCorretor.name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{selectedCorretor.name}</h2>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Mail className="w-4 h-4" />
                        {selectedCorretor.email}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Calendar className="w-4 h-4" />
                        Desde {formatDate(selectedCorretor.created_at)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <button 
                        onClick={() => setShowMenu(showMenu === selectedCorretor.id ? null : selectedCorretor.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>
                      
                      {/* Menu Dropdown */}
                      {showMenu === selectedCorretor.id && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className="absolute right-0 top-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
                        >
                          <button
                            onClick={() => handleToggleCorretor(selectedCorretor.id, selectedCorretor.ativo)}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50 transition-colors text-left border-b border-gray-100 last:border-b-0"
                          >
                            {selectedCorretor.ativo ? (
                              <>
                                <Lock className="w-4 h-4 text-orange-500" />
                                <span>Desativar</span>
                              </>
                            ) : (
                              <>
                                <Unlock className="w-4 h-4 text-green-500" />
                                <span>Ativar</span>
                              </>
                            )}
                          </button>
                          <button
                            onClick={() => handleDeleteCorretor(selectedCorretor.id)}
                            disabled={deletingId === selectedCorretor.id}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-red-50 transition-colors text-left text-red-600 disabled:opacity-50"
                          >
                            <Trash2 className="w-4 h-4" />
                            <span>{deletingId === selectedCorretor.id ? 'Deletando...' : 'Deletar'}</span>
                          </button>
                        </motion.div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Stats */}
              {corretorStats && (
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Desempenho
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-blue-600 mb-1">
                        <Building2 className="w-5 h-5" />
                        <span className="text-sm">Imóveis</span>
                      </div>
                      <div className="text-2xl font-bold text-blue-900">
                        {corretorStats.total_properties}
                      </div>
                    </div>
                    <div className="bg-green-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-green-600 mb-1">
                        <TrendingUp className="w-5 h-5" />
                        <span className="text-sm">Ativos</span>
                      </div>
                      <div className="text-2xl font-bold text-green-900">
                        {corretorStats.active_properties}
                      </div>
                    </div>
                    <div className="bg-purple-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-purple-600 mb-1">
                        <MessageSquare className="w-5 h-5" />
                        <span className="text-sm">Vendidos</span>
                      </div>
                      <div className="text-2xl font-bold text-purple-900">
                        {corretorStats.sold_properties}
                      </div>
                    </div>
                    <div className="bg-orange-50 rounded-xl p-4 col-span-2">
                      <div className="flex items-center gap-2 text-orange-600 mb-1">
                        <TrendingUp className="w-5 h-5" />
                        <span className="text-sm">Taxa de Conversão</span>
                      </div>
                      <div className="text-2xl font-bold text-orange-900">
                        {corretorStats.conversion_rate}%
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <div className="bg-gray-50 rounded-xl p-12 text-center">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Selecione um corretor
              </h3>
              <p className="text-gray-600">
                Clique em um corretor na lista para ver seus detalhes
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

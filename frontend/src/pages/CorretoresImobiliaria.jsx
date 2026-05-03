import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { corretoresAPI } from '../services/api'
import { User, Mail, Phone, CheckCircle, X, Plus } from 'lucide-react'

export default function CorretoresImobiliaria() {
  const { user } = useAuth()
  const [corretores, setCorretores] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  })

  useEffect(() => {
    loadCorretores()
  }, [])

  const loadCorretores = async () => {
    try {
      const response = await corretoresAPI.list()
      setCorretores(response.data)
    } catch (error) {
      console.error('Erro ao carregar corretores:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await corretoresAPI.create(formData)
      setShowForm(false)
      setFormData({ name: '', email: '', phone: '' })
      loadCorretores()
    } catch (error) {
      console.error('Erro ao criar corretor:', error)
    }
  }

  const toggleStatus = async (corretorId) => {
    try {
      const corretor = corretores.find(c => c.id === corretorId)
      await corretoresAPI.update(corretorId, { ativo: !corretor.ativo })
      loadCorretores()
    } catch (error) {
      console.error('Erro ao alterar status:', error)
    }
  }

  const deleteCorretor = async (corretorId) => {
    if (confirm('Confirma exclusão?')) {
      try {
        await corretoresAPI.delete(corretorId)
        loadCorretores()
      } catch (error) {
        console.error('Erro ao excluir:', error)
      }
    }
  }

  if (loading) return <div>Carregando...</div>

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Corretores</h1>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" />
          Novo Corretor
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Novo Corretor</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              placeholder="Nome completo"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="p-3 border rounded-lg focus:ring-2 focus:ring-primary-500"
              required
            />
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="p-3 border rounded-lg focus:ring-2 focus:ring-primary-500"
              required
            />
            <input
              placeholder="Telefone"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="p-3 border rounded-lg focus:ring-2 focus:ring-primary-500"
            />
            <div className="md:col-span-3 flex gap-2">
              <button type="submit" className="flex-1 bg-primary-600 text-white p-3 rounded-lg hover:bg-primary-700">
                Criar
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="flex-1 bg-gray-200 p-3 rounded-lg hover:bg-gray-300"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-4 text-left font-semibold">Nome</th>
              <th className="p-4 text-left font-semibold">Email</th>
              <th className="p-4 text-left font-semibold">Telefone</th>
              <th className="p-4 text-left font-semibold">Status</th>
              <th className="p-4 text-left font-semibold">Ações</th>
            </tr>
          </thead>
          <tbody>
            {corretores.map((c) => (
              <tr key={c.id} className="border-t hover:bg-gray-50">
                <td className="p-4 font-medium">{c.name}</td>
                <td className="p-4">{c.email}</td>
                <td className="p-4">{c.phone}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    c.ativo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {c.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex gap-2">
                    <button
                      onClick={() => toggleStatus(c.id)}
                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                    >
                      {c.ativo ? 'Desativar' : 'Ativar'}
                    </button>
                    <button
                      onClick={() => deleteCorretor(c.id)}
                      className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                    >
                      Excluir
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


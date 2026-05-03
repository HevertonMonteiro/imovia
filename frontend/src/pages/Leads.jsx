import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  Mail,
  Phone,
  Trash2,
  Loader2,
  AlertTriangle,
  Building2,
  ArrowRight
} from 'lucide-react'
import { leadsAPI } from '../services/api'

export default function Leads() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadLeads()
  }, [])

  const loadLeads = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await leadsAPI.list()
      setLeads(response.data || [])
    } catch (err) {
      console.error('Erro ao carregar leads:', err)
      setError('Não foi possível carregar os leads no momento.')
    } finally {
      setLoading(false)
    }
  }

  const filteredLeads = leads.filter((lead) => {
    const query = searchQuery.toLowerCase()
    return (
      lead.client_name?.toLowerCase().includes(query) ||
      lead.client_email?.toLowerCase().includes(query) ||
      lead.property_id?.toString().includes(query)
    )
  })

  const formatDate = (value) => {
    if (!value) return '-'
    return new Date(value).toLocaleDateString('pt-BR')
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-600 mt-1">Gerencie todos os contatos e oportunidades de venda.</p>
        </div>

        <div className="w-full md:w-80">
          <label className="relative block">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Buscar por cliente, email ou imóvel"
              className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            />
          </label>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-10 h-10 text-primary-600 animate-spin" />
        </div>
      ) : error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </div>
      ) : !filteredLeads.length ? (
        <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-gray-600">
          <Building2 className="mx-auto mb-4 h-12 w-12 text-primary-600" />
          <p className="text-lg font-medium">Nenhum lead encontrado</p>
          <p className="mt-2 text-sm text-gray-500">Aguarde novos contatos ou ajuste os filtros de pesquisa.</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {filteredLeads.map((lead) => (
            <motion.div
              key={lead.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
              className="bg-white rounded-3xl border border-gray-200 p-6 shadow-sm"
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <div className="h-11 w-11 rounded-2xl bg-primary-100 flex items-center justify-center text-primary-700 font-semibold">
                      {lead.client_name?.charAt(0) || '?'}
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">{lead.client_name || 'Cliente sem nome'}</h2>
                      <p className="text-sm text-gray-500">{lead.client_email || 'Sem email'}</p>
                    </div>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-3">
                    <div className="rounded-2xl bg-gray-50 p-4">
                      <p className="text-xs uppercase tracking-wide text-gray-500">Imóvel</p>
                      <p className="mt-1 font-medium text-gray-900">{lead.property_id || '-'}</p>
                    </div>
                    <div className="rounded-2xl bg-gray-50 p-4">
                      <p className="text-xs uppercase tracking-wide text-gray-500">Telefone</p>
                      <p className="mt-1 text-gray-900">{lead.client_phone || '-'}</p>
                    </div>
                    <div className="rounded-2xl bg-gray-50 p-4">
                      <p className="text-xs uppercase tracking-wide text-gray-500">Data</p>
                      <p className="mt-1 text-gray-900">{formatDate(lead.created_at || lead.data_criacao)}</p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={() => navigate(`/imovel/${lead.property_id}`)}
                    className="inline-flex items-center gap-2 rounded-full bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700"
                  >
                    <ArrowRight className="w-4 h-4" />
                    Ver imóvel
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
                  >
                    <Mail className="w-4 h-4" />
                    Contato
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

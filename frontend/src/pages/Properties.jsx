import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Building2, 
  Plus, 
  Search, 
  Filter,
  MapPin,
  Bed,
  Bath,
  Square,
  Car,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  Sparkles
} from 'lucide-react'
import { propertiesAPI } from '../services/api'

const propertyTypes = [
  { value: '', label: 'Todos os tipos' },
  { value: 'apartamento', label: 'Apartamento' },
  { value: 'casa', label: 'Casa' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'terreno', label: 'Terreno' },
  { value: 'escritório', label: 'Escritório' },
]

const propertyStatuses = [
  { value: '', label: 'Todos os status' },
  { value: 'disponível', label: 'Disponível' },
  { value: 'reservado', label: 'Reservado' },
  { value: 'vendido', label: 'Vendido' },
  { value: 'alugado', label: 'Alugado' },
]

export default function Properties() {
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchParams, setSearchParams] = useSearchParams()
  const [filters, setFilters] = useState({
    type: searchParams.get('type') || '',
    status: searchParams.get('status') || '',
    search: searchParams.get('search') || '',
  })
  const navigate = useNavigate()

  useEffect(() => {
    loadProperties()
  }, [filters])

  const loadProperties = async () => {
    try {
      const params = {}
      if (filters.type) params.property_type = filters.type
      if (filters.status) params.status = filters.status
      
      const response = await propertiesAPI.list(params)
      setProperties(response.data)
    } catch (error) {
      console.error('Erro ao carregar imóveis:', error)
      // Dados de exemplo
      setProperties([
        {
          id: '1',
          title: 'Apartamento Moderno Centro',
          description: 'Apartamento com 2 quartos, 1 banheiro, 80m²',
          property_type: 'apartamento',
          value: 450000,
          address: 'Av. Paulista, 1000',
          city: 'São Paulo',
          state: 'SP',
          bedrooms: 2,
          bathrooms: 1,
          area: 80,
          garage_spaces: 1,
          status: 'disponível',
          images: [],
          views: 156,
          clicks: 23,
          leads: 5,
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          title: 'Casa com Jardim',
          description: 'Casa térrea com 3 quartos, 2 banheiros',
          property_type: 'casa',
          value: 850000,
          address: 'Rua das Flores, 50',
          city: 'São Paulo',
          state: 'SP',
          bedrooms: 3,
          bathrooms: 2,
          area: 150,
          garage_spaces: 2,
          status: 'disponível',
          images: [],
          views: 234,
          clicks: 45,
          leads: 12,
          created_at: new Date().toISOString()
        },
        {
          id: '3',
          title: 'Sala Comercial',
          description: 'Sala comercial em edifício corporativo',
          property_type: 'comercial',
          value: 320000,
          address: 'Av. Brasil, 500',
          city: 'Rio de Janeiro',
          state: 'RJ',
          bedrooms: 0,
          bathrooms: 1,
          area: 45,
          garage_spaces: 1,
          status: 'vendido',
          images: [],
          views: 89,
          clicks: 12,
          leads: 3,
          created_at: new Date().toISOString()
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleDelete = async (id) => {
    if (confirm('Tem certeza que deseja excluir este imóvel?')) {
      try {
        await propertiesAPI.delete(id)
        loadProperties()
      } catch (error) {
        console.error('Erro ao excluir:', error)
      }
    }
  }

  const formatValue = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value)
  }

  const getStatusColor = (status) => {
    const colors = {
      'disponível': 'bg-green-100 text-green-700',
      'reservado': 'bg-yellow-100 text-yellow-700',
      'vendido': 'bg-purple-100 text-purple-700',
      'alugado': 'bg-blue-100 text-blue-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
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
          <h1 className="text-2xl font-bold text-gray-900">Imóveis</h1>
          <p className="text-gray-600 mt-1">{properties.length} imóveis cadastrados</p>
        </div>
        <button
          onClick={() => navigate('/properties/new')}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Novo Imóvel
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar imóveis..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              />
            </div>
          </div>
          <select
            value={filters.type}
            onChange={(e) => handleFilterChange('type', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            {propertyTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            {propertyStatuses.map(status => (
              <option key={status.value} value={status.value}>{status.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Properties Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {properties.map((property, index) => (
          <motion.div
            key={property.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden"
          >
            {/* Image */}
            <div className="h-48 bg-gradient-to-br from-primary-100 to-accent-100 flex items-center justify-center relative">
              <Building2 className="w-16 h-16 text-primary-400" />
              {property.images?.length > 0 && (
                <img 
                  src={property.images[0]} 
                  alt={property.title}
                  className="absolute inset-0 w-full h-full object-cover"
                />
              )}
              <div className="absolute top-3 right-3">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(property.status)}`}>
                  {property.status}
                </span>
              </div>
            </div>

            {/* Content */}
            <div className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900 line-clamp-1">{property.title}</h3>
                <span className="text-lg font-bold text-primary-600">
                  {formatValue(property.value)}
                </span>
              </div>

              <div className="flex items-center gap-1 text-gray-500 text-sm mb-3">
                <MapPin className="w-4 h-4" />
                <span className="line-clamp-1">{property.address}, {property.city}</span>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                {property.bedrooms > 0 && (
                  <div className="flex items-center gap-1">
                    <Bed className="w-4 h-4" />
                    <span>{property.bedrooms}</span>
                  </div>
                )}
                {property.bathrooms > 0 && (
                  <div className="flex items-center gap-1">
                    <Bath className="w-4 h-4" />
                    <span>{property.bathrooms}</span>
                  </div>
                )}
                {property.area > 0 && (
                  <div className="flex items-center gap-1">
                    <Square className="w-4 h-4" />
                    <span>{property.area}m²</span>
                  </div>
                )}
                {property.garage_spaces > 0 && (
                  <div className="flex items-center gap-1">
                    <Car className="w-4 h-4" />
                    <span>{property.garage_spaces}</span>
                  </div>
                )}
                {property.corretor_nome && (
                  <div className="flex items-center gap-1 text-primary-600 font-medium">
                    <User className="w-4 h-4" />
                    <span>{property.corretor_nome}</span>
                  </div>
                )}
              </div>

              {/* Stats */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    <span>{property.views}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Sparkles className="w-4 h-4" />
                    <span>{property.leads}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    to={`/properties/${property.id}`}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                  </Link>
                  <Link
                    to={`/properties/${property.id}/edit`}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(property.id)}
                    className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {properties.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Building2 className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Nenhum imóvel encontrado</h3>
          <p className="text-gray-600 mb-4">Comece cadastrando seu primeiro imóvel</p>
          <button
            onClick={() => navigate('/properties/new')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Novo Imóvel
          </button>
        </div>
      )}
    </div>
  )
}
import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, MapPin, Bed, Bath, Car, Home, Filter, X, ChevronDown, User, LogOut, Building } from 'lucide-react'
import { publicApi } from '../services/api'
import { useAuth } from '../context/AuthContext'

function Catalogo() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [filters, setFilters] = useState({
    property_type: '',
    city: '',
    state: '',
    min_value: '',
    max_value: '',
    bedrooms: '',
    bathrooms: ''
  })
  const [showFilters, setShowFilters] = useState(false)
  const [filterOptions, setFilterOptions] = useState(null)

  // Funções de usuário
  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const goToProfile = () => {
    navigate('/perfil')
  }

  // Load properties on mount
  useEffect(() => {
    loadProperties()
    loadFilterOptions()
  }, [])

  // Reload when filters change
  useEffect(() => {
    loadProperties()
  }, [filters])

  const loadProperties = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.property_type) params.property_type = filters.property_type
      if (filters.city) params.city = filters.city
      if (filters.state) params.state = filters.state
      if (filters.min_value) params.min_value = filters.min_value
      if (filters.max_value) params.max_value = filters.max_value
      if (filters.bedrooms) params.bedrooms = filters.bedrooms
      if (filters.bathrooms) params.bathrooms = filters.bathrooms

      const response = await publicApi.get('/public/properties', { params })
      setProperties(response.data)
    } catch (error) {
      console.error('Erro ao carregar imóveis:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadFilterOptions = async () => {
    try {
      const response = await publicApi.get('/public/filters/options')
      setFilterOptions(response.data)
    } catch (error) {
      console.error('Erro ao carregar opções de filtro:', error)
    }
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 0
    }).format(price)
  }

  const clearFilters = () => {
    setFilters({
      property_type: '',
      city: '',
      state: '',
      min_value: '',
      max_value: '',
      bedrooms: '',
      bathrooms: ''
    })
  }

  const getPropertyTypeLabel = (type) => {
    const labels = {
      apartamento: 'Apartamento',
      casa: 'Casa',
      comercial: 'Comercial',
      terreno: 'Terreno',
      escritório: 'Escritório',
      garagem: 'Garagem'
    }
    return labels[type] || type
  }

return (
    <div className="min-h-screen bg-gray-50">
      {/* Header com Menu do Usuário */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        {/*.Top Bar - Usuário */}
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Building className="w-6 h-6" />
            <span className="font-bold text-lg">Imovia</span>
          </div>
          
          {/* user Menu */}
          {isAuthenticated ? (
            <div className="relative">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
              >
                <User className="w-5 h-5" />
                <span className="text-sm">{user?.name || 'Minha Conta'}</span>
              </button>
              
              {/* Dropdown do Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
                  <button 
                    onClick={goToProfile}
                    className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <User className="w-4 h-4" />
                    Meu Perfil
                  </button>
                  <button 
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    Sair
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link 
                to="/login"
                className="text-white hover:text-primary-200 font-medium"
              >
                Entrar
              </Link>
              <Link 
                to="/register"
                className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                Criar Conta
              </Link>
            </div>
          )}
        </div>
        
        {/* Título Principal */}
        <div className="container mx-auto px-4 pb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            🏠 Encontre seu Imóvel Ideal
          </h1>
          <p className="text-primary-100 text-lg">
            Explore nossa seleção de imóveis com descrições geradas por IA
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow-md py-4 sticky top-0 z-10">
        <div className="container mx-auto px-4">
          {/* Mobile Filter Toggle */}
          <button 
            className="md:hidden flex items-center gap-2 text-gray-600"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={20} />
            <span>Filtros</span>
            <ChevronDown size={20} className={`transform transition ${showFilters ? 'rotate-180' : ''}`} />
          </button>

          {/* Filters Panel */}
          <div className={`md:block ${showFilters ? 'block' : 'hidden'} mt-4 md:mt-0`}>
            <div className="grid grid-cols-2 md:grid-cols-7 gap-4">
              {/* Property Type */}
              <select
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.property_type}
                onChange={(e) => setFilters({ ...filters, property_type: e.target.value })}
              >
                <option value="">Tipo</option>
                {filterOptions?.property_types?.map(type => (
                  <option key={type} value={type}>{getPropertyTypeLabel(type)}</option>
                ))}
              </select>

              {/* State */}
              <select
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.state}
                onChange={(e) => setFilters({ ...filters, state: e.target.value, city: '' })}
              >
                <option value="">Estado</option>
                {filterOptions?.cities_by_state && Object.keys(filterOptions.cities_by_state).map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>

              {/* City */}
              <select
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.city}
                onChange={(e) => setFilters({ ...filters, city: e.target.value })}
                disabled={!filters.state}
              >
                <option value="">Cidade</option>
                {filters.state && filterOptions?.cities_by_state?.[filters.state]?.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>

{/* Min Price - Input Numérico */}
              <div className="relative">
                <input
                  type="number"
                  placeholder="Mín (R$)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                  value={filters.min_value}
                  onChange={(e) => setFilters({ ...filters, min_value: e.target.value })}
                />
              </div>

              {/* Max Price - Input Numérico */}
              <div className="relative">
                <input
                  type="number"
                  placeholder="Máx (R$)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                  value={filters.max_value}
                  onChange={(e) => setFilters({ ...filters, max_value: e.target.value })}
                />
              </div>

              {/* Bedrooms */}
              <select
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.bedrooms}
                onChange={(e) => setFilters({ ...filters, bedrooms: e.target.value })}
              >
                <option value="">Quartos</option>
                <option value="1">1+ quarto</option>
                <option value="2">2+ quartos</option>
                <option value="3">3+ quartos</option>
                <option value="4">4+ quartos</option>
              </select>

              {/* Clear Filters */}
              <button
                onClick={clearFilters}
                className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg border border-red-200"
              >
                <X size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Properties Grid */}
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : properties.length === 0 ? (
          <div className="text-center py-20">
            <Home size={64} className="mx-auto text-gray-300 mb-4" />
            <h2 className="text-xl text-gray-600 mb-2">Nenhum imóvel encontrado</h2>
            <p className="text-gray-500">Tente ajustar os filtros para ver mais resultados</p>
          </div>
        ) : (
          <>
            <p className="text-gray-600 mb-6">{properties.length} imóvel(is) encontrado(s)</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {properties.map(property => (
                <Link 
                  key={property.id} 
                  to={`/imovel/${property.id}`}
                  className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow group"
                >
                  {/* Image */}
                  <div className="relative h-48 bg-gray-200">
                    {property.images && property.images.length > 0 ? (
                      <img 
                        src={property.images[0]} 
                        alt={property.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Home size={48} className="text-gray-300" />
                      </div>
                    )}
                    {/* Badge */}
                    <div className="absolute top-2 left-2 bg-primary-600 text-white text-xs font-bold px-2 py-1 rounded">
                      {getPropertyTypeLabel(property.property_type)}
                    </div>
                    {/* Price */}
                    <div className="absolute bottom-2 right-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded text-primary-700 font-bold">
                      {formatPrice(property.value)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <h3 className="font-semibold text-lg text-gray-800 mb-2 line-clamp-1">
                      {property.ai_title || property.title}
                    </h3>
                    
                    <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                      {property.ai_description || property.description}
                    </p>

                    <div className="flex items-center gap-4 text-gray-500 text-sm mb-4">
                      <span className="flex items-center gap-1">
                        <Bed size={16} />
                        {property.bedrooms} quart.
                      </span>
                      <span className="flex items-center gap-1">
                        <Bath size={16} />
                        {property.bathrooms} banh.
                      </span>
                      <span className="flex items-center gap-1">
                        <Car size={16} />
                        {property.garage_spaces} vagas
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-gray-500 text-sm">
                      <MapPin size={16} />
                      <span>{property.city}, {property.state}</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>

{/* CTA */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-12">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold mb-4">Não encontrou o que procurava?</h2>
          <p className="text-primary-100 mb-6">
            Configure suas preferências e seja avisado quando houver imóveis matching
          </p>
          <div className="flex justify-center gap-4">
            <Link 
              to="/preferencias"
              className="inline-block bg-white text-primary-600 font-semibold px-6 py-3 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Minhas Preferências
            </Link>
            <Link 
              to="/catalogo"
              className="inline-block bg-primary-500 text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary-400 transition-colors"
            >
              Ver Catálogo
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Catalogo

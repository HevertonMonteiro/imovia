import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { MapPin, Bed, Bath, AreaChart, Target, CheckCircle, Loader2 } from 'lucide-react'
import { publicApi, api } from '../services/api'

function Preferencias() {
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  
  const [preferences, setPreferences] = useState({
    property_type: '',
    city: '',
    state: '',
    min_value: '',
    max_value: '',
    bedrooms: '',
    bathrooms: '',
    min_area: '',
    max_area: '',
    goal: 'comprar'
  })
  
  const [filterOptions, setFilterOptions] = useState(null)

  useEffect(() => {
    loadFilterOptions()
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('token')
    if (token) {
      setIsLoggedIn(true)
    }
  }

  const loadFilterOptions = async () => {
    try {
      const response = await publicApi.get('/public/filters/options')
      setFilterOptions(response.data)
    } catch (error) {
      console.error('Erro ao carregar opções:', error)
    }
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 0
    }).format(price || 0)
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

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    
    try {
      // Converter valores para números
      const prefsData = {
        property_type: preferences.property_type || null,
        city: preferences.city || null,
        state: preferences.state || null,
        min_value: preferences.min_value ? parseFloat(preferences.min_value) : null,
        max_value: preferences.max_value ? parseFloat(preferences.max_value) : null,
        bedrooms: preferences.bedrooms ? parseInt(preferences.bedrooms) : null,
        bathrooms: preferences.bathrooms ? parseInt(preferences.bathrooms) : null,
        min_area: preferences.min_area ? parseFloat(preferences.min_area) : null,
        max_area: preferences.max_area ? parseFloat(preferences.max_area) : null,
        goal: preferences.goal
      }
      
      if (isLoggedIn) {
        // Se logado, salvar no perfil do usuário
        await api.put('/clients/preferences', prefsData)
      } else {
        // Se não logado, salvar no localStorage
        localStorage.setItem('client_preferences', JSON.stringify(prefsData))
      }
      
      setSuccess(true)
    } catch (error) {
      console.error('Erro ao salvar preferências:', error)
      alert('Erro ao salvar preferências')
    } finally {
      setSaving(false)
    }
  }

  const clearFilters = () => {
    setPreferences({
      property_type: '',
      city: '',
      state: '',
      min_value: '',
      max_value: '',
      bedrooms: '',
      bathrooms: '',
      min_area: '',
      max_area: '',
      goal: 'comprar'
    })
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle size={32} className="text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Preferências Salvas!</h2>
          <p className="text-gray-600 mb-6">
            Suas preferências foram salvas com sucesso. Agora você receberá alertas de imóveis que match com seu perfil.
          </p>
          <div className="flex flex-col gap-3">
            <Link 
              to="/catalogo"
              className="w-full bg-primary-600 text-white font-semibold py-3 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Ver Catálogo
            </Link>
            <button 
              onClick={() => setSuccess(false)}
              className="w-full bg-gray-100 text-gray-700 font-medium py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Alterar Preferências
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header com botão de voltar */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center">
          <Link
            to="/catalogo"
            className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium transition-colors"
          >
            <span>← Voltar ao Catálogo</span>
          </Link>
        </div>
      </div>
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            🎯 Suas Preferências
          </h1>
          <p className="text-primary-100 text-lg">
            Conte-nos o que você procura para encontrados os imóveis ideais
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-6 md:p-8">
            {/* Goal Selection */}
            <div className="mb-8">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <Target className="inline w-4 h-4 mr-2" />
                Você quer...
              </label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setPreferences({ ...preferences, goal: 'comprar' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.goal === 'comprar' 
                      ? 'border-primary-600 bg-primary-50 text-primary-700' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">🏠</div>
                  <div className="font-medium">Comprar</div>
                </button>
                <button
                  type="button"
                  onClick={() => setPreferences({ ...preferences, goal: 'alugar' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.goal === 'alugar' 
                      ? 'border-primary-600 bg-primary-50 text-primary-700' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">🔑</div>
                  <div className="font-medium">Alugar</div>
                </button>
              </div>
            </div>

            {/* Property Type */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Imóvel
              </label>
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={preferences.property_type}
                onChange={(e) => setPreferences({ ...preferences, property_type: e.target.value })}
              >
                <option value="">Todos os tipos</option>
                {filterOptions?.property_types?.map(type => (
                  <option key={type} value={type}>{getPropertyTypeLabel(type)}</option>
                ))}
              </select>
            </div>

            {/* Location */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado
                </label>
                <select
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={preferences.state}
                  onChange={(e) => setPreferences({ ...preferences, state: e.target.value, city: '' })}
                >
                  <option value="">Todos os estados</option>
                  {filterOptions?.cities_by_state && Object.keys(filterOptions.cities_by_state).map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cidade
                </label>
                <select
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={preferences.city}
                  onChange={(e) => setPreferences({ ...preferences, city: e.target.value })}
                  disabled={!preferences.state}
                >
                  <option value="">Todas as cidades</option>
                  {preferences.state && filterOptions?.cities_by_state?.[preferences.state]?.map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Price Range */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <AreaChart className="inline w-4 h-4 mr-2" />
                Faixa de Preço
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <input
                    type="number"
                    placeholder="Mínimo"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    value={preferences.min_value}
                    onChange={(e) => setPreferences({ ...preferences, min_value: e.target.value })}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {preferences.min_value ? formatPrice(preferences.min_value) : 'Qualquer preço'}
                  </p>
                </div>
                <div>
                  <input
                    type="number"
                    placeholder="Máximo"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    value={preferences.max_value}
                    onChange={(e) => setPreferences({ ...preferences, max_value: e.target.value })}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {preferences.max_value ? formatPrice(preferences.max_value) : 'Qualquer preço'}
                  </p>
                </div>
              </div>
            </div>

            {/* Bedrooms & Bathrooms */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Bed className="inline w-4 h-4 mr-2" />
                  Quartos
                </label>
                <select
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={preferences.bedrooms}
                  onChange={(e) => setPreferences({ ...preferences, bedrooms: e.target.value })}
                >
                  <option value="">Qualquer número</option>
                  <option value="1">1+ quarto</option>
                  <option value="2">2+ quartos</option>
                  <option value="3">3+ quartos</option>
                  <option value="4">4+ quartos</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Bath className="inline w-4 h-4 mr-2" />
                  Banheiros
                </label>
                <select
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={preferences.bathrooms}
                  onChange={(e) => setPreferences({ ...preferences, bathrooms: e.target.value })}
                >
                  <option value="">Qualquer número</option>
                  <option value="1">1+ banheiro</option>
                  <option value="2">2+ banheiros</option>
                  <option value="3">3+ banheiros</option>
                </select>
              </div>
            </div>

            {/* Area Range */}
            <div className="mb-8">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <AreaChart className="inline w-4 h-4 mr-2" />
                Área (m²)
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <input
                    type="number"
                    placeholder="Mínima"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    value={preferences.min_area}
                    onChange={(e) => setPreferences({ ...preferences, min_area: e.target.value })}
                  />
                </div>
                <div>
                  <input
                    type="number"
                    placeholder="Máxima"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    value={preferences.max_area}
                    onChange={(e) => setPreferences({ ...preferences, max_area: e.target.value })}
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                type="button"
                onClick={clearFilters}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Limpar
              </button>
              <button
                type="submit"
                disabled={saving}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Salvando...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Salvar Preferências
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Tips */}
          <div className="mt-6 bg-blue-50 rounded-xl p-6">
            <h3 className="font-semibold text-blue-900 mb-2">💡 Dicas</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Quanto mais específicas suas preferências, melhores serão os resultados</li>
              <li>• Você pode alterar suas preferências a qualquer momento</li>
              <li>• Receba alertas cuando nuevos imóveis matching seu perfil</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Preferencias

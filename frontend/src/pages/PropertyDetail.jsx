import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Building2, 
  MapPin, 
  Bed, 
  Bath, 
  Square, 
  Car,
  ArrowLeft,
  Edit,
  Trash2,
  Sparkles,
  Eye,
  MessageSquare,
  Loader2,
  CheckCircle,
  AlertCircle,
  Lightbulb
} from 'lucide-react'
import { propertiesAPI, aiAPI } from '../services/api'

export default function PropertyDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [property, setProperty] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [generatingAd, setGeneratingAd] = useState(false)
  const [improvingImages, setImprovingImages] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [activeTab, setActiveTab] = useState('details')
  const [savingAIAd, setSavingAIAd] = useState(false)

  useEffect(() => {
    loadProperty()
  }, [id])

  const loadProperty = async () => {
    try {
      const response = await propertiesAPI.get(id)
      setProperty(response.data)
    } catch (error) {
      console.error('Erro ao carregar imóvel:', error)
      // Dados de exemplo
      setProperty({
        id: id,
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
        ai_title: null,
        ai_description: null,
        ai_highlights: [],
        image_analysis: null,
        views: 156,
        clicks: 23,
        leads: 5,
        created_at: new Date().toISOString()
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      const response = await aiAPI.analyze(id)
      setProperty(prev => ({ ...prev, image_analysis: response.data }))
    } catch (error) {
      console.error('Erro ao analisar:', error)
    } finally {
      setAnalyzing(false)
    }
  }

const handleGenerateAd = async () => {
    setGeneratingAd(true)
    try {
      const response = await aiAPI.generateAd(id)
      setProperty(prev => ({
        ...prev,
        ai_title: response.data.title,
        ai_description: response.data.description,
        ai_highlights: response.data.highlights,
        review_required: response.data.review_required || true
      }))
    } catch (error) {
      console.error('Erro ao gerar anúncio:', error)
    } finally {
      setGeneratingAd(false)
    }
  }

  const handleSaveAIAd = async () => {
    setSavingAIAd(true)
    try {
      await propertiesAPI.update(id, {
        ai_title: property.ai_title,
        ai_description: property.ai_description,
        ai_highlights: property.ai_highlights
      })
      alert('✅ Anúncio salvo com sucesso!')
    } catch (error) {
      console.error('Erro ao salvar anúncio:', error)
      alert('Erro ao salvar. Tente novamente.')
    } finally {
      setSavingAIAd(false)
    }
  }

  const handleRegenerateAd = async () => {
    if (confirm('Regenerar anúncio IA? Alterações serão perdidas.')) {
      handleGenerateAd()
    }
  }

  const handleImproveImages = async () => {
    setImprovingImages(true)
    try {
      await aiAPI.improveImages(id)
      alert('Imagens melhoradas com sucesso!')
    } catch (error) {
      console.error('Erro ao melhorar imagens:', error)
    } finally {
      setImprovingImages(false)
    }
  }

  const handleGetSuggestions = async () => {
    try {
      const response = await aiAPI.getSuggestions(id)
      setSuggestions(response.data.suggestions)
    } catch (error) {
      console.error('Erro ao obter sugestões:', error)
    }
  }

  const handleDelete = async () => {
    if (confirm('Tem certeza que deseja excluir este imóvel?')) {
      try {
        await propertiesAPI.delete(id)
        navigate('/properties')
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

  if (!property) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Imóvel não encontrado</h2>
        <button onClick={() => navigate('/properties')} className="text-primary-600 hover:underline">
          Voltar para imóveis
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/properties')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{property.title}</h1>
            <div className="flex items-center gap-3 mt-1">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(property.status)}`}>
                {property.status}
              </span>
              <span className="text-gray-500 text-sm capitalize">{property.property_type}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to={`/properties/${id}/edit`}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Edit className="w-4 h-4" />
            Editar
          </Link>
          <button
            onClick={handleDelete}
            className="flex items-center gap-2 px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Excluir
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Image */}
          <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
            <div className="aspect-video bg-gradient-to-br from-primary-100 to-accent-100 rounded-lg flex items-center justify-center">
              <Building2 className="w-24 h-24 text-primary-400" />
            </div>
            {property.images?.length > 0 && (
              <div className="grid grid-cols-4 gap-2 mt-4">
                {property.images.map((img, i) => (
                  <img key={i} src={img} alt={`Imagem ${i + 1}`} className="w-full h-20 object-cover rounded-lg" />
                ))}
              </div>
            )}
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="flex border-b border-gray-100">
              <button
                onClick={() => setActiveTab('details')}
                className={`px-6 py-3 font-medium text-sm transition-colors ${
                  activeTab === 'details'
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Detalhes
              </button>
              <button
                onClick={() => setActiveTab('ad')}
                className={`px-6 py-3 font-medium text-sm transition-colors ${
                  activeTab === 'ad'
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Anúncio IA
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`px-6 py-3 font-medium text-sm transition-colors ${
                  activeTab === 'analysis'
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Análise
              </button>
            </div>

            <div className="p-6">
              {activeTab === 'details' && (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-1">Descrição</h3>
                    <p className="text-gray-900">{property.description || 'Sem descrição'}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-1">Endereço</h3>
                      <p className="text-gray-900 flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        {property.address}, {property.city} - {property.state}
                      </p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-1">Valor</h3>
                      <p className="text-2xl font-bold text-primary-600">{formatValue(property.value)}</p>
                    </div>
                  </div>
                  <div className="flex gap-6 pt-4 border-t border-gray-100">
                    {property.bedrooms > 0 && (
                      <div className="flex items-center gap-2">
                        <Bed className="w-5 h-5 text-gray-400" />
                        <span className="text-gray-700">{property.bedrooms} quartos</span>
                      </div>
                    )}
                    {property.bathrooms > 0 && (
                      <div className="flex items-center gap-2">
                        <Bath className="w-5 h-5 text-gray-400" />
                        <span className="text-gray-700">{property.bathrooms} banheiros</span>
                      </div>
                    )}
                    {property.area > 0 && (
                      <div className="flex items-center gap-2">
                        <Square className="w-5 h-5 text-gray-400" />
                        <span className="text-gray-700">{property.area} m²</span>
                      </div>
                    )}
                    {property.garage_spaces > 0 && (
                      <div className="flex items-center gap-2">
                        <Car className="w-5 h-5 text-gray-400" />
                        <span className="text-gray-700">{property.garage_spaces} vagas</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'ad' && (
                <div className="space-y-4">
{property.ai_title ? (
                    <div className='space-y-4'>
                      {/* Título editável */}
                      <div>
                        <label className='block text-sm font-medium text-gray-700 mb-2'>Título IA (edite se necessário)</label>
                        <input 
                          type='text' 
                          value={property.ai_title || ''}
                          onChange={(e) => setProperty({...property, ai_title: e.target.value})}
                          className='w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500'
                          placeholder='Clique para editar título gerado pela IA'
                        />
                      </div>
                      
                      {/* Descrição editável */}
                      <div>
                        <label className='block text-sm font-medium text-gray-700 mb-2'>Descrição IA</label>
                        <textarea 
                          rows={4}
                          value={property.ai_description || ''}
                          onChange={(e) => setProperty({...property, ai_description: e.target.value})}
                          className='w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 resize-vertical'
                          placeholder='Descrição gerada pela IA - revise e edite'
                        />
                      </div>
                      
                      {/* Highlights editáveis */}
                      <div>
                        <label className='block text-sm font-medium text-gray-700 mb-2'>Destaques IA</label>
                        <div className='space-y-2'>
                          {property.ai_highlights?.map((highlight, i) => (
                            <input 
                              key={i}
                              value={highlight}
                              onChange={(e) => {
                                const newHighlights = [...property.ai_highlights];
                                newHighlights[i] = e.target.value;
                                setProperty({...property, ai_highlights: newHighlights});
                              }}
                              className='w-full p-2 border border-gray-200 rounded text-sm focus:ring-1 focus:ring-primary-500'
                            />
                          )) || ''}
                          <button className='text-primary-600 hover:text-primary-700 text-sm mt-2'>
                            + Adicionar destaque
                          </button>
                        </div>
                      </div>
                      
                      {property.review_required && (
                        <div className='p-3 bg-yellow-50 border border-yellow-200 rounded-lg'>
                          <AlertCircle className='w-4 h-4 text-yellow-600 inline mr-2' />
                          <span className='text-sm text-yellow-800 font-medium'>⚠️ REVISE e edite antes de publicar!</span>
                        </div>
                      )}
                      
                      <div className='flex gap-3 pt-4'>
                        <button
                          onClick={handleSaveAIAd}
                          disabled={!property.ai_title || savingAIAd}
                          className='flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium'
                        >
                          {savingAIAd ? 'Salvando...' : '💾 Salvar Anúncio Editado'}
                        </button>
                        <button
                          onClick={handleRegenerateAd}
                          className='flex-1 bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700'
                        >
                          🔄 Regenerar IA
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">Nenhum anúncio gerado ainda</p>
                      <button
                        onClick={handleGenerateAd}
                        disabled={generatingAd}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 mx-auto"
                      >
                        {generatingAd ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Gerando...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4" />
                            Gerar Anúncio com IA
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'analysis' && (
                <div className="space-y-4">
                  {property.image_analysis ? (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-green-50 rounded-lg">
                          <div className="text-sm text-green-600 mb-1">Iluminação</div>
                          <div className="text-2xl font-bold text-green-700">{property.image_analysis.lighting_score}%</div>
                        </div>
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <div className="text-sm text-blue-600 mb-1">Qualidade</div>
                          <div className="text-2xl font-bold text-blue-700">{property.image_analysis.quality_score}%</div>
                        </div>
                      </div>
                      {property.image_analysis.environments?.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Ambientes identificados:</h4>
                          <div className="flex flex-wrap gap-2">
                            {property.image_analysis.environments.map((env, i) => (
                              <span key={i} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                                {env.environment}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {property.image_analysis.issues?.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Problemas detectados:</h4>
                          <div className="space-y-2">
                            {property.image_analysis.issues.map((issue, i) => (
                              <div key={i} className="flex items-center gap-2 text-red-600">
                                <AlertCircle className="w-4 h-4" />
                                {issue}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-600 mb-4">Nenhuma análise realizada ainda</p>
                      <button
                        onClick={handleAnalyze}
                        disabled={analyzing}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 mx-auto"
                      >
                        {analyzing ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Analisando...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4" />
                            Analisar Imagens
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Stats */}
          <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">Performance</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-600">
                  <Eye className="w-4 h-4" />
                  Visualizações
                </div>
                <span className="font-semibold text-gray-900">{property.views}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-600">
                  <MessageSquare className="w-4 h-4" />
                  Cliques
                </div>
                <span className="font-semibold text-gray-900">{property.clicks}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-600">
                  <Sparkles className="w-4 h-4" />
                  Leads
                </div>
                <span className="font-semibold text-gray-900">{property.leads}</span>
              </div>
            </div>
          </div>

          {/* AI Actions */}
          <div className="bg-gradient-to-r from-primary-600 to-accent-500 rounded-xl p-6 text-white">
            <h3 className="font-semibold mb-4">Ações com IA</h3>
            <div className="space-y-3">
              <button
                onClick={handleGenerateAd}
                disabled={generatingAd}
                className="w-full flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                {generatingAd ? 'Gerando...' : 'Gerar Anúncio'}
              </button>
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                {analyzing ? 'Analisando...' : 'Analisar Imagens'}
              </button>
              <button
                onClick={handleImproveImages}
                disabled={improvingImages}
                className="w-full flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                {improvingImages ? 'Melhorando...' : 'Melhorar Imagens'}
              </button>
              <button
                onClick={handleGetSuggestions}
                className="w-full flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
              >
                <Lightbulb className="w-4 h-4" />
                Ver Sugestões
              </button>
            </div>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-4">Sugestões Inteligentes</h3>
              <div className="space-y-3">
                {suggestions.map((suggestion, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <Lightbulb className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                    {suggestion}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
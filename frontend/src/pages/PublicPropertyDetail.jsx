import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Phone, Mail, Share2, Heart, MapPin, Bed, Bath, Car, Home, Building, User, ArrowRight, X } from 'lucide-react'
import { publicApi } from '../services/api'
import { useAuth } from '../context/AuthContext'

function PublicPropertyDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuth()
const [property, setProperty] = useState(null)
  const [loading, setLoading] = useState(true)
  const [leadForm, setLeadForm] = useState({
    client_name: '',
    client_email: '',
    client_phone: '',
    message: ''
  })
  const [showLeadForm, setShowLeadForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [sessionId] = useState(localStorage.getItem('session_id') || crypto.randomUUID())
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [showImageModal, setShowImageModal] = useState(false)
  
  useEffect(() => {
    localStorage.setItem('session_id', sessionId)
    loadProperty()
  }, [id])

  const loadProperty = async () => {
    try {
      const response = await publicApi.get(`/public/properties/${id}`)
      setProperty(response.data)
      
      // Track view
      publicApi.post('/public/views', { session_id: sessionId, property_id: id })
    } catch (error) {
      console.error('Erro:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInterest = async () => {
    setSubmitting(true)
    try {
      await publicApi.post('/public/leads', {
        property_id: id,
        ...leadForm
      })
      
      // Success feedback
      alert('✅ Interesse registrado! O corretor entrará em contato em breve.')
      setLeadForm({ client_name: '', client_email: '', client_phone: '', message: '' })
    } catch (error) {
      alert('Erro ao enviar. Tente novamente.')
    } finally {
      setSubmitting(false)
    }
  }

  const shareProperty = () => {
    const url = `${window.location.origin}/imovel/${id}`
    navigator.clipboard.writeText(url)
    alert('Link copiado!')
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(price)
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center">Carregando...</div>

  if (!property) return <div className="min-h-screen flex items-center justify-center">Imóvel não encontrado</div>

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <button 
            onClick={() => navigate('/catalogo')}
            className="flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-4"
          >
            <ArrowLeft size={20} />
            Voltar ao Catálogo
          </button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Images Gallery */}
          <div>
            <div className="relative rounded-xl overflow-hidden shadow-2xl group">
              {property.images?.length > 0 ? (
                <>
                  {/* Imagem principal do carrossel */}
                  <img 
                    src={property.images[currentImageIndex]} 
                    alt={property.title}
                    className="w-full h-96 lg:h-[500px] object-cover cursor-pointer"
                    onClick={() => setShowImageModal(true)}
                  />
                  
                  {/* Navegação carrossel */}
                  {property.images.length > 1 && (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : property.images.length - 1))
                        }}
                        className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full transition-all opacity-0 group-hover:opacity-100"
                      >
                        <ArrowLeft size={20} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setCurrentImageIndex((prev) => (prev < property.images.length - 1 ? prev + 1 : 0))
                        }}
                        className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full transition-all opacity-0 group-hover:opacity-100"
                      >
                        <ArrowRight size={20} />
                      </button>
                    </>
                  )}
                  
                  {/* Dots */}
                  {property.images.length > 1 && (
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                      {property.images.map((_, index) => (
                        <button
                          key={index}
                          onClick={() => setCurrentImageIndex(index)}
                          className={`w-3 h-3 rounded-full transition-all ${
                            index === currentImageIndex ? 'bg-white w-6' : 'bg-white/50 hover:bg-white'
                          }`}
                        />
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <div className="w-full h-96 lg:h-[500px] bg-gray-200 flex items-center justify-center cursor-pointer" onClick={() => setShowImageModal(true)}>
                  <Home size={64} className="text-gray-400" />
                </div>
              )}
            </div>
            
            {/* Actions */}
            <div className="flex gap-2 mt-4">
              <button 
                onClick={shareProperty}
                className="flex-1 bg-primary-600 text-white py-3 px-6 rounded-lg hover:bg-primary-700 flex items-center justify-center gap-2"
              >
                <Share2 size={20} />
                Compartilhar
              </button>
              <button className="bg-white border-2 border-gray-200 p-3 rounded-lg hover:bg-gray-50">
                <Heart size={24} className="text-gray-400 hover:text-red-500" />
              </button>
            </div>
          </div>

          {/* Property Info */}
          <div>
            <div className="bg-white p-8 rounded-xl shadow-lg">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">{property.ai_title || property.title}</h1>
                  <p className="text-2xl font-bold text-primary-600 mt-2">
                    {formatPrice(property.value)}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                <div className="flex items-center gap-2">
                  <Building size={16} />
                  <span>{property.property_type?.toUpperCase()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin size={16} />
                  <span>{property.city}, {property.state}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Bed size={16} />
                  <span>{property.bedrooms} quartos</span>
                </div>
                <div className="flex items-center gap-2">
                  <Bath size={16} />
                  <span>{property.bathrooms} banheiros</span>
                </div>
                <div className="flex items-center gap-2">
                  <Car size={16} />
                  <span>{property.garage_spaces} vagas</span>
                </div>
              </div>

              <div className="mb-8">
                <h3 className="font-semibold mb-3">Descrição</h3>
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {property.ai_description || property.description}
                </p>
              </div>

              {/* CTA Buttons */}
              <div className="space-y-3">
                <button 
                  onClick={() => setShowLeadForm(true)}
                  className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-emerald-600 hover:to-emerald-700 shadow-lg flex items-center justify-center gap-3"
                >
                  <Phone size={24} />
                  Tenho Interesse
                </button>
                
                {isAuthenticated && (
                  <button className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg hover:bg-primary-700">
                    Salvar nos Favoritos
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Lead Form Modal + Image Modal */}
        <>
          {showLeadForm && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-2xl p-8 max-w-md w-full max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold">Tenho Interesse!</h2>
                  <button 
                    onClick={() => setShowLeadForm(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={24} />
                  </button>
                </div>
                
                <form onSubmit={(e) => { e.preventDefault(); handleInterest() }}>
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="Seu nome completo *"
                      className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      value={leadForm.client_name}
                      onChange={(e) => setLeadForm({...leadForm, client_name: e.target.value})}
                      required
                    />
                    
                    <input
                      type="email"
                      placeholder="Seu email (opcional)"
                      className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      value={leadForm.client_email}
                      onChange={(e) => setLeadForm({...leadForm, client_email: e.target.value})}
                    />
                    
                    <input
                      type="tel"
                      placeholder="Seu telefone/WhatsApp *"
                      className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      value={leadForm.client_phone}
                      onChange={(e) => setLeadForm({...leadForm, client_phone: e.target.value})}
                      required
                    />
                    
                    <textarea
                      placeholder="Mensagem (opcional)"
                      rows={4}
                      className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                      value={leadForm.message}
                      onChange={(e) => setLeadForm({...leadForm, message: e.target.value})}
                    />
                  </div>
                  
                  <div className="flex gap-3 mt-8">
                    <button
                      type="button"
                      onClick={() => setShowLeadForm(false)}
                      className="flex-1 bg-gray-100 text-gray-700 py-3 px-6 rounded-xl hover:bg-gray-200 transition-colors"
                    >
                      Cancelar
                    </button>
                    <button
                      type="submit"
                      disabled={submitting}
                      className="flex-1 bg-emerald-500 text-white py-3 px-6 rounded-xl font-semibold hover:bg-emerald-600 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {submitting ? 'Enviando...' : 'Enviar Interesse'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Modal Expand Imagem */}
          {showImageModal && property.images && property.images.length > 0 && (
            <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4" onClick={() => setShowImageModal(false)}>
              <button 
                className="absolute top-6 right-6 text-white hover:text-gray-300 p-2 rounded-full bg-black/30"
                onClick={(e) => { e.stopPropagation(); setShowImageModal(false); }}
              >
                <X size={28} />
              </button>
              <img 
                src={property.images[currentImageIndex]} 
                alt="Expandida"
                className="max-w-full max-h-full object-contain"
              />
              <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2">
                {property.images.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentImageIndex(index)}
                    className={`w-3 h-3 rounded-full transition-all ${
                      index === currentImageIndex ? 'bg-white w-8' : 'bg-white/50 hover:bg-white'
                    }`}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      </div>
    </div>
  )
}

export default PublicPropertyDetail


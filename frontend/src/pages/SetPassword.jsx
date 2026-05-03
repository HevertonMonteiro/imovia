import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Lock, Eye, EyeOff, Loader2, CheckCircle, Building } from 'lucide-react'
import { api } from '../services/api'

export default function SetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const navigate = useNavigate()
  
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  
  useEffect(() => {
    if (!token) {
      setError('Token de convite não encontrado')
    }
  }, [token])
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!name.trim()) {
      setError('Por favor, informe seu nome')
      return
    }
    
    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      return
    }
    
    if (password !== confirmPassword) {
      setError('As senhas não coincidem')
      return
    }
    
    setLoading(true)
    
    try {
      const response = await api.post('/auth/set-password', null, {
        params: { token, password, name }
      })
      
      setSuccess(true)
      
      // Redirecionar após 2 segundos
      setTimeout(() => {
        const userType = response.data.user?.tipo
        if (userType === 'cliente') {
          navigate('/catalogo')
        } else {
          navigate('/')
        }
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao definir senha')
    } finally {
      setLoading(false)
    }
  }
  
  if (success) {
    return (
      <div className="min-h-screen flex">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="w-full max-w-md">
            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle size={40} className="text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Senha Definida!
              </h2>
              <p className="text-gray-600">
                Sua conta foi ativada com sucesso. Redirecting...
              </p>
            </div>
          </div>
        </div>
        
        <div className="hidden lg:flex flex-1 bg-gradient-to-br from-primary-600 to-accent-500 items-center justify-center p-12">
          <div className="max-w-lg text-center text-white">
            <div className="w-24 h-24 bg-white/20 rounded-3xl flex items-center justify-center mx-auto mb-8">
              <Building className="w-12 h-12" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              Bem-vindo à Plataforma!
            </h2>
            <p className="text-lg text-white/80">
              Sua conta foi criada com sucesso. Agora você pode gerenciar seus imóveis.
            </p>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="min-h-screen flex">
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
              <Building className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Imovia</h1>
              <p className="text-sm text-gray-500">Gestão Imobiliária Inteligente</p>
            </div>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Crie sua senha
          </h2>
          <p className="text-gray-600 mb-8">
            Defina sua senha para acessar a plataforma
          </p>
          
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Seu Nome
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Seu nome completo"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
                disabled={!token}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Senha
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  required
                  disabled={!token}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirmar Senha
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
                disabled={!token}
              />
            </div>
            
            <button
              type="submit"
              disabled={loading || !token}
              className="w-full flex items-center justify-center gap-2 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Criando conta...
                </>
              ) : (
                <>
                  <Lock className="w-5 h-5" />
                  Criar Senha
                </>
              )}
            </button>
          </form>
        </div>
      </div>
      
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-primary-600 to-accent-500 items-center justify-center p-12">
        <div className="max-w-lg text-center text-white">
          <div className="w-24 h-24 bg-white/20 rounded-3xl flex items-center justify-center mx-auto mb-8">
            <Building className="w-12 h-12" />
          </div>
          <h2 className="text-3xl font-bold mb-4">
            Complete seu Cadastro
          </h2>
          <p className="text-lg text-white/80">
            Defina sua senha para ativar sua conta e começar a usar a plataforma.
          </p>
        </div>
      </div>
    </div>
  )
}

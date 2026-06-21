import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Send, Loader2, MessageSquare, ArrowLeft, Phone, Sparkles } from 'lucide-react'
import { api, publicApi } from '../services/api'

// Chat MVP: cliente cria conversa no imóvel e envia mensagens.
// Corretor vê fila/abre conversa pelo lead selecionado (MVP simplificado).

function useQuery() {
  const { search } = useLocation()
  return useMemo(() => new URLSearchParams(search), [search])
}

export default function Chat() {
  const navigate = useNavigate()
  const query = useQuery()

  const [loading, setLoading] = useState(true)
  const [conversations, setConversations] = useState([])
  const [activeConversation, setActiveConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)

  const conversationPropertyId = query.get('property_id')

  useEffect(() => {
    loadConversations()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadConversations = async () => {
    try {
      setLoading(true)
      const res = await api.get('/chat/conversations')
      setConversations(res.data || [])
      if (res.data && res.data.length > 0) {
        setActiveConversation(res.data[0])
      }
    } catch (e) {
      console.error('Erro ao carregar conversas:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!activeConversation) return
    loadMessages(activeConversation.id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeConversation?.id])

  const loadMessages = async (conversationId) => {
    try {
      const res = await api.get(`/chat/conversations/${conversationId}/messages`)
      setMessages(res.data || [])
    } catch (e) {
      console.error('Erro ao carregar mensagens:', e)
    }
  }

  const ensureConversationForProperty = async () => {
    if (!conversationPropertyId) return
    try {
      const res = await api.post('/chat/conversations', {
        property_id: conversationPropertyId
      })
      const conv = res.data
      setActiveConversation(conv)
      await loadConversations()
      await loadMessages(conv.id)
    } catch (e) {
      console.error('Erro ao criar conversa:', e)
    }
  }

  useEffect(() => {
    // se vier property_id, cria/abre conversa
    if (conversationPropertyId) {
      ensureConversationForProperty()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationPropertyId])

  const sendMessage = async () => {
    if (!activeConversation) return
    if (!text.trim()) return

    try {
      setSending(true)
      const res = await api.post(`/chat/conversations/${activeConversation.id}/messages`, {
        text
      })
      setText('')
      await loadMessages(activeConversation.id)
    } catch (e) {
      console.error('Erro ao enviar mensagem:', e)
      alert(e.response?.data?.detail || 'Erro ao enviar')
    } finally {
      setSending(false)
    }
  }

  const sendAction = async (action) => {
    if (!activeConversation) return
    try {
      const res = await api.post(`/chat/conversations/${activeConversation.id}/action`, {
        action
      })
      const payload = res.data
      if (payload?.type === 'redirect' && payload?.to) {
        navigate(payload.to)
      }
    } catch (e) {
      console.error('Erro ao executar ação:', e)
      alert(e.response?.data?.detail || 'Erro')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-10 h-10 animate-spin text-primary-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-3 mb-5">
          <button
            onClick={() => navigate('/leads')}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Chat</h1>
            <p className="text-gray-600 text-sm">Converse com a IA e depois com o responsável</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Lateral - conversas */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl border border-gray-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <MessageSquare className="w-5 h-5 text-primary-600" />
                <h2 className="font-semibold">Conversas</h2>
              </div>

              <div className="space-y-2">
                {conversations.length === 0 ? (
                  <div className="text-gray-500 text-sm">Nenhuma conversa ainda.</div>
                ) : (
                  conversations.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => setActiveConversation(c)}
                      className={`w-full text-left p-3 rounded-xl border transition-colors ${
                        activeConversation?.id === c.id
                          ? 'border-primary-300 bg-primary-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <div className="font-medium text-gray-900">Imóvel {c.property_id}</div>
                          <div className="text-xs text-gray-500">Status: {c.status}</div>
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Chat */}
          <div className="lg:col-span-2">
            {activeConversation ? (
              <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
                <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-primary-600 to-accent-500 text-white">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5" />
                        <span className="font-semibold">Atendimento IA</span>
                      </div>
                      <div className="text-white/80 text-sm mt-1">
                        Imóvel: {activeConversation.property_id}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => sendAction('other_property')}
                        className="bg-white/20 hover:bg-white/30 text-white px-3 py-2 rounded-xl text-sm font-semibold"
                      >
                        Quero outro imóvel
                      </button>
                      <button
                        onClick={() => sendAction('transfer_visit')}
                        className="bg-white text-primary-700 hover:bg-gray-100 px-3 py-2 rounded-xl text-sm font-semibold"
                      >
                        Prosseguir com visita
                      </button>
                    </div>
                  </div>
                </div>

                <div className="p-4 h-[50vh] overflow-y-auto bg-gray-50">
                  <div className="space-y-3">
                    {messages.length === 0 ? (
                      <div className="text-sm text-gray-500">Envie uma mensagem para começar.</div>
                    ) : (
                      messages.map((m) => {
                        const mine = m.sender_user_id === undefined ? false : false
                        // MVP: estilizar pelo sender_type
                        const isClient = m.sender_type === 'cliente'
                        return (
                          <div
                            key={m.id}
                            className={`flex ${isClient ? 'justify-end' : 'justify-start'}`}
                          >
                            <div
                              className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm shadow-sm ${
                                isClient
                                  ? 'bg-primary-600 text-white'
                                  : 'bg-white border border-gray-200 text-gray-900'
                              }`}
                            >
                              {m.text}
                            </div>
                          </div>
                        )
                      })
                    )}
                  </div>
                </div>

                <div className="p-4 border-t border-gray-100">
                  <div className="flex gap-3">
                    <input
                      className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
                      placeholder="Digite sua mensagem..."
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') sendMessage()
                      }}
                    />
                    <button
                      onClick={sendMessage}
                      disabled={sending}
                      className="w-14 h-12 rounded-xl bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white flex items-center justify-center"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-2">
                    <button
                      onClick={() => sendAction('transfer_visit')}
                      className="px-3 py-2 rounded-xl text-sm font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100"
                    >
                      Falar com responsável
                    </button>
                    <button
                      onClick={() => sendAction('other_property')}
                      className="px-3 py-2 rounded-xl text-sm font-semibold bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100"
                    >
                      Quero escolher outro imóvel
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-gray-200 p-8 text-center">
                <div className="mx-auto w-16 h-16 bg-primary-50 rounded-2xl flex items-center justify-center text-primary-700">
                  <MessageSquare className="w-8 h-8" />
                </div>
                <h2 className="mt-4 font-semibold text-gray-900">Selecione uma conversa</h2>
                <p className="text-gray-600 text-sm mt-1">Ou abra um imóvel para iniciar um chat.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}


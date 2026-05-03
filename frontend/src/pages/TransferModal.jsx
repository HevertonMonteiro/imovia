import { motion } from 'framer-motion'
import { corretoresAPI } from '../services/api'
import { X } from 'lucide-react'

const TransferModal = ({ leadId, corretores, onClose, onTransfer }) => {
  const handleTransfer = async (corretorId) => {
    try {
      await corretoresAPI.transferir(leadId, { corretor_id: corretorId })
      onClose()
      onTransfer()
    } catch (error) {
      alert('Erro ao transferir')
    }
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div 
        initial={{ scale: 0.95 }} 
        animate={{ scale: 1 }} 
        className="bg-white rounded-2xl p-6 w-full max-w-sm max-h-[80vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900">Transferir Lead</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="space-y-2 mb-6">
          {corretores.map((corretor) => (
            <button
              key={corretor.id}
              onClick={() => handleTransfer(corretor.id)}
              className="w-full flex items-center gap-3 p-4 border border-gray-200 rounded-xl hover:border-primary-300 hover:bg-primary-50 transition-all group"
            >
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                <span className="text-primary-700 font-semibold">
                  {corretor.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">{corretor.name}</p>
                <p className="text-sm text-gray-500 truncate">{corretor.email}</p>
              </div>
              <div className="w-5 h-5 border-2 border-primary-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
              </div>
            </button>
          ))}
        </div>
        
        {corretores.length === 0 && (
          <p className="text-center text-gray-500 py-8">Nenhum corretor disponível</p>
        )}
      </motion.div>
    </motion.div>
  )
}

export default TransferModal

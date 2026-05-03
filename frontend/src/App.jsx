import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

// Context
import { AuthProvider, useAuth } from './context/AuthContext'

// Páginas do Corretor
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Properties from './pages/Properties'
import PropertyForm from './pages/PropertyForm'
import PropertyDetail from './pages/PropertyDetail'
import Clients from './pages/Clients'
import Leads from './pages/Leads'
import Corretores from './pages/Corretores'
import Imobiliarias from './pages/Imobiliarias'

// Páginas Públicas (Área do Cliente)
import Catalogo from './pages/Catalogo'
import PublicPropertyDetail from './pages/PublicPropertyDetail'
import Preferencias from './pages/Preferencias'
import Profile from './pages/Profile'
import SetPassword from './pages/SetPassword'

// Componentes
import Sidebar from './components/Sidebar'
import Header from './components/Header'

// Estilos
import './index.css'

function PrivateRoute({ children }) {
  const { isAuthenticated, loading, user } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }
  
  // Redirect baseado no tipo de usuário
  const userType = user?.tipo
  
  // Se é cliente, redirecionar para catálogo
  if (userType === 'cliente') {
    return <Navigate to="/catalogo" />
  }
  
  // Se é corretor ou admin, redirecionar para dashboard
  return children
}

function AppLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64">
        <Header />
        <main className="flex-1 p-8 mt-16">
          {children}
        </main>
      </div>
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/" element={
        <PrivateRoute>
          <AppLayout>
            <Dashboard />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/properties" element={
        <PrivateRoute>
          <AppLayout>
            <Properties />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/properties/new" element={
        <PrivateRoute>
          <AppLayout>
            <PropertyForm />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/properties/:id" element={
        <PrivateRoute>
          <AppLayout>
            <PropertyDetail />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/properties/:id/edit" element={
        <PrivateRoute>
          <AppLayout>
            <PropertyForm />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/clients" element={
        <PrivateRoute>
          <AppLayout>
            <Clients />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/leads" element={
        <PrivateRoute>
          <AppLayout>
            <Leads />
          </AppLayout>
        </PrivateRoute>
      } />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AnimatePresence mode="wait">
<Routes>
{/* ===== ÁREA DO CLIENTE (PÚBLICA) ===== */}
            <Route path="/catalogo" element={<Catalogo />} />
            <Route path="/imovel/:id" element={<PublicPropertyDetail />} />
            <Route path="/preferencias" element={<Preferencias />} />
            <Route path="/minhas-preferencias" element={<Preferencias />} />
            <Route path="/perfil" element={<Profile />} />
            <Route path="/criar-senha" element={<SetPassword />} />
            
            {/* ===== AUTENTICAÇÃO ===== */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
{/* ===== PAINEL DO CORRETOR (PRIVADA) ===== */}
            <Route path="/*" element={
              <PrivateRoute>
                <AppLayout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/properties" element={<Properties />} />
                    <Route path="/properties/new" element={<PropertyForm />} />
                    <Route path="/properties/:id" element={<PropertyDetail />} />
                    <Route path="/properties/:id/edit" element={<PropertyForm />} />
                    <Route path="/clients" element={<Clients />} />
                    <Route path="/leads" element={<Leads />} />
                    <Route path="/corretores" element={<Corretores />} />
                    <Route path="/imobiliarias" element={<Imobiliarias />} />
                  </Routes>
                </AppLayout>
              </PrivateRoute>
            } />
          </Routes>
        </AnimatePresence>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
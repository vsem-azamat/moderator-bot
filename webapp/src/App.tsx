import { useEffect, useState } from 'react'
import { useLaunchParams, useRawInitData } from '@telegram-apps/sdk-react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import BulkChatManager from './components/BulkChatManager'
import './App.css'

const queryClient = new QueryClient()

// Type declaration for Telegram WebApp
declare global {
  interface Window {
    Telegram: {
      WebApp: {
        themeParams: {
          bg_color?: string
          text_color?: string
          button_color?: string
          button_text_color?: string
        }
      }
    }
  }
}

interface UserInfo {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
}

function App() {
  const launchParams = useLaunchParams()
  const rawInitData = useRawInitData()
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [themeParams, setThemeParams] = useState<{
    bgColor?: string
    textColor?: string
    buttonColor?: string
    buttonTextColor?: string
  } | null>(null)
  const [activeTab, setActiveTab] = useState<'bulk' | 'analytics' | 'settings' | 'debug'>('bulk')

  useEffect(() => {
    // Parse raw init data
    if (rawInitData) {
      try {
        const parsed = new URLSearchParams(rawInitData)
        const userStr = parsed.get('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          setUserInfo(user)
        }
      } catch (error) {
        console.error('Failed to parse init data:', error)
      }
    }
  }, [rawInitData])

  useEffect(() => {
    // Get theme from Telegram WebApp
    if (window.Telegram?.WebApp) {
      const webapp = window.Telegram.WebApp
      setThemeParams({
        bgColor: webapp.themeParams?.bg_color || '#ffffff',
        textColor: webapp.themeParams?.text_color || '#000000',
        buttonColor: webapp.themeParams?.button_color || '#0088cc',
        buttonTextColor: webapp.themeParams?.button_text_color || '#ffffff'
      })
    }
  }, [])

  useEffect(() => {
    // Apply Telegram theme
    if (themeParams) {
      document.documentElement.style.setProperty('--tg-bg-color', themeParams.bgColor || '#ffffff')
      document.documentElement.style.setProperty('--tg-text-color', themeParams.textColor || '#000000')
      document.documentElement.style.setProperty('--tg-button-color', themeParams.buttonColor || '#0088cc')
      document.documentElement.style.setProperty('--tg-button-text-color', themeParams.buttonTextColor || '#ffffff')
    }
  }, [themeParams])

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app" style={{
        backgroundColor: themeParams?.bgColor || '#ffffff',
        color: themeParams?.textColor || '#000000',
        minHeight: '100vh',
        padding: '1rem'
      }}>
        <div className="container">
          <header className="app-header">
            <h1>🛡️ Moderator Bot</h1>
            {userInfo && (
              <div className="user-badge">
                👋 {userInfo.first_name}
              </div>
            )}
          </header>

          <nav className="navigation">
            <button
              className={`nav-btn ${activeTab === 'bulk' ? 'active' : ''}`}
              onClick={() => setActiveTab('bulk')}
            >
              🎯 Массовые операции
            </button>
            <button
              className={`nav-btn ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
            >
              📊 Аналитика
            </button>
            <button
              className={`nav-btn ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              ⚙️ Настройки
            </button>
            <button
              className={`nav-btn ${activeTab === 'debug' ? 'active' : ''}`}
              onClick={() => setActiveTab('debug')}
            >
              🔧 Debug
            </button>
          </nav>

          <main className="tab-content">
            {activeTab === 'bulk' && <BulkChatManager />}

            {activeTab === 'analytics' && (
              <div className="placeholder-tab">
                <h2>📊 Аналитика</h2>
                <div className="placeholder-content">
                  <p>🚧 В разработке</p>
                  <ul>
                    <li>📈 Статистика чатов</li>
                    <li>👥 Активность пользователей</li>
                    <li>⚡ Модерационные действия</li>
                    <li>📋 Отчеты и экспорт</li>
                  </ul>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="placeholder-tab">
                <h2>⚙️ Глобальные настройки</h2>
                <div className="placeholder-content">
                  <p>🚧 В разработке</p>
                  <ul>
                    <li>🤖 Настройки бота</li>
                    <li>🔔 Уведомления</li>
                    <li>🔒 Безопасность</li>
                    <li>🌐 Локализация</li>
                  </ul>
                </div>
              </div>
            )}

            {activeTab === 'debug' && (
              <div className="debug-tab">
                <h2>🔧 Отладка</h2>
                <div className="debug-info">
                  <details>
                    <summary>Launch Params</summary>
                    <pre>{JSON.stringify(launchParams, null, 2)}</pre>
                  </details>
                  <details>
                    <summary>User Info</summary>
                    <pre>{JSON.stringify(userInfo, null, 2)}</pre>
                  </details>
                  <details>
                    <summary>Theme Params</summary>
                    <pre>{JSON.stringify(themeParams, null, 2)}</pre>
                  </details>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App

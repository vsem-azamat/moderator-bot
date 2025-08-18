import { useEffect, useState } from 'react'
import { useLaunchParams, useRawInitData } from '@telegram-apps/sdk-react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ChatList from './components/ChatList'
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
  const [initData, setInitData] = useState<unknown>(null)
  const [themeParams, setThemeParams] = useState<unknown>(null)
  const [activeTab, setActiveTab] = useState<'user' | 'chats' | 'debug'>('chats')

  useEffect(() => {
    // Parse raw init data
    if (rawInitData) {
      try {
        const parsed = new URLSearchParams(rawInitData)
        const userStr = parsed.get('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          setInitData({ user })
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
          <h1>Moderator Bot Admin Panel</h1>

          <div className="navigation">
            <button
              className={`nav-btn ${activeTab === 'chats' ? 'active' : ''}`}
              onClick={() => setActiveTab('chats')}
            >
              🎛️ Управление чатами
            </button>
            <button
              className={`nav-btn ${activeTab === 'user' ? 'active' : ''}`}
              onClick={() => setActiveTab('user')}
            >
              👤 Пользователь
            </button>
            <button
              className={`nav-btn ${activeTab === 'debug' ? 'active' : ''}`}
              onClick={() => setActiveTab('debug')}
            >
              🔧 Отладка
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'chats' && (
              <div className="chats-tab">
                <ChatList />
              </div>
            )}

            {activeTab === 'user' && (
              <div className="user-tab">
                {userInfo ? (
                  <div className="user-info">
                    <h2>Информация о пользователе</h2>
                    <div className="user-card">
                      <p><strong>ID:</strong> {userInfo.id}</p>
                      <p><strong>Имя:</strong> {userInfo.first_name} {userInfo.last_name || ''}</p>
                      {userInfo.username && <p><strong>Имя пользователя:</strong> @{userInfo.username}</p>}
                      {userInfo.language_code && <p><strong>Язык:</strong> {userInfo.language_code}</p>}
                      {userInfo.is_premium !== undefined && (
                        <p><strong>Premium:</strong> {userInfo.is_premium ? 'Да' : 'Нет'}</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="loading">
                    <p>Загрузка информации о пользователе...</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'debug' && (
              <div className="debug-tab">
                <div className="debug-info">
                  <h3>Отладочная информация</h3>
                  <details>
                    <summary>Launch Params</summary>
                    <pre>{JSON.stringify(launchParams, null, 2)}</pre>
                  </details>
                  <details>
                    <summary>Init Data</summary>
                    <pre>{JSON.stringify(initData, null, 2)}</pre>
                  </details>
                  <details>
                    <summary>Theme Params</summary>
                    <pre>{JSON.stringify(themeParams, null, 2)}</pre>
                  </details>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App

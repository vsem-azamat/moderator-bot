import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ChatSelectionPanel from './ChatSelectionPanel'
import ActionConfigPanel from './ActionConfigPanel'
import BulkActionExecutor from './BulkActionExecutor'
import { apiService } from '../services/api'
import type { BulkActionConfig } from '../types'

// No props needed for this component

const BulkChatManager: React.FC = () => {
  const [selectedChats, setSelectedChats] = useState<number[]>([])
  const [actionConfig, setActionConfig] = useState<BulkActionConfig | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionResults, setExecutionResults] = useState<{ error?: string } | null>(null)

  // Fetch chats data
  const { data: chats = [], isLoading, error } = useQuery({
    queryKey: ['chats'],
    queryFn: () => apiService.getChats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  })

  const handleChatSelection = (chatIds: number[]) => {
    setSelectedChats(chatIds)
  }

  const handleActionConfig = (config: BulkActionConfig) => {
    setActionConfig(config)
  }

  const handleExecuteAction = async () => {
    if (!actionConfig || selectedChats.length === 0) return

    setIsExecuting(true)
    setExecutionResults(null)

    try {
      const results = await apiService.bulkUpdateChats(selectedChats, actionConfig)
      setExecutionResults(results)
    } catch (error) {
      console.error('Bulk action failed:', error)
      setExecutionResults({ error: 'Операция не выполнена' })
    } finally {
      setIsExecuting(false)
    }
  }

  const handleReset = () => {
    setSelectedChats([])
    setActionConfig(null)
    setExecutionResults(null)
  }

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка чатов...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <h3>❌ Ошибка загрузки</h3>
        <p>Не удалось загрузить список чатов</p>
        <p className="error-details">
          {error instanceof Error ? error.message : 'Неизвестная ошибка'}
        </p>
        <div className="error-actions">
          <button
            onClick={() => window.location.reload()}
            className="retry-button"
          >
            🔄 Перезагрузить
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bulk-chat-manager">
      <div className="manager-header">
        <h2>🎯 Массовые операции с чатами</h2>
        <div className="header-stats">
          <span className="stat">
            📊 Всего чатов: <strong>{chats.length}</strong>
          </span>
          <span className="stat">
            ✅ Выбрано: <strong>{selectedChats.length}</strong>
          </span>
        </div>
      </div>

      <div className="manager-layout">
        <div className="left-panel">
          <ActionConfigPanel
            onConfigChange={handleActionConfig}
            selectedCount={selectedChats.length}
          />

          {actionConfig && selectedChats.length > 0 && (
            <BulkActionExecutor
              actionConfig={actionConfig}
              selectedChats={selectedChats}
              chats={chats}
              onExecute={handleExecuteAction}
              onReset={handleReset}
              isExecuting={isExecuting}
              executionResults={executionResults}
            />
          )}
        </div>

        <div className="right-panel">
          <ChatSelectionPanel
            chats={chats}
            selectedChats={selectedChats}
            onSelectionChange={handleChatSelection}
          />
        </div>
      </div>
    </div>
  )
}

export default BulkChatManager

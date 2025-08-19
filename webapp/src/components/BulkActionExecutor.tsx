import { useState } from 'react'
import type { Chat, BulkActionConfig, BulkExecutionResult } from '../types'

interface BulkActionExecutorProps {
  actionConfig: BulkActionConfig
  selectedChats: number[]
  chats: Chat[]
  onExecute: () => void
  onReset: () => void
  isExecuting: boolean
  executionResults: BulkExecutionResult | null
}

const BulkActionExecutor: React.FC<BulkActionExecutorProps> = ({
  actionConfig,
  selectedChats,
  chats,
  onExecute,
  onReset,
  isExecuting,
  executionResults
}) => {
  const [showConfirmation, setShowConfirmation] = useState(false)

  const selectedChatTitles = chats
    .filter(chat => selectedChats.includes(chat.id))
    .map(chat => chat.title)

  const getActionDescription = () => {
    switch (actionConfig.actionType) {
      case 'update_description':
        return `Обновить описание для ${selectedChats.length} чатов`
      case 'update_welcome':
        return `Настроить приветствие в ${selectedChats.length} чатах`
      case 'broadcast_message':
        return `Отправить сообщение в ${selectedChats.length} чатов`
      case 'chat_settings':
        return `Изменить настройки ${selectedChats.length} чатов`
      case 'user_management':
        return `Выполнить действия с пользователями в ${selectedChats.length} чатах`
      default:
        return `Выполнить действие в ${selectedChats.length} чатах`
    }
  }

  const getActionIcon = () => {
    switch (actionConfig.actionType) {
      case 'update_description': return '📝'
      case 'update_welcome': return '👋'
      case 'broadcast_message': return '📢'
      case 'chat_settings': return '⚙️'
      case 'user_management': return '👥'
      default: return '🛠️'
    }
  }

  const handleExecute = () => {
    if (actionConfig.confirmationRequired) {
      setShowConfirmation(true)
    } else {
      onExecute()
    }
  }

  const handleConfirmedExecute = () => {
    setShowConfirmation(false)
    onExecute()
  }

  const renderConfigPreview = () => {
    return (
      <div className="config-preview">
        <h4>Параметры действия:</h4>
        <div className="config-values">
          {Object.entries(actionConfig.values).map(([key, value]) => (
            <div key={key} className="config-item">
              <span className="config-key">{key}:</span>
              <span className="config-value">
                {typeof value === 'boolean'
                  ? (value ? 'Да' : 'Нет')
                  : typeof value === 'string' && value.length > 50
                    ? `${value.slice(0, 50)}...`
                    : String(value)
                }
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderExecutionResults = () => {
    if (!executionResults) return null

    return (
      <div className={`execution-results ${executionResults.success ? 'success' : 'error'}`}>
        <div className="results-header">
          <h4>
            {executionResults.success ? '✅ Операция завершена' : '❌ Операция не выполнена'}
          </h4>
        </div>

        {executionResults.error ? (
          <div className="error-message">
            <p>{executionResults.error}</p>
          </div>
        ) : (
          <div className="results-summary">
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-label">Всего чатов:</span>
                <span className="stat-value">{executionResults.totalChats}</span>
              </div>
              <div className="stat success">
                <span className="stat-label">Успешно:</span>
                <span className="stat-value">{executionResults.successCount}</span>
              </div>
              {executionResults.failureCount > 0 && (
                <div className="stat error">
                  <span className="stat-label">Ошибок:</span>
                  <span className="stat-value">{executionResults.failureCount}</span>
                </div>
              )}
            </div>

            {executionResults.results && executionResults.results.length > 0 && (
              <div className="detailed-results">
                <h5>Детальные результаты:</h5>
                <div className="results-list">
                  {executionResults.results.map(result => (
                    <div
                      key={result.chatId}
                      className={`result-item ${result.success ? 'success' : 'error'}`}
                    >
                      <div className="result-icon">
                        {result.success ? '✅' : '❌'}
                      </div>
                      <div className="result-info">
                        <div className="result-title">{result.chatTitle}</div>
                        {result.error && (
                          <div className="result-error">{result.error}</div>
                        )}
                        {result.changes && (
                          <div className="result-changes">
                            Изменения: {Object.keys(result.changes).join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="results-actions">
          <button onClick={onReset} className="reset-button">
            🔄 Начать заново
          </button>
        </div>
      </div>
    )
  }

  if (executionResults) {
    return (
      <div className="bulk-action-executor">
        {renderExecutionResults()}
      </div>
    )
  }

  return (
    <div className="bulk-action-executor">
      <div className="executor-header">
        <h3>
          {getActionIcon()} Выполнение действия
        </h3>
      </div>

      <div className="action-summary">
        <div className="summary-card">
          <div className="summary-title">
            {getActionDescription()}
          </div>

          <div className="selected-chats-preview">
            <h4>Выбранные чаты:</h4>
            <div className="chat-tags">
              {selectedChatTitles.slice(0, 3).map(title => (
                <span key={title} className="chat-tag">
                  {title}
                </span>
              ))}
              {selectedChatTitles.length > 3 && (
                <span className="chat-tag more">
                  +{selectedChatTitles.length - 3} еще
                </span>
              )}
            </div>
          </div>

          {renderConfigPreview()}
        </div>
      </div>

      <div className="executor-actions">
        <button
          onClick={handleExecute}
          disabled={isExecuting}
          className="execute-button primary"
        >
          {isExecuting ? (
            <>
              <div className="loading-spinner small"></div>
              Выполняется...
            </>
          ) : (
            <>
              ▶️ Выполнить действие
            </>
          )}
        </button>

        <button
          onClick={onReset}
          disabled={isExecuting}
          className="reset-button secondary"
        >
          🔄 Сбросить
        </button>
      </div>

      {showConfirmation && (
        <div className="confirmation-modal">
          <div className="modal-overlay" onClick={() => setShowConfirmation(false)}></div>
          <div className="modal-content">
            <div className="modal-header">
              <h3>⚠️ Подтверждение действия</h3>
            </div>
            <div className="modal-body">
              <p>
                Вы уверены, что хотите выполнить это действие для {selectedChats.length} чатов?
              </p>
              <div className="warning-note">
                <strong>Внимание:</strong> Это действие может быть необратимым.
              </div>
              {renderConfigPreview()}
            </div>
            <div className="modal-actions">
              <button
                onClick={handleConfirmedExecute}
                className="confirm-button primary"
              >
                ✅ Да, выполнить
              </button>
              <button
                onClick={() => setShowConfirmation(false)}
                className="cancel-button secondary"
              >
                ❌ Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BulkActionExecutor

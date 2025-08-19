import { useState, useMemo } from 'react'
import type { Chat, ChatFilters } from '../types'

interface ChatSelectionPanelProps {
  chats: Chat[]
  selectedChats: number[]
  onSelectionChange: (selectedIds: number[]) => void
}

const ChatSelectionPanel: React.FC<ChatSelectionPanelProps> = ({
  chats,
  selectedChats,
  onSelectionChange
}) => {
  const [filters, setFilters] = useState<ChatFilters>({
    search: '',
    type: [],
    isActive: undefined
  })
  const [showFilters, setShowFilters] = useState(false)

  // Filter chats based on current filters
  const filteredChats = useMemo(() => {
    return chats.filter(chat => {
      // Search filter
      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        const matchesTitle = chat.title.toLowerCase().includes(searchLower)
        const matchesDescription = chat.description?.toLowerCase().includes(searchLower)
        if (!matchesTitle && !matchesDescription) return false
      }

      // Type filter
      if (filters.type.length > 0 && !filters.type.includes(chat.type)) {
        return false
      }

      // Active filter
      if (filters.isActive !== undefined && chat.is_active !== filters.isActive) {
        return false
      }

      // Member count filters
      if (filters.memberCountMin && (chat.member_count || 0) < filters.memberCountMin) {
        return false
      }
      if (filters.memberCountMax && (chat.member_count || 0) > filters.memberCountMax) {
        return false
      }

      return true
    })
  }, [chats, filters])

  const handleChatToggle = (chatId: number) => {
    const newSelection = selectedChats.includes(chatId)
      ? selectedChats.filter(id => id !== chatId)
      : [...selectedChats, chatId]
    onSelectionChange(newSelection)
  }

  const handleSelectAll = () => {
    const allFilteredIds = filteredChats.map(chat => chat.id)
    onSelectionChange(allFilteredIds)
  }

  const handleSelectNone = () => {
    onSelectionChange([])
  }

  const handleInvertSelection = () => {
    const filteredIds = filteredChats.map(chat => chat.id)
    const newSelection = filteredIds.filter(id => !selectedChats.includes(id))
    onSelectionChange([...selectedChats.filter(id => !filteredIds.includes(id)), ...newSelection])
  }

  const formatChatType = (type: string) => {
    const types = {
      'group': '👥 Группа',
      'supergroup': '🔥 Супергруппа',
      'channel': '📢 Канал'
    }
    return types[type as keyof typeof types] || type
  }

  const formatMemberCount = (count?: number) => {
    if (!count) return 'Неизвестно'
    if (count < 1000) return count.toString()
    if (count < 1000000) return `${(count / 1000).toFixed(1)}K`
    return `${(count / 1000000).toFixed(1)}M`
  }

  return (
    <div className="chat-selection-panel">
      <div className="panel-header">
        <h3>📋 Выбор чатов</h3>
        <div className="header-actions">
          <button
            className="filter-toggle"
            onClick={() => setShowFilters(!showFilters)}
          >
            🔍 Фильтры
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="filters-section">
          <div className="filter-row">
            <input
              type="text"
              placeholder="Поиск по названию или описанию..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="search-input"
            />
          </div>

          <div className="filter-row">
            <div className="filter-group">
              <label>Тип чата:</label>
              <div className="checkbox-group">
                {['group', 'supergroup', 'channel'].map(type => (
                  <label key={type} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.type.includes(type)}
                      onChange={(e) => {
                        const newTypes = e.target.checked
                          ? [...filters.type, type]
                          : filters.type.filter(t => t !== type)
                        setFilters(prev => ({ ...prev, type: newTypes }))
                      }}
                    />
                    {formatChatType(type)}
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="filter-row">
            <div className="filter-group">
              <label>Статус:</label>
              <select
                value={filters.isActive === undefined ? '' : filters.isActive ? 'true' : 'false'}
                onChange={(e) => {
                  const value = e.target.value === '' ? undefined : e.target.value === 'true'
                  setFilters(prev => ({ ...prev, isActive: value }))
                }}
                className="status-select"
              >
                <option value="">Все</option>
                <option value="true">Активные</option>
                <option value="false">Неактивные</option>
              </select>
            </div>
          </div>
        </div>
      )}

      <div className="selection-controls">
        <div className="selection-info">
          <span>
            Показано: <strong>{filteredChats.length}</strong> из {chats.length}
          </span>
          <span>
            Выбрано: <strong>{selectedChats.length}</strong>
          </span>
        </div>

        <div className="selection-actions">
          <button onClick={handleSelectAll} className="action-btn select-all">
            Выбрать все
          </button>
          <button onClick={handleSelectNone} className="action-btn select-none">
            Снять все
          </button>
          <button onClick={handleInvertSelection} className="action-btn invert">
            Инвертировать
          </button>
        </div>
      </div>

      <div className="chat-list">
        {filteredChats.length === 0 ? (
          <div className="empty-state">
            <p>🔍 Чаты не найдены</p>
            <p className="hint">Попробуйте изменить условия поиска</p>
          </div>
        ) : (
          filteredChats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${selectedChats.includes(chat.id) ? 'selected' : ''}`}
              onClick={() => handleChatToggle(chat.id)}
            >
              <div className="chat-checkbox">
                <input
                  type="checkbox"
                  checked={selectedChats.includes(chat.id)}
                  onChange={() => {}} // Handled by parent div click
                />
              </div>

              <div className="chat-info">
                <div className="chat-header">
                  <h4 className="chat-title">{chat.title}</h4>
                  <div className="chat-badges">
                    <span className="chat-type">{formatChatType(chat.type)}</span>
                    <span className={`chat-status ${chat.is_active ? 'active' : 'inactive'}`}>
                      {chat.is_active ? '🟢' : '🔴'}
                    </span>
                  </div>
                </div>

                <div className="chat-meta">
                  <span className="member-count">
                    👥 {formatMemberCount(chat.member_count)}
                  </span>
                  <span className="chat-id">ID: {chat.id}</span>
                </div>

                {chat.description && (
                  <p className="chat-description">{chat.description}</p>
                )}

                {chat.welcome_message && (
                  <div className="welcome-preview">
                    <span className="welcome-label">👋 Приветствие:</span>
                    <span className="welcome-text">
                      {chat.welcome_message.length > 50
                        ? `${chat.welcome_message.slice(0, 50)}...`
                        : chat.welcome_message}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ChatSelectionPanel

import { useState, useEffect } from 'react'
import type { BulkActionType, BulkActionConfig, ActionField } from '../types'

interface ActionConfigPanelProps {
  onConfigChange: (config: BulkActionConfig | null) => void
  selectedCount: number
}

const BULK_ACTIONS: BulkActionType[] = [
  {
    id: 'update_description',
    name: 'Изменить описание',
    icon: '📝',
    description: 'Массовое обновление описания чатов',
    category: 'content',
    fields: [
      {
        key: 'description',
        label: 'Новое описание',
        type: 'textarea',
        required: true,
        placeholder: 'Введите новое описание для выбранных чатов...',
        validation: { maxLength: 500 }
      }
    ]
  },
  {
    id: 'update_welcome',
    name: 'Настроить приветствие',
    icon: '👋',
    description: 'Изменить приветственное сообщение',
    category: 'content',
    fields: [
      {
        key: 'welcome_message',
        label: 'Текст приветствия',
        type: 'textarea',
        required: true,
        placeholder: 'Добро пожаловать в наш чат! 🎓',
        validation: { maxLength: 1000 }
      },
      {
        key: 'auto_delete_delay',
        label: 'Автоудаление через (сек)',
        type: 'number',
        placeholder: '300',
        validation: { min: 10, max: 3600 }
      }
    ]
  },
  {
    id: 'broadcast_message',
    name: 'Отправить сообщение',
    icon: '📢',
    description: 'Массовая рассылка сообщений в чаты',
    category: 'communication',
    fields: [
      {
        key: 'message',
        label: 'Текст сообщения',
        type: 'textarea',
        required: true,
        placeholder: 'Важное объявление для всех участников...',
        validation: { maxLength: 2000 }
      },
      {
        key: 'pin_message',
        label: 'Закрепить сообщение',
        type: 'boolean'
      }
    ]
  },
  {
    id: 'chat_settings',
    name: 'Настройки чата',
    icon: '⚙️',
    description: 'Изменить основные настройки чатов',
    category: 'settings',
    fields: [
      {
        key: 'is_active',
        label: 'Активировать чат',
        type: 'boolean'
      },
      {
        key: 'moderation_level',
        label: 'Уровень модерации',
        type: 'select',
        options: [
          { value: 'low', label: 'Низкий' },
          { value: 'medium', label: 'Средний' },
          { value: 'high', label: 'Высокий' }
        ]
      }
    ]
  },
  {
    id: 'user_management',
    name: 'Управление пользователями',
    icon: '👥',
    description: 'Массовые операции с пользователями',
    category: 'moderation',
    fields: [
      {
        key: 'action_type',
        label: 'Тип действия',
        type: 'select',
        required: true,
        options: [
          { value: 'kick_inactive', label: 'Исключить неактивных' },
          { value: 'mute_all', label: 'Заглушить всех' },
          { value: 'promote_admins', label: 'Назначить админов' }
        ]
      },
      {
        key: 'duration',
        label: 'Длительность (мин)',
        type: 'number',
        placeholder: '60',
        validation: { min: 1, max: 10080 }
      }
    ]
  }
]

const ActionConfigPanel: React.FC<ActionConfigPanelProps> = ({
  onConfigChange,
  selectedCount
}) => {
  const [selectedAction, setSelectedAction] = useState<BulkActionType | null>(null)
  const [values, setValues] = useState<Record<string, unknown>>({})
  const [applyTo, setApplyTo] = useState<'selected' | 'all'>('selected')

  useEffect(() => {
    if (selectedAction) {
      const config: BulkActionConfig = {
        actionType: selectedAction.id,
        values,
        applyTo,
        confirmationRequired: selectedAction.category === 'moderation'
      }
      onConfigChange(config)
    } else {
      onConfigChange(null)
    }
  }, [selectedAction, values, applyTo, onConfigChange])

  const handleActionSelect = (action: BulkActionType) => {
    setSelectedAction(action)
    setValues({})
  }

  const handleValueChange = (key: string, value: unknown) => {
    setValues(prev => ({ ...prev, [key]: value }))
  }

  const renderField = (field: ActionField) => {
    const value = values[field.key] || ''

    switch (field.type) {
      case 'text':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleValueChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            className="field-input"
          />
        )

      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleValueChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            className="field-textarea"
            rows={4}
          />
        )

      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleValueChange(field.key, parseInt(e.target.value))}
            placeholder={field.placeholder}
            min={field.validation?.min}
            max={field.validation?.max}
            className="field-input"
          />
        )

      case 'boolean':
        return (
          <label className="field-checkbox">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) => handleValueChange(field.key, e.target.checked)}
            />
            <span className="checkmark"></span>
          </label>
        )

      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleValueChange(field.key, e.target.value)}
            className="field-select"
          >
            <option value="">Выберите вариант</option>
            {field.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        )

      default:
        return null
    }
  }

  const groupedActions = BULK_ACTIONS.reduce((acc, action) => {
    if (!acc[action.category]) acc[action.category] = []
    acc[action.category].push(action)
    return acc
  }, {} as Record<string, BulkActionType[]>)

  const categoryNames = {
    content: 'Контент',
    settings: 'Настройки',
    moderation: 'Модерация',
    communication: 'Коммуникации'
  }

  return (
    <div className="action-config-panel">
      <div className="panel-header">
        <h3>🛠️ Настройка действий</h3>
        <div className="selection-counter">
          {selectedCount > 0 ? (
            <span className="counter-badge">{selectedCount} выбрано</span>
          ) : (
            <span className="counter-empty">Выберите чаты</span>
          )}
        </div>
      </div>

      {!selectedAction ? (
        <div className="action-selector">
          <div className="action-grid-compact">
            {Object.entries(groupedActions).map(([category, actions]) => (
              <div key={category} className="action-category-compact">
                <h4 className="category-title-compact">
                  {categoryNames[category as keyof typeof categoryNames]}
                </h4>
                <div className="actions-row">
                  {actions.map(action => (
                    <button
                      key={action.id}
                      className="action-card-compact"
                      onClick={() => handleActionSelect(action)}
                      disabled={selectedCount === 0}
                      title={action.description}
                    >
                      <div className="action-icon-compact">{action.icon}</div>
                      <div className="action-name-compact">{action.name}</div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="action-config-expanded">
          <div className="config-header-expanded">
            <button
              className="back-button-expanded"
              onClick={() => setSelectedAction(null)}
            >
              ← Назад
            </button>
            <div className="config-title-expanded">
              <span className="config-icon">{selectedAction.icon}</span>
              <h4>{selectedAction.name}</h4>
            </div>
          </div>

          <div className="config-form-expanded">
            {selectedAction.fields.map(field => (
              <div key={field.key} className="field-group-expanded">
                <label className="field-label-expanded">
                  {field.label}
                  {field.required && <span className="required">*</span>}
                </label>
                {renderField(field)}
              </div>
            ))}

            <div className="apply-options-expanded">
              <label className="apply-option-expanded">
                <input
                  type="radio"
                  value="selected"
                  checked={applyTo === 'selected'}
                  onChange={(e) => setApplyTo(e.target.value as 'selected')}
                />
                <span>Применить к выбранным <strong>({selectedCount})</strong> чатам</span>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ActionConfigPanel

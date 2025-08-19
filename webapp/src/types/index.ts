export interface Chat {
  id: number
  title: string
  type: 'group' | 'supergroup' | 'channel'
  member_count?: number
  description?: string
  welcome_message?: string
  auto_delete_welcome_delay?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BulkActionType {
  id: string
  name: string
  icon: string
  description: string
  category: 'content' | 'settings' | 'moderation' | 'communication'
  fields: ActionField[]
}

export interface ActionField {
  key: string
  label: string
  type: 'text' | 'textarea' | 'number' | 'boolean' | 'select'
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  validation?: {
    minLength?: number
    maxLength?: number
    min?: number
    max?: number
  }
}

export interface BulkActionConfig {
  actionType: string
  values: Record<string, unknown>
  applyTo: 'selected' | 'all' | 'filtered'
  confirmationRequired: boolean
}

export interface BulkExecutionResult {
  success: boolean
  totalChats: number
  successCount: number
  failureCount: number
  results: ChatUpdateResult[]
  error?: string
}

export interface ChatUpdateResult {
  chatId: number
  chatTitle: string
  success: boolean
  error?: string
  changes?: Record<string, unknown>
}

export interface ChatFilters {
  search: string
  type: string[]
  memberCountMin?: number
  memberCountMax?: number
  isActive?: boolean
}

export interface ChatStats {
  totalChats: number
  activeChats: number
  totalMembers: number
  averageMembers: number
  chatsByType: Record<string, number>
}

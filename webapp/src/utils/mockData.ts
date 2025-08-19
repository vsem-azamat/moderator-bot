import type { Chat, BulkActionConfig, BulkExecutionResult } from '../types'

// Mock chat data
export const mockChatsData: Chat[] = [
  {
    id: 1,
    title: 'Программирование в Чехии',
    type: 'supergroup',
    member_count: 15420,
    description: 'Чат для IT-специалистов в Чешской Республике',
    welcome_message: 'Добро пожаловать в сообщество программистов! 🚀',
    auto_delete_welcome_delay: 300,
    is_active: true,
    created_at: '2023-01-15T10:00:00Z',
    updated_at: '2024-12-19T14:30:00Z'
  },
  {
    id: 2,
    title: 'Изучаем чешский язык',
    type: 'group',
    member_count: 8750,
    description: 'Изучение чешского языка для русскоговорящих',
    welcome_message: 'Dobrý den! Добро пожаловать в языковую группу! 🇨🇿',
    is_active: true,
    created_at: '2023-03-20T15:20:00Z',
    updated_at: '2024-12-18T09:15:00Z'
  },
  {
    id: 3,
    title: 'Работа в Праге',
    type: 'supergroup',
    member_count: 23100,
    description: 'Поиск работы и вакансии в Праге',
    welcome_message: 'Добро пожаловать! Здесь вы найдете работу своей мечты в Праге 💼',
    auto_delete_welcome_delay: 600,
    is_active: true,
    created_at: '2023-02-10T12:45:00Z',
    updated_at: '2024-12-19T16:00:00Z'
  },
  {
    id: 4,
    title: 'Студенты в Чехии',
    type: 'group',
    member_count: 5640,
    description: 'Сообщество студентов и абитуриентов',
    welcome_message: 'Привет, студент! 🎓 Здесь ты найдешь всю нужную информацию!',
    is_active: false,
    created_at: '2023-05-12T08:30:00Z',
    updated_at: '2024-11-20T11:45:00Z'
  },
  {
    id: 5,
    title: 'Новости IT Чехия',
    type: 'channel',
    member_count: 12890,
    description: 'Актуальные новости IT-сферы в Чешской Республике',
    is_active: true,
    created_at: '2023-04-01T14:20:00Z',
    updated_at: '2024-12-19T10:30:00Z'
  },
  {
    id: 6,
    title: 'Поиск жилья Прага',
    type: 'supergroup',
    member_count: 18500,
    description: 'Поиск и сдача жилья в Праге и окрестностях',
    welcome_message: 'Добро пожаловать в группу поиска жилья! 🏠',
    auto_delete_welcome_delay: 480,
    is_active: true,
    created_at: '2023-01-25T16:10:00Z',
    updated_at: '2024-12-19T12:20:00Z'
  },
  {
    id: 7,
    title: 'Авто в Чехии',
    type: 'group',
    member_count: 4200,
    description: 'Покупка, продажа и обслуживание автомобилей',
    welcome_message: 'Добро пожаловать в автомобильное сообщество! 🚗',
    is_active: true,
    created_at: '2023-06-15T11:00:00Z',
    updated_at: '2024-12-17T14:45:00Z'
  },
  {
    id: 8,
    title: 'Медицина в Чехии',
    type: 'group',
    member_count: 3100,
    description: 'Медицинская помощь и страхование для иностранцев',
    welcome_message: 'Здравствуйте! Здесь вы найдете ответы на медицинские вопросы 🏥',
    is_active: false,
    created_at: '2023-07-08T13:30:00Z',
    updated_at: '2024-10-12T09:20:00Z'
  },
  {
    id: 9,
    title: 'Путешествия по Чехии',
    type: 'supergroup',
    member_count: 9800,
    description: 'Туризм, достопримечательности и путешествия',
    welcome_message: 'Добро пожаловать в сообщество путешественников! 🗺️',
    auto_delete_welcome_delay: 300,
    is_active: true,
    created_at: '2023-08-22T17:15:00Z',
    updated_at: '2024-12-18T15:30:00Z'
  },
  {
    id: 10,
    title: 'Бизнес в Чехии',
    type: 'group',
    member_count: 6700,
    description: 'Открытие и ведение бизнеса в ЧР',
    welcome_message: 'Добро пожаловать в бизнес-сообщество! 💼',
    is_active: true,
    created_at: '2023-09-10T10:45:00Z',
    updated_at: '2024-12-19T11:10:00Z'
  }
]

// Mock API functions
export const mockChats = async (): Promise<Chat[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 800))
  return mockChatsData
}

export const mockBulkUpdate = async (
  chatIds: number[],
  config: BulkActionConfig
): Promise<BulkExecutionResult> => {
  // Simulate API processing time
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Simulate some failures (10% failure rate)
  const results = chatIds.map(chatId => {
    const chat = mockChatsData.find(c => c.id === chatId)
    const success = Math.random() > 0.1 // 90% success rate

    return {
      chatId,
      chatTitle: chat?.title || `Chat ${chatId}`,
      success,
      error: success ? undefined : 'Временная ошибка API Telegram',
      changes: success ? config.values : undefined
    }
  })

  const successCount = results.filter(r => r.success).length
  const failureCount = results.length - successCount

  return {
    success: failureCount === 0,
    totalChats: chatIds.length,
    successCount,
    failureCount,
    results
  }
}

// Export mock stats for future analytics
export const mockChatStats = {
  totalChats: mockChatsData.length,
  activeChats: mockChatsData.filter(c => c.is_active).length,
  totalMembers: mockChatsData.reduce((sum, chat) => sum + (chat.member_count || 0), 0),
  averageMembers: Math.round(
    mockChatsData.reduce((sum, chat) => sum + (chat.member_count || 0), 0) / mockChatsData.length
  ),
  chatsByType: mockChatsData.reduce((acc, chat) => {
    acc[chat.type] = (acc[chat.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)
}

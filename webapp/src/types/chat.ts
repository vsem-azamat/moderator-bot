export interface Chat {
  id: number;
  title?: string;
  is_forum: boolean;
  welcome_message?: string;
  welcome_delete_time: number;
  is_welcome_enabled: boolean;
  is_captcha_enabled: boolean;
  created_at?: string;
  modified_at?: string;
}

export interface ChatStats {
  chat_id: number;
  member_count: number;
  message_count_24h: number;
  active_users_24h: number;
  moderation_actions_24h: number;
  last_activity?: string;
}

export interface ChatUpdateData {
  welcome_message?: string;
  welcome_delete_time?: number;
  is_welcome_enabled?: boolean;
  is_captcha_enabled?: boolean;
}

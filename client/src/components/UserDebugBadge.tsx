import { useTelegram } from '@/contexts/TelegramContext';
import { Badge } from '@/components/ui/badge';

export function UserDebugBadge() {
  const { user, telegramData } = useTelegram();

  if (!user) return null;

  const isTelegramUser = !!telegramData;
  const isMockUser = user.telegram_id === 123456789;

  return (
    <div className="fixed top-2 right-2 z-50" data-testid="user-debug-badge">
      <Badge 
        variant={isTelegramUser ? "default" : "secondary"}
        className="flex items-center gap-2 px-3 py-1"
      >
        <span className="text-xs">
          {isTelegramUser ? '🔵 Telegram' : '🟡 Browser'}
        </span>
        <div className="text-xs opacity-80">
          ID: {user.telegram_id}
        </div>
        {isMockUser && (
          <span className="text-xs font-bold">ТЕСТ</span>
        )}
      </Badge>
      <div className="mt-1 text-[10px] text-right text-muted-foreground">
        User: {user.id.slice(0, 8)}...
      </div>
    </div>
  );
}

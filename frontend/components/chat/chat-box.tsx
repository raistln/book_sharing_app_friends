'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import { useAuth } from '@/lib/hooks/use-auth';
import { useMessages, useSendMessage } from '@/lib/hooks/use-chat';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Loader2, Send, MessageCircle, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatBoxProps {
  loanId: string;
  otherUser: {
    id: string;
    username: string;
    avatar_url?: string;
  };
}

export function ChatBox({ loanId, otherUser }: ChatBoxProps) {
  const { user } = useAuth();
  const { messages, isLoading, refetch, resetTimestamp } = useMessages(loanId);
  const sendMessage = useSendMessage();
  const [newMessage, setNewMessage] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al último mensaje
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    sendMessage.mutate(
      {
        loan_id: loanId,
        content: newMessage.trim(),
      },
      {
        onSuccess: () => {
          setNewMessage('');
          // Refrescar para obtener el mensaje enviado y actualizar el timestamp
          refetch();
        },
      }
    );
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-storybook-gold-light rounded-full flex items-center justify-center">
            {otherUser.avatar_url ? (
              <Image
                src={otherUser.avatar_url}
                alt={otherUser.username}
                width={40}
                height={40}
                className="h-full w-full rounded-full object-cover"
              />
            ) : (
              <User className="h-5 w-5 text-storybook-leather" />
            )}
          </div>
          <div>
            <CardTitle className="text-lg">Chat con {otherUser.username}</CardTitle>
            <CardDescription className="text-xs">
              {messages.length} {messages.length === 1 ? 'mensaje' : 'mensajes'}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Messages Area */}
        <ScrollArea className="flex-1 px-4" ref={scrollRef}>
          {isLoading ? (
            <div className="flex justify-center items-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-storybook-leather" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <MessageCircle className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light text-sm">
                No hay mensajes aún. ¡Inicia la conversaci&oacute;n!
              </p>
            </div>
          ) : (
            <div className="space-y-4 py-4">
              {messages.map((message) => {
                const isOwnMessage = message.sender_id === user?.id;
                return (
                  <div
                    key={message.id}
                    className={cn(
                      'flex',
                      isOwnMessage ? 'justify-end' : 'justify-start'
                    )}
                  >
                    <div
                      className={cn(
                        'max-w-[70%] rounded-lg px-4 py-2',
                        isOwnMessage
                          ? 'bg-storybook-leather text-storybook-cream'
                          : 'bg-storybook-parchment text-storybook-ink'
                      )}
                    >
                      <p className="text-sm whitespace-pre-wrap break-words">
                        {message.content}
                      </p>
                      <p
                        className={cn(
                          'text-xs mt-1',
                          isOwnMessage
                            ? 'text-storybook-gold-light'
                            : 'text-storybook-ink-light'
                        )}
                      >
                        {new Date(message.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Escribe un mensaje..."
              disabled={sendMessage.isPending}
              className="flex-1"
              maxLength={500}
            />
            <Button
              type="submit"
              disabled={!newMessage.trim() || sendMessage.isPending}
              size="icon"
            >
              {sendMessage.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
          <p className="text-xs text-storybook-ink-light mt-2">
            {newMessage.length}/500 caracteres
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

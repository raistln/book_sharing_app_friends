// Mensaje de chat
export interface Message {
  id: string;
  loan_id: string;
  sender_id: string;
  content: string;
  created_at: string;
  
  // Información del remitente (opcional, puede venir del backend)
  sender?: {
    id: string;
    username: string;
    avatar_url?: string;
  };
}

// Crear mensaje
export interface MessageCreate {
  loan_id: string;
  content: string;
}

// Conversación (lista de mensajes de un préstamo)
export interface Conversation {
  loan_id: string;
  messages: Message[];
  participants: {
    lender: {
      id: string;
      username: string;
      avatar_url?: string;
    };
    borrower: {
      id: string;
      username: string;
      avatar_url?: string;
    };
  };
}

import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';

const useChatStore = create((set, get) => ({
  messages: [],
  sessionId: uuidv4(),
  isConnected: false,
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  clearMessages: () => set({ messages: [] }),
  
  updateMessage: (messageId, updates) => set((state) => ({
    messages: state.messages.map(msg =>
      msg.id === messageId ? { ...msg, ...updates } : msg
    )
  })),
  
  setSessionId: (sessionId) => set({ sessionId }),
  
  setConnected: (connected) => set({ isConnected: connected }),
  
  getLastMessage: () => {
    const { messages } = get();
    return messages[messages.length - 1];
  },
  
  getMessagesByRole: (role) => {
    const { messages } = get();
    return messages.filter(msg => msg.role === role);
  }
}));

export { useChatStore };

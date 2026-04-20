import { create } from 'zustand';
import type { Organisation, GateStatus } from '../types';

interface Notification {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  timestamp: string;
}

interface AppState {
  currentOrg: Organisation | null;
  gates: GateStatus[];
  notifications: Notification[];
  sidebarOpen: boolean;
  setCurrentOrg: (org: Organisation | null) => void;
  setGates: (gates: GateStatus[]) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentOrg: null,
  gates: [],
  notifications: [],
  sidebarOpen: false,
  setCurrentOrg: (org) => set({ currentOrg: org }),
  setGates: (gates) => set({ gates }),
  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          ...notification,
          id: crypto.randomUUID(),
          timestamp: new Date().toISOString(),
        },
      ],
    })),
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
  clearNotifications: () => set({ notifications: [] }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));

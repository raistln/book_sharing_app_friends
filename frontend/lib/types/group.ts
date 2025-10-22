import type { User } from './api';

// Roles de miembros
export type MemberRole = 'admin' | 'member';

// Miembro de grupo
export interface GroupMember {
  id: string;
  group_id: string;
  user_id: string;
  role: MemberRole;
  joined_at: string;
  invited_by?: string;
}

// Miembro con información de usuario
export interface GroupMemberWithUser {
  user: User;
  role: MemberRole;
  joined_at: string;
}

// Grupo completo
export interface Group {
  id: string;
  name: string;
  description?: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
  members: GroupMemberWithUser[];
}

// Resumen de grupo
export interface GroupSummary {
  id: string;
  name: string;
  description?: string;
  member_count: number;
  admin_count: number;
  created_at: string;
  is_admin: boolean;
}

// Crear grupo
export interface GroupCreate {
  name: string;
  description?: string;
}

// Actualizar grupo
export interface GroupUpdate {
  name?: string;
  description?: string;
}

// Añadir miembro
export interface GroupMemberCreate {
  user_id: string;
  role?: MemberRole;
}

// Actualizar rol de miembro
export interface GroupMemberUpdate {
  role: MemberRole;
}

// Invitación
export interface Invitation {
  id: string;
  group_id: string;
  email?: string;
  code: string;
  message?: string;
  invited_by: string;
  created_at: string;
  expires_at: string;
  is_accepted?: boolean;
  responded_at?: string;
  group?: {
    name: string;
  };
  invited_by_username?: string;
}

// Crear invitación
export interface InvitationCreate {
  email?: string;
  username?: string;
  message?: string;
}

// Responder invitación
export interface InvitationResponse {
  code: string;
  accept: boolean;
}

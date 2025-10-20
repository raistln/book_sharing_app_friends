import { apiClient } from './client';
import type {
  Group,
  GroupSummary,
  GroupCreate,
  GroupUpdate,
  GroupMember,
  GroupMemberCreate,
  GroupMemberUpdate,
  GroupMemberWithUser,
  Invitation,
  InvitationCreate,
  InvitationResponse,
} from '@/lib/types/group';

export const groupsApi = {
  // Obtener todos los grupos del usuario
  async getMyGroups(): Promise<GroupSummary[]> {
    const response = await apiClient.get<GroupSummary[]>('/groups/');
    return response.data;
  },

  // Obtener detalles de un grupo
  async getGroup(groupId: string): Promise<Group> {
    const response = await apiClient.get<Group>(`/groups/${groupId}`);
    return response.data;
  },

  // Crear un nuevo grupo
  async createGroup(data: GroupCreate): Promise<Group> {
    const response = await apiClient.post<Group>('/groups/', data);
    return response.data;
  },

  // Actualizar un grupo
  async updateGroup(groupId: string, data: GroupUpdate): Promise<Group> {
    const response = await apiClient.put<Group>(`/groups/${groupId}`, data);
    return response.data;
  },

  // Eliminar un grupo
  async deleteGroup(groupId: string): Promise<void> {
    await apiClient.delete(`/groups/${groupId}`);
  },

  // Obtener miembros de un grupo
  async getGroupMembers(groupId: string): Promise<GroupMemberWithUser[]> {
    const response = await apiClient.get<GroupMemberWithUser[]>(
      `/groups/${groupId}/members`
    );
    return response.data;
  },

  // Añadir un miembro al grupo
  async addMember(groupId: string, data: GroupMemberCreate): Promise<void> {
    await apiClient.post(`/groups/${groupId}/members`, data);
  },

  // Actualizar rol de un miembro
  async updateMemberRole(
    groupId: string,
    memberId: string,
    data: GroupMemberUpdate
  ): Promise<void> {
    await apiClient.put(`/groups/${groupId}/members/${memberId}`, data);
  },

  // Eliminar un miembro del grupo
  async removeMember(groupId: string, memberId: string): Promise<void> {
    await apiClient.delete(`/groups/${groupId}/members/${memberId}`);
  },

  // Salir de un grupo
  async leaveGroup(groupId: string): Promise<void> {
    await apiClient.post(`/groups/${groupId}/leave`);
  },

  // Crear invitación
  async createInvitation(
    groupId: string,
    data: InvitationCreate
  ): Promise<Invitation> {
    const response = await apiClient.post<Invitation>(
      `/groups/${groupId}/invitations`,
      data
    );
    return response.data;
  },

  // Obtener invitaciones del grupo
  async getGroupInvitations(groupId: string): Promise<Invitation[]> {
    const response = await apiClient.get<Invitation[]>(
      `/groups/${groupId}/invitations`
    );
    return response.data;
  },

  // Obtener invitación por código
  async getInvitationByCode(code: string): Promise<Invitation> {
    const response = await apiClient.get<Invitation>(
      `/groups/invitations/by-code/${code}`
    );
    return response.data;
  },

  // Responder a una invitación por código
  async respondToInvitation(data: InvitationResponse): Promise<GroupMember> {
    const response = await apiClient.post<GroupMember>(
      `/groups/invitations/accept/${data.code}`
    );
    return response.data;
  },

  // Cancelar invitación
  async cancelInvitation(groupId: string, invitationId: string): Promise<void> {
    await apiClient.delete(`/groups/${groupId}/invitations/${invitationId}`);
  },
};

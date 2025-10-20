import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { groupsApi } from '@/lib/api/groups';
import { toast } from '@/components/ui/use-toast';
import type {
  GroupCreate,
  GroupUpdate,
  GroupMemberCreate,
  GroupMemberUpdate,
  InvitationCreate,
  InvitationResponse,
} from '@/lib/types/group';

// Hook para obtener todos los grupos del usuario
export function useMyGroups() {
  const { data: groups = [], isLoading, error } = useQuery({
    queryKey: ['myGroups'],
    queryFn: groupsApi.getMyGroups,
  });

  return { groups, isLoading, error };
}

// Hook para obtener un grupo específico
export function useGroup(groupId: string) {
  const { data: group, isLoading, error } = useQuery({
    queryKey: ['group', groupId],
    queryFn: () => groupsApi.getGroup(groupId),
    enabled: !!groupId,
  });

  return { group, isLoading, error };
}

// Hook para obtener miembros de un grupo
export function useGroupMembers(groupId: string) {
  const { data: members = [], isLoading, error } = useQuery({
    queryKey: ['groupMembers', groupId],
    queryFn: () => groupsApi.getGroupMembers(groupId),
    enabled: !!groupId,
  });

  return { members, isLoading, error };
}

// Hook para obtener invitaciones de un grupo
export function useGroupInvitations(groupId: string) {
  const { data: invitations = [], isLoading, error } = useQuery({
    queryKey: ['groupInvitations', groupId],
    queryFn: () => groupsApi.getGroupInvitations(groupId),
    enabled: !!groupId,
  });

  return { invitations, isLoading, error };
}

// Hook para crear un grupo
export function useCreateGroup() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: groupsApi.createGroup,
    onSuccess: (newGroup) => {
      queryClient.invalidateQueries({ queryKey: ['myGroups'] });
      toast({
        title: '¡Grupo creado! 👥',
        description: `"${newGroup.name}" ha sido creado exitosamente`,
      });
      router.push(`/groups/${newGroup.id}`);
    },
    onError: (error: any) => {
      toast({
        title: 'Error al crear grupo',
        description: error.response?.data?.detail || 'No se pudo crear el grupo',
        variant: 'destructive',
      });
    },
  });
}

// Hook para actualizar un grupo
export function useUpdateGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ groupId, data }: { groupId: string; data: GroupUpdate }) =>
      groupsApi.updateGroup(groupId, data),
    onSuccess: (updatedGroup) => {
      queryClient.invalidateQueries({ queryKey: ['myGroups'] });
      queryClient.invalidateQueries({ queryKey: ['group', updatedGroup.id] });
      toast({
        title: '¡Grupo actualizado! ✨',
        description: 'Los cambios se han guardado correctamente',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al actualizar',
        description: error.response?.data?.detail || 'No se pudo actualizar el grupo',
        variant: 'destructive',
      });
    },
  });
}

// Hook para eliminar un grupo
export function useDeleteGroup() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: groupsApi.deleteGroup,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myGroups'] });
      toast({
        title: 'Grupo eliminado',
        description: 'El grupo ha sido eliminado correctamente',
      });
      router.push('/groups');
    },
    onError: (error: any) => {
      toast({
        title: 'Error al eliminar',
        description: error.response?.data?.detail || 'No se pudo eliminar el grupo',
        variant: 'destructive',
      });
    },
  });
}

// Hook para añadir un miembro
export function useAddMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ groupId, data }: { groupId: string; data: GroupMemberCreate }) =>
      groupsApi.addMember(groupId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['group', variables.groupId] });
      queryClient.invalidateQueries({ queryKey: ['groupMembers', variables.groupId] });
      toast({
        title: 'Miembro añadido',
        description: 'El usuario ha sido añadido al grupo',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al añadir miembro',
        description: error.response?.data?.detail || 'No se pudo añadir el miembro',
        variant: 'destructive',
      });
    },
  });
}

// Hook para actualizar rol de miembro
export function useUpdateMemberRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      groupId,
      memberId,
      data,
    }: {
      groupId: string;
      memberId: string;
      data: GroupMemberUpdate;
    }) => groupsApi.updateMemberRole(groupId, memberId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['group', variables.groupId] });
      queryClient.invalidateQueries({ queryKey: ['groupMembers', variables.groupId] });
      toast({
        title: 'Rol actualizado',
        description: 'El rol del miembro ha sido actualizado',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al actualizar rol',
        description: error.response?.data?.detail || 'No se pudo actualizar el rol',
        variant: 'destructive',
      });
    },
  });
}

// Hook para eliminar un miembro
export function useRemoveMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ groupId, memberId }: { groupId: string; memberId: string }) =>
      groupsApi.removeMember(groupId, memberId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['group', variables.groupId] });
      queryClient.invalidateQueries({ queryKey: ['groupMembers', variables.groupId] });
      toast({
        title: 'Miembro eliminado',
        description: 'El usuario ha sido eliminado del grupo',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al eliminar miembro',
        description: error.response?.data?.detail || 'No se pudo eliminar el miembro',
        variant: 'destructive',
      });
    },
  });
}

// Hook para salir de un grupo
export function useLeaveGroup() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: groupsApi.leaveGroup,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myGroups'] });
      toast({
        title: 'Has salido del grupo',
        description: 'Ya no eres miembro de este grupo',
      });
      router.push('/groups');
    },
    onError: (error: any) => {
      toast({
        title: 'Error al salir',
        description: error.response?.data?.detail || 'No se pudo salir del grupo',
        variant: 'destructive',
      });
    },
  });
}

// Hook para crear invitación
export function useCreateInvitation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ groupId, data }: { groupId: string; data: InvitationCreate }) =>
      groupsApi.createInvitation(groupId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['groupInvitations', variables.groupId] });
      toast({
        title: 'Invitación creada',
        description: 'La invitación ha sido enviada correctamente',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al crear invitación',
        description: error.response?.data?.detail || 'No se pudo crear la invitación',
        variant: 'destructive',
      });
    },
  });
}

// Hook para responder invitación
export function useRespondInvitation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: groupsApi.respondToInvitation,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['myGroups'] });
      if (variables.accept) {
        toast({
          title: '¡Bienvenido al grupo! 🎉',
          description: 'Te has unido al grupo exitosamente',
        });
        router.push('/groups');
      } else {
        toast({
          title: 'Invitación rechazada',
          description: 'Has rechazado la invitación al grupo',
        });
      }
    },
    onError: (error: any) => {
      toast({
        title: 'Error al responder',
        description: error.response?.data?.detail || 'No se pudo procesar la respuesta',
        variant: 'destructive',
      });
    },
  });
}

// Hook para cancelar invitación
export function useCancelInvitation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ groupId, invitationId }: { groupId: string; invitationId: string }) =>
      groupsApi.cancelInvitation(groupId, invitationId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['groupInvitations', variables.groupId] });
      toast({
        title: 'Invitación cancelada',
        description: 'La invitación ha sido eliminada',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al cancelar',
        description: error.response?.data?.detail || 'No se pudo cancelar la invitación',
        variant: 'destructive',
      });
    },
  });
}

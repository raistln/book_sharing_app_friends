'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  useGroup,
  useGroupMembers,
  useGroupInvitations,
  useUpdateGroup,
  useDeleteGroup,
  useRemoveMember,
  useUpdateMemberRole,
  useLeaveGroup,
  useCreateInvitation,
  useCancelInvitation,
} from '@/lib/hooks/use-groups';
import { useAuth } from '@/lib/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ArrowLeft,
  Users,
  Crown,
  Mail,
  Trash2,
  Edit,
  LogOut as LogOutIcon,
  Loader2,
  Copy,
  Check,
} from 'lucide-react';
import { toast } from '@/components/ui/use-toast';

export default function GroupDetailPage() {
  const params = useParams();
  const router = useRouter();
  const groupId = params.id as string;
  const { user } = useAuth();

  const { group, isLoading: loadingGroup } = useGroup(groupId);
  const { members, isLoading: loadingMembers } = useGroupMembers(groupId);
  const { invitations, isLoading: loadingInvitations } = useGroupInvitations(groupId);

  const updateGroup = useUpdateGroup();
  const deleteGroup = useDeleteGroup();
  const removeMember = useRemoveMember();
  const updateMemberRole = useUpdateMemberRole();
  const leaveGroup = useLeaveGroup();
  const createInvitation = useCreateInvitation();
  const cancelInvitation = useCancelInvitation();

  const [isEditingGroup, setIsEditingGroup] = useState(false);
  const [editFormData, setEditFormData] = useState({ name: '', description: '' });
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteUsername, setInviteUsername] = useState('');
  const [inviteMessage, setInviteMessage] = useState('');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const isAdmin = group?.members.some(
    (m) => m.user.id === user?.id && m.role === 'admin'
  );
  
  const isCreator = group?.created_by === user?.id;
  const canLeaveGroup = !isCreator; // Solo el creador no puede salir

  const handleEditGroup = () => {
    if (group) {
      setEditFormData({
        name: group.name,
        description: group.description || '',
      });
      setIsEditingGroup(true);
    }
  };

  const handleSaveEdit = () => {
    if (editFormData.name.trim()) {
      updateGroup.mutate(
        {
          groupId,
          data: {
            name: editFormData.name.trim(),
            description: editFormData.description.trim() || undefined,
          },
        },
        {
          onSuccess: () => setIsEditingGroup(false),
        }
      );
    }
  };

  const handleDeleteGroup = () => {
    deleteGroup.mutate(groupId);
  };

  const handleLeaveGroup = () => {
    leaveGroup.mutate(groupId);
  };

  const handleRemoveMember = (memberId: string) => {
    removeMember.mutate({ groupId, memberId });
  };

  const handleUpdateRole = (memberId: string, newRole: 'admin' | 'member') => {
    updateMemberRole.mutate({
      groupId,
      memberId,
      data: { role: newRole },
    });
  };

  const handleSendInvitation = () => {
    if (inviteEmail.trim() || inviteUsername.trim()) {
      createInvitation.mutate(
        {
          groupId,
          data: {
            email: inviteEmail.trim() || undefined,
            username: inviteUsername.trim() || undefined,
            message: inviteMessage.trim() || undefined,
          },
        },
        {
          onSuccess: () => {
            setInviteEmail('');
            setInviteUsername('');
            setInviteMessage('');
          },
        }
      );
    }
  };

  const copyInvitationCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    toast({
      title: 'Código copiado',
      description: 'El código de invitación ha sido copiado al portapapeles',
    });
    setTimeout(() => setCopiedCode(null), 2000);
  };

  if (loadingGroup) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-12 w-12 animate-spin text-storybook-leather" />
      </div>
    );
  }

  if (!group) {
    return (
      <main className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6 text-center">
            <p className="text-storybook-ink-light mb-4">Grupo no encontrado</p>
            <Link href="/groups">
              <Button>Volver a Grupos</Button>
            </Link>
          </CardContent>
        </Card>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-12">
        {/* Back Button */}
        <Link href="/groups">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a Grupos
          </Button>
        </Link>

        {/* Group Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {isEditingGroup ? (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="edit-name">Nombre</Label>
                      <Input
                        id="edit-name"
                        value={editFormData.name}
                        onChange={(e) =>
                          setEditFormData({ ...editFormData, name: e.target.value })
                        }
                        disabled={updateGroup.isPending}
                      />
                    </div>
                    <div>
                      <Label htmlFor="edit-description">Descripción</Label>
                      <Textarea
                        id="edit-description"
                        value={editFormData.description}
                        onChange={(e) =>
                          setEditFormData({ ...editFormData, description: e.target.value })
                        }
                        rows={3}
                        disabled={updateGroup.isPending}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleSaveEdit}
                        disabled={updateGroup.isPending || !editFormData.name.trim()}
                      >
                        {updateGroup.isPending ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Guardando...
                          </>
                        ) : (
                          'Guardar'
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setIsEditingGroup(false)}
                        disabled={updateGroup.isPending}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-3 mb-2">
                      <CardTitle className="text-3xl">{group.name}</CardTitle>
                      {isAdmin && <Badge variant="default"><Crown className="h-3 w-3 mr-1" />Admin</Badge>}
                    </div>
                    <CardDescription className="text-base">
                      {group.description || 'Sin descripción'}
                    </CardDescription>
                    <div className="flex items-center gap-4 mt-4 text-sm text-storybook-ink-light">
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        <span>{members.length} miembros</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Crown className="h-4 w-4" />
                        <span>{members.filter((m) => m.role === 'admin').length} administradores</span>
                      </div>
                    </div>
                  </>
                )}
              </div>
              {!isEditingGroup && (
                <div className="flex gap-2">
                  {isAdmin && (
                    <>
                      <Button variant="outline" size="sm" onClick={handleEditGroup}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="outline" size="sm" className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>¿Eliminar grupo?</AlertDialogTitle>
                            <AlertDialogDescription>
                              Esta acción eliminará permanentemente el grupo y todos sus datos. No se puede deshacer.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancelar</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={handleDeleteGroup}
                              className="bg-red-600 hover:bg-red-700"
                            >
                              Eliminar
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </>
                  )}
                  {canLeaveGroup && (
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <LogOutIcon className="mr-2 h-4 w-4" />
                          Salir del Grupo
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>¿Salir del grupo?</AlertDialogTitle>
                          <AlertDialogDescription>
                            Dejarás de ser miembro de este grupo. Necesitarás una nueva invitación para volver a unirte.
                            {isAdmin && " Como eres administrador, asegúrate de que haya otros administradores en el grupo."}
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancelar</AlertDialogCancel>
                          <AlertDialogAction onClick={handleLeaveGroup}>
                            Salir
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  )}
                </div>
              )}
            </div>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Members Card */}
          <Card>
            <CardHeader>
              <CardTitle>Miembros ({members.length})</CardTitle>
                <CardDescription>Personas que forman parte del grupo</CardDescription>
            </CardHeader>
            <CardContent>
              {loadingMembers ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-storybook-leather" />
                </div>
              ) : (
                <div className="space-y-3">
                  {members.map((member) => (
                    <div
                      key={member.user.id}
                      className="flex items-center justify-between p-3 bg-storybook-parchment rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-storybook-gold-light rounded-full flex items-center justify-center">
                          <span className="font-semibold text-storybook-leather">
                            {member.user.username[0].toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">{member.user.username}</p>
                          <p className="text-sm text-storybook-ink-light">{member.user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {isAdmin && member.user.id !== user?.id ? (
                          <>
                            <Select
                              value={member.role}
                              onValueChange={(value: 'admin' | 'member') =>
                                handleUpdateRole(member.user.id, value)
                              }
                            >
                              <SelectTrigger className="w-32">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="admin">Administrador</SelectItem>
                                <SelectItem value="member">Miembro</SelectItem>
                              </SelectContent>
                            </Select>
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button variant="ghost" size="sm" className="text-red-600">
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>¿Eliminar miembro?</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    {member.user.username} será eliminado del grupo.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                                  <AlertDialogAction
                                    onClick={() => handleRemoveMember(member.user.id)}
                                    className="bg-red-600 hover:bg-red-700"
                                  >
                                    Eliminar
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </>
                        ) : (
                          <Badge variant={member.role === 'admin' ? 'default' : 'secondary'}>
                            {member.role === 'admin' ? (
                              <>
                                <Crown className="h-3 w-3 mr-1" />
                                Administrador
                              </>
                            ) : (
                              'Miembro'
                            )}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Invitations Card (Admin only) */}
          {isAdmin && (
            <Card>
              <CardHeader>
                <CardTitle>Invitaciones</CardTitle>
                <CardDescription>Invita a nuevos miembros al grupo</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Send Invitation Form */}
                  <div className="space-y-3 p-4 bg-storybook-parchment rounded-lg">
                    <div>
                      <Label htmlFor="invite-email">Email (opcional)</Label>
                      <Input
                        id="invite-email"
                        type="email"
                        placeholder="usuario@ejemplo.com"
                        value={inviteEmail}
                        onChange={(e) => setInviteEmail(e.target.value)}
                        disabled={createInvitation.isPending}
                      />
                    </div>
                    <div>
                      <Label htmlFor="invite-username">Usuario (opcional)</Label>
                      <Input
                        id="invite-username"
                        type="text"
                        placeholder="nombre_usuario"
                        value={inviteUsername}
                        onChange={(e) => setInviteUsername(e.target.value)}
                        disabled={createInvitation.isPending}
                      />
                      <p className="text-xs text-storybook-ink-light mt-1">
                        Proporciona correo o usuario para invitar a alguien específico, o déjalos vacíos para crear un código genérico
                      </p>
                    </div>
                    <div>
                      <Label htmlFor="invite-message">Mensaje (opcional)</Label>
                      <Textarea
                        id="invite-message"
                        placeholder="¡Únete a nuestro grupo!"
                        value={inviteMessage}
                        onChange={(e) => setInviteMessage(e.target.value)}
                        rows={2}
                        disabled={createInvitation.isPending}
                      />
                    </div>
                    <Button
                      onClick={handleSendInvitation}
                      disabled={createInvitation.isPending}
                      className="w-full"
                    >
                      {createInvitation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Enviando...
                        </>
                      ) : (
                        <>
                          <Mail className="mr-2 h-4 w-4" />
                          Enviar Invitación
                        </>
                      )}
                    </Button>
                  </div>

                  {/* Pending Invitations */}
                  {loadingInvitations ? (
                    <div className="flex justify-center py-4">
                      <Loader2 className="h-6 w-6 animate-spin text-storybook-leather" />
                    </div>
                  ) : invitations.length > 0 ? (
                    <div className="space-y-2">
                      <h4 className="font-semibold text-sm">Invitaciones Pendientes</h4>
                      {invitations
                        .filter((inv) => inv.is_accepted === null)
                        .map((invitation) => (
                          <div
                            key={invitation.id}
                            className="flex items-center justify-between p-3 bg-storybook-gold-light/30 rounded-lg"
                          >
                            <div className="flex-1">
                              <p className="font-medium text-sm">{invitation.email}</p>
                              <p className="text-xs text-storybook-ink-light">
                                Expira: {new Date(invitation.expires_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => copyInvitationCode(invitation.code)}
                                title="Copiar código"
                              >
                                {copiedCode === invitation.code ? (
                                  <Check className="h-4 w-4 text-green-600" />
                                ) : (
                                  <Copy className="h-4 w-4" />
                                )}
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => cancelInvitation.mutate({ groupId, invitationId: invitation.id })}
                                disabled={cancelInvitation.isPending}
                                className="text-red-600 hover:text-red-700"
                                title="Cancelar invitación"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                    </div>
                  ) : (
                    <p className="text-sm text-storybook-ink-light text-center py-4">
                      No hay invitaciones pendientes
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
    </main>
  );
}

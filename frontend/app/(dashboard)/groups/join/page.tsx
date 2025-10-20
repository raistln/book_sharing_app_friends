'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useRespondInvitation } from '@/lib/hooks/use-groups';
import { groupsApi } from '@/lib/api/groups';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Users, Loader2, CheckCircle } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';

export default function JoinGroupPage() {
  const router = useRouter();
  const respondInvitation = useRespondInvitation();
  const [code, setCode] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [invitationDetails, setInvitationDetails] = useState<any>(null);

  const handleValidateCode = async () => {
    if (!code.trim()) {
      toast({
        title: 'Error',
        description: 'Por favor ingresa un código de invitación',
        variant: 'destructive',
      });
      return;
    }

    setIsValidating(true);
    try {
      const invitation = await groupsApi.getInvitationByCode(code.trim());
      setInvitationDetails(invitation);
    } catch (error: any) {
      toast({
        title: 'Código inválido',
        description: error.response?.data?.detail || 'El código no existe o ha expirado',
        variant: 'destructive',
      });
      setInvitationDetails(null);
    } finally {
      setIsValidating(false);
    }
  };

  const handleJoinGroup = () => {
    respondInvitation.mutate({
      code: code.trim(),
      accept: true,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light">
      <div className="container mx-auto px-4 py-12">
        {/* Back Button */}
        <Link href="/groups">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a Grupos
          </Button>
        </Link>

        {/* Main Card */}
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-3 bg-storybook-gold-light rounded-full">
                  <Users className="h-6 w-6 text-storybook-leather" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Unirse a un Grupo</CardTitle>
                  <CardDescription>
                    Ingresa el código de invitación que recibiste
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Code Input */}
                <div className="space-y-2">
                  <Label htmlFor="code">Código de Invitación</Label>
                  <div className="flex gap-2">
                    <Input
                      id="code"
                      type="text"
                      placeholder="Ej: abc123def456"
                      value={code}
                      onChange={(e) => {
                        setCode(e.target.value.toLowerCase());
                        setInvitationDetails(null);
                      }}
                      disabled={isValidating || respondInvitation.isPending}
                      className="flex-1 font-mono"
                      maxLength={50}
                    />
                    <Button
                      onClick={handleValidateCode}
                      disabled={!code.trim() || isValidating || respondInvitation.isPending}
                    >
                      {isValidating ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Validando...
                        </>
                      ) : (
                        'Validar'
                      )}
                    </Button>
                  </div>
                  <p className="text-sm text-storybook-ink-light">
                    El código es proporcionado por un administrador del grupo
                  </p>
                </div>

                {/* Invitation Details */}
                {invitationDetails && (
                  <div className="p-4 bg-storybook-gold-light/30 border border-storybook-gold rounded-lg space-y-3">
                    <div className="flex items-center gap-2 text-green-600">
                      <CheckCircle className="h-5 w-5" />
                      <span className="font-semibold">Código válido</span>
                    </div>
                    <div className="space-y-2">
                      <div>
                        <p className="text-sm text-storybook-ink-light">Has sido invitado a:</p>
                        <p className="font-semibold text-lg text-storybook-leather">
                          {invitationDetails.group?.name || 'Grupo'}
                        </p>
                      </div>
                      {invitationDetails.message && (
                        <div>
                          <p className="text-sm text-storybook-ink-light">Mensaje:</p>
                          <p className="text-sm italic">{invitationDetails.message}</p>
                        </div>
                      )}
                      <div>
                        <p className="text-xs text-storybook-ink-light">
                          Invitado por: {invitationDetails.invited_by_username || 'Admin'}
                        </p>
                        <p className="text-xs text-storybook-ink-light">
                          Expira: {new Date(invitationDetails.expires_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Info Box */}
                <div className="bg-storybook-parchment border border-storybook-gold-light rounded-lg p-4">
                  <h4 className="font-semibold text-storybook-leather mb-2">
                    ℹ️ ¿Cómo funciona?
                  </h4>
                  <ul className="text-sm text-storybook-ink-light space-y-1">
                    <li>• Pide a un administrador del grupo que te envíe un código</li>
                    <li>• Ingresa el código en el campo de arriba</li>
                    <li>• Valida que el código sea correcto</li>
                    <li>• Únete al grupo con un solo click</li>
                  </ul>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => router.back()}
                    disabled={respondInvitation.isPending}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleJoinGroup}
                    disabled={!invitationDetails || respondInvitation.isPending}
                    className="flex-1"
                  >
                    {respondInvitation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Uniéndose...
                      </>
                    ) : (
                      <>
                        <Users className="mr-2 h-4 w-4" />
                        Unirse al Grupo
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

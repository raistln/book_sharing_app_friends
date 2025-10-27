'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useMyProfile, useUpdateProfile, useChangePassword, useUploadAvatar, useDeleteAvatar } from '@/lib/hooks/use-profile';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Loader2, User, Upload, Trash2, Save } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';

export default function EditProfilePage() {
  const router = useRouter();
  const { profile, isLoading: loadingProfile } = useMyProfile();
  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();
  const uploadAvatar = useUploadAvatar();
  const deleteAvatar = useDeleteAvatar();

  const [profileData, setProfileData] = useState({
    full_name: '',
    bio: '',
    location: '',
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  useEffect(() => {
    if (profile) {
      setProfileData({
        full_name: profile.full_name || '',
        bio: profile.bio || '',
        location: profile.location || '',
      });
      if (profile.avatar_url) {
        setAvatarPreview(profile.avatar_url);
      }
    }
  }, [profile]);

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile.mutate(profileData);
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast({
        title: 'Error',
        description: 'Las contraseñas no coinciden',
        variant: 'destructive',
      });
      return;
    }

    if (passwordData.new_password.length < 8) {
      toast({
        title: 'Error',
        description: 'La contraseña debe tener al menos 8 caracteres',
        variant: 'destructive',
      });
      return;
    }

    changePassword.mutate(passwordData, {
      onSuccess: () => {
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: '',
        });
      },
    });
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast({
          title: 'Error',
          description: 'La imagen no puede superar los 5MB',
          variant: 'destructive',
        });
        return;
      }

      setAvatarFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAvatarUpload = () => {
    if (avatarFile) {
      uploadAvatar.mutate(avatarFile, {
        onSuccess: () => {
          setAvatarFile(null);
        },
      });
    }
  };

  const handleAvatarDelete = () => {
    deleteAvatar.mutate(undefined, {
      onSuccess: () => {
        setAvatarPreview(null);
        setAvatarFile(null);
      },
    });
  };

  if (loadingProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-storybook-leather" />
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-12">
        {/* Back Button */}
        <Link href="/profile">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver al Perfil
          </Button>
        </Link>

        <div className="max-w-3xl mx-auto space-y-6">
          {/* Avatar Section */}
          <Card>
            <CardHeader>
              <CardTitle>Foto de Perfil</CardTitle>
              <CardDescription>Actualiza tu imagen de perfil</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className="w-24 h-24 bg-storybook-gold-light rounded-full flex items-center justify-center overflow-hidden">
                  {avatarPreview ? (
                    <img
                      src={avatarPreview}
                      alt="Avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="h-12 w-12 text-storybook-leather" />
                  )}
                </div>
                <div className="flex-1 space-y-3">
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Label 
                        htmlFor="avatar-upload" 
                        className="flex items-center justify-center w-full px-4 py-2 border-2 border-dashed border-storybook-leather rounded-lg cursor-pointer hover:bg-storybook-parchment transition-colors"
                      >
                        <Upload className="mr-2 h-4 w-4" />
                        <span>Seleccionar imagen</span>
                      </Label>
                      <Input
                        id="avatar-upload"
                        type="file"
                        accept="image/*"
                        onChange={handleAvatarChange}
                        disabled={uploadAvatar.isPending || deleteAvatar.isPending}
                        className="hidden"
                      />
                    </div>
                    {avatarFile && (
                      <Button
                        onClick={handleAvatarUpload}
                        disabled={uploadAvatar.isPending}
                      >
                        {uploadAvatar.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <Upload className="mr-2 h-4 w-4" />
                            Subir
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                  {avatarFile && (
                    <p className="text-sm text-storybook-ink">
                      Archivo seleccionado: {avatarFile.name}
                    </p>
                  )}
                  {avatarPreview && !avatarFile && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleAvatarDelete}
                      disabled={deleteAvatar.isPending}
                      className="text-red-600"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Eliminar Foto
                    </Button>
                  )}
                  <p className="text-sm text-storybook-ink-light">
                    JPG, PNG o GIF. Máximo 5MB.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Profile Information */}
          <Card>
            <CardHeader>
              <CardTitle>Información Personal</CardTitle>
              <CardDescription>Actualiza tu información de perfil</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleProfileSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Usuario</Label>
                  <Input
                    id="username"
                    value={profile?.username || ''}
                    disabled
                    className="bg-gray-100"
                  />
                  <p className="text-xs text-storybook-ink-light">
                    El nombre de usuario no se puede cambiar
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Correo electrónico</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profile?.email || ''}
                    disabled
                    className="bg-gray-100"
                  />
                  <p className="text-xs text-storybook-ink-light">
                    El email no se puede cambiar
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="full_name">Nombre Completo</Label>
                  <Input
                    id="full_name"
                    type="text"
                    placeholder="Tu nombre completo"
                    value={profileData.full_name}
                    onChange={(e) =>
                      setProfileData({ ...profileData, full_name: e.target.value })
                    }
                    disabled={updateProfile.isPending}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Ubicación</Label>
                  <Input
                    id="location"
                    type="text"
                    placeholder="Ciudad, País"
                    value={profileData.location}
                    onChange={(e) =>
                      setProfileData({ ...profileData, location: e.target.value })
                    }
                    disabled={updateProfile.isPending}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Biografía</Label>
                  <Textarea
                    id="bio"
                    placeholder="Cuéntanos sobre ti..."
                    value={profileData.bio}
                    onChange={(e) =>
                      setProfileData({ ...profileData, bio: e.target.value })
                    }
                    rows={4}
                    maxLength={500}
                    disabled={updateProfile.isPending}
                  />
                  <p className="text-xs text-storybook-ink-light">
                    {profileData.bio.length}/500 caracteres
                  </p>
                </div>

                <Button
                  type="submit"
                  disabled={updateProfile.isPending}
                  className="w-full"
                >
                  {updateProfile.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Guardar Cambios
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Change Password */}
          <Card>
            <CardHeader>
              <CardTitle>Cambiar Contraseña</CardTitle>
              <CardDescription>Actualiza tu contraseña de acceso</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePasswordSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current_password">Contraseña Actual</Label>
                  <Input
                    id="current_password"
                    type="password"
                    value={passwordData.current_password}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, current_password: e.target.value })
                    }
                    disabled={changePassword.isPending}
                    required
                  />
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label htmlFor="new_password">Nueva Contraseña</Label>
                  <Input
                    id="new_password"
                    type="password"
                    value={passwordData.new_password}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, new_password: e.target.value })
                    }
                    disabled={changePassword.isPending}
                    required
                    minLength={8}
                  />
                  <p className="text-xs text-storybook-ink-light">
                    Mínimo 8 caracteres
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirmar Nueva Contraseña</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, confirm_password: e.target.value })
                    }
                    disabled={changePassword.isPending}
                    required
                    minLength={8}
                  />
                </div>

                <Button
                  type="submit"
                  disabled={changePassword.isPending}
                  className="w-full"
                  variant="outline"
                >
                  {changePassword.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Cambiando...
                    </>
                  ) : (
                    'Cambiar Contraseña'
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
    </main>
  );
}

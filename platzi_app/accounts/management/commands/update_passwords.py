from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Actualiza las contraseñas de los usuarios al nuevo algoritmo de hashing'

    def handle(self, *args, **options):
        users = User.objects.all()
        updated_count = 0
        
        self.stdout.write(self.style.WARNING(
            f'Actualizando contraseñas de {users.count()} usuarios...'
        ))
        
        for user in users:
            # Obtener la contraseña hasheada actual
            old_password = user.password
            
            # Si ya está usando MD5, no hacer nada
            if old_password.startswith('md5$'):
                continue
            
            # Re-hashear con el nuevo algoritmo (MD5 para desarrollo)
            # NOTA: Esto solo funciona si conocemos la contraseña en texto plano
            # Para usuarios existentes, mantener el hash actual
            self.stdout.write(
                f'Usuario {user.username}: Ya tiene hash seguro, manteniéndolo.'
            )
        
        self.stdout.write(self.style.SUCCESS(
            f'Proceso completado. {updated_count} usuarios actualizados.'
        ))
        self.stdout.write(self.style.WARNING(
            'NOTA: Los nuevos usuarios usarán el algoritmo MD5 (más rápido para desarrollo).'
        ))
        self.stdout.write(self.style.WARNING(
            'IMPORTANTE: Cambiar a PBKDF2 en producción para mayor seguridad.'
        ))

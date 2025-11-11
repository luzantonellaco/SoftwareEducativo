import os
import sys

# Ajustar la variable de entorno al settings del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juegoeducativo.settings')

import django
django.setup()

from aplicacion.models import NivelUnlock
from django.contrib.auth import get_user_model

User = get_user_model()

print('Listing NivelUnlock entries:')
for u in NivelUnlock.objects.select_related('user').all():
    print(f'user={u.user.username!s}\talias={getattr(u.user, "alias", None)!s}\tlevel={u.level}\tunlocked_at={u.unlocked_at}')

print('\nSummary per user:')
from collections import defaultdict
summary = defaultdict(list)
for u in NivelUnlock.objects.select_related('user').all():
    summary[u.user.username].append(u.level)
for username, levels in summary.items():
    print(f'{username}: {levels}')

# Exit with 0
sys.exit(0)

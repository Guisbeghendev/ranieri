from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserLoginForm, UserForm, ProfileForm
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from core.models import Profile, Galeria, AudienceGroup
from django.db.models import Q

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = Profile.objects.get_or_create(user=user)
            messages.success(request, "Cadastro realizado com sucesso! Por favor, faça login.")
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bem-vindo de volta, {user.username}!")
            return redirect('accounts:dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Você foi desconectado.")
    return redirect('home')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['user_name'] = user.get_full_name() or user.username
        context['is_superuser'] = user.is_superuser
        context['is_staff_user'] = user.is_staff
        context['is_photographer_user'] = getattr(user, 'is_photographer', False)
        context['user_profile'] = Profile.objects.get_or_create(user=user)[0]
        context['user_roles'] = user.groups.all()  # auth.Group do usuário

        # Últimas 3 galerias públicas
        context['latest_public_galleries'] = Galeria.objects.filter(is_public=True).order_by('-created_at')[:3]

        # Dicionário para armazenar as últimas 3 galerias POR GRUPO DE AUDIÊNCIA (agora inclui públicas se associadas ao grupo)
        latest_galleries_by_group = {}

        # Pega os AudienceGroups aos quais o usuário está diretamente associado
        user_audience_groups = user.audience_groups.all()

        # DEBUG PRINT: Verifique quais AudienceGroups o usuário possui
        print(
            f"DEBUG: User '{user.username}' (PK: {user.pk}) belongs to AudienceGroups: {[ag.name for ag in user_audience_groups]}")

        if user_audience_groups.exists():
            for audience_group in user_audience_groups:
                # Busca galerias associadas a este AudienceGroup (AGORA INCLUI PÚBLICAS SE ASSOCIADAS)
                group_galleries = Galeria.objects.filter(
                    Q(audience_groups=audience_group)  # REMOVIDO: & Q(is_public=False)
                ).order_by('-created_at')[:3]  # Limita a 3 galerias por grupo

                # DEBUG PRINT: Verifique as galerias encontradas para cada grupo
                print(
                    f"DEBUG: For AudienceGroup '{audience_group.name}', found {group_galleries.count()} galleries: {[g.name for g in group_galleries]}")

                if group_galleries.exists():
                    latest_galleries_by_group[audience_group.name] = group_galleries

        # Adiciona as galerias do próprio fotógrafo (se aplicável), garantindo que não duplique
        if context['is_photographer_user']:
            pks_already_collected = set()
            for galleries_list in latest_galleries_by_group.values():
                for gallery in galleries_list:
                    pks_already_collected.add(gallery.pk)

            # Busca galerias criadas pelo fotógrafo que AINDA NÃO FORAM INCLUÍDAS
            # Aqui, ainda filtramos por is_public=False se quisermos que 'Minhas Galerias (Fotógrafo)'
            # seja estritamente para as privadas dele que não estão em nenhum grupo.
            # Se você quiser que o fotógrafo veja TODAS as suas galerias aqui (públicas e privadas),
            # remova o Q(is_public=False) também desta consulta.
            photographer_galleries_not_in_groups = Galeria.objects.filter(
                Q(fotografo=user) & Q(is_public=False)
            ).exclude(pk__in=list(pks_already_collected)).order_by('-created_at')[:3]

            if photographer_galleries_not_in_groups.exists():
                latest_galleries_by_group['Minhas Galerias (Fotógrafo)'] = photographer_galleries_not_in_groups
                # DEBUG PRINT: Verifique as galerias do fotógrafo não incluídas em grupos
                print(
                    f"DEBUG: Fotógrafo galleries not in groups: {[g.name for g in photographer_galleries_not_in_groups]}")

        context['latest_galleries_by_group'] = latest_galleries_by_group
        # DEBUG PRINT: Verifique o dicionário final para o contexto
        print(f"DEBUG: Final latest_galleries_by_group for context: {latest_galleries_by_group}")

        context['see_more_galleries_url'] = reverse_lazy('galleries:client_group_list')

        return context


class ViewProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile, created = Profile.objects.get_or_create(user=user)
        context['user_profile'] = profile
        context['user_roles'] = user.groups.all()
        return context


class EditProfileView(LoginRequiredMixin, View):
    template_name = 'edit_profile.html'
    login_url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)

        user_form = UserForm(request.POST, request.FILES, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Houve um erro ao atualizar seu perfil. Por favor, verifique os campos.")
            return render(request, self.template_name, {
                'user_form': user_form,
                'profile_form': profile_form
            })


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'delete_account.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('accounts:login')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        logout(self.request)
        messages.success(self.request, "Sua conta foi excluída com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_to_delete'] = self.request.user
        return context

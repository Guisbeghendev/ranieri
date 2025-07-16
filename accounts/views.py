# accounts/views.py
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserLoginForm, UserForm, ProfileForm
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View, DeleteView  # Importa DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from core.models import Profile, Galeria  # Importa o modelo Profile e Galeria para o dashboard
from django.db.models import Q  # Importa Q para consultas complexas

User = get_user_model()  # Garante que estamos usando o modelo de usuário correto


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

        # As flags is_superuser, is_staff e is_photographer já devem estar corretas
        # devido aos signals. Passamos elas diretamente para o contexto.
        context['is_superuser'] = user.is_superuser
        # NOVO: Variável para verificar se o usuário tem status de staff (para acesso ao admin)
        context['is_staff_user'] = user.is_staff
        # NOVO: Variável para verificar se o usuário tem status de fotógrafo
        context['is_photographer_user'] = getattr(user, 'is_photographer', False)

        # Garante que o perfil do usuário está disponível no contexto
        context['user_profile'] = Profile.objects.get_or_create(user=user)[0]

        # Adiciona os grupos padrão do Django (roles/cargos) ao contexto
        context['user_roles'] = user.groups.all()

        # Últimas 3 galerias públicas a uma variável de contexto dedicada (para o card público)
        context['latest_public_galleries'] = Galeria.objects.filter(is_public=True).order_by('-created_at')[:3]

        # Dicionário para armazenar as últimas 3 galerias POR GRUPO DE AUDIÊNCIA (apenas privadas)
        latest_galleries_by_group = {}

        if user.audience_groups.exists():
            for group in user.audience_groups.all():
                # Garante que apenas galerias NÃO PÚBLICAS associadas ao grupo sejam exibidas
                group_galleries = Galeria.objects.filter(
                    Q(audience_groups=group) & Q(is_public=False)
                ).order_by('-created_at')[:3]
                if group_galleries.exists():
                    latest_galleries_by_group[group.name] = group_galleries

        # Usa a nova variável de contexto 'is_photographer_user'
        if context['is_photographer_user']:
            # Garante que apenas galerias NÃO PÚBLICAS criadas pelo fotógrafo e não associadas
            # a grupos de audiência do usuário atual sejam exibidas aqui
            photographer_galleries = Galeria.objects.filter(
                Q(fotografo=user) & Q(is_public=False) & ~Q(audience_groups__in=user.audience_groups.all())
            ).distinct().order_by('-created_at')[:3]
            if photographer_galleries.exists():
                latest_galleries_by_group['Minhas Galerias (Fotógrafo)'] = photographer_galleries

        context['latest_galleries_by_group'] = latest_galleries_by_group

        context['see_more_galleries_url'] = reverse_lazy(
            'galleries:client_group_list')  # Mantém o link para grupos de cliente

        return context


# VIEW para exibir o perfil
class ViewProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile, created = Profile.objects.get_or_create(user=user)
        context['user_profile'] = profile
        # Adiciona os grupos padrão do Django (roles/cargos) ao contexto
        context['user_roles'] = user.groups.all()
        # Mantém audience_groups para o caso de você usá-los em outro lugar no profile.html
        context['audience_groups'] = user.audience_groups.all()
        return context


# VIEW para editar o perfil
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


# NOVA VIEW: Para exclusão da conta
class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User  # O modelo a ser excluído é o User
    template_name = 'delete_account.html'  # Template de confirmação
    success_url = reverse_lazy('home')  # Redireciona para a home após a exclusão
    login_url = reverse_lazy('accounts:login')

    def get_object(self, queryset=None):
        # Garante que apenas o próprio usuário logado pode ser excluído
        return self.request.user

    def form_valid(self, form):
        # Realiza o logout antes de excluir o usuário para evitar problemas de sessão
        logout(self.request)
        messages.success(self.request, "Sua conta foi excluída com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_to_delete'] = self.request.user  # Passa o usuário para o template
        return context

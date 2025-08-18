# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from core.models import Profile  # Importa o modelo Profile do app core

User = get_user_model()  # Obtém o modelo de usuário ativo no projeto


# Formulário de Registro de Usuário - AGORA USANDO SEU MODELO CUSTOMIZADO E GARANTINDO O USO DE get_user_model()
class UserRegistrationForm(UserCreationForm):
    # TRECHO ATUALIZADO: Redefine o campo username para mudar o label e adicionar o help_text
    username = forms.CharField(
        max_length=150,
        label='Nome ou Apelido',  # O novo label do campo
        help_text='Use seu nome ou um apelido único. Não use números de registro ou documentos.',
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User  # Garante que o formulário use o nosso modelo User
        fields = UserCreationForm.Meta.fields + ('email',)  # Adiciona o campo de email


# Formulário de Login de Usuário
class UserLoginForm(AuthenticationForm):
    # AQUI ESTÁ A CORREÇÃO: Redefinimos o campo username do formulário de autenticação
    username = forms.CharField(
        label='Nome ou Apelido',  # O novo label para o formulário de login
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-laranja1 bg-white text-preto1 placeholder-gray-500'})
    )


class UserForm(forms.ModelForm):
    """
    Formulário para edição de campos do modelo User.
    Permite editar nome, sobrenome e e-mail.
    """
    email = forms.EmailField(required=False, label="E-mail")
    first_name = forms.CharField(max_length=150, required=False, label="Nome")
    last_name = forms.CharField(max_length=150, required=False, label="Sobrenome")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Campos que o usuário pode editar
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
        }
        widgets = {
            # CORRIGIDO: Usando bg-white e text-gray-900 para visibilidade garantida
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}),
        }


class ProfileForm(forms.ModelForm):
    """
    Formulário para edição de campos do modelo Profile.
    Todos os campos são opcionais.
    """
    # Campos DateField
    birth_date = forms.DateField(
        required=False,
        label="Data de Nascimento",
        widget=forms.DateInput(attrs={'type': 'date',
                                      'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y']  # Adiciona formatos de entrada
    )

    # Campos CharField
    address = forms.CharField(max_length=255, required=False, label="Endereço",
                              widget=forms.TextInput(attrs={
                                  'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}))
    city = forms.CharField(max_length=100, required=False, label="Cidade",
                           widget=forms.TextInput(attrs={
                               'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}))
    state = forms.CharField(max_length=100, required=False, label="Estado",
                            widget=forms.TextInput(attrs={
                                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}))
    whatsapp = forms.CharField(max_length=30, required=False, label="WhatsApp",
                               widget=forms.TextInput(attrs={
                                   'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}))
    other_contact = forms.CharField(max_length=255, required=False, label="Outro Contato",
                                    widget=forms.TextInput(attrs={
                                        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}))
    document_id = forms.CharField(max_length=50, required=False, label="RA do Aluno",
                                  widget=forms.TextInput(attrs={
                                      'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}))

    # Campos TextField
    quem_sou_para_escola = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4,
                                     'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}),
        required=False,
        label="Quem sou para a Escola?"
    )
    biography = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4,
                                     'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}),
        required=False,
        label="Biografia"
    )

    # Campo ImageField
    profile_picture = forms.ImageField(required=False, label="Foto de Perfil",
                                       # ATUALIZADO: Cor do botão de upload para laranja1 com texto preto1
                                       widget=forms.FileInput(attrs={
                                           'class': 'mt-1 block w-full text-sm text-gray-900 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-laranja1 file:text-preto1 hover:file:bg-laranja3'}))

    # Campo URLField
    website = forms.URLField(required=False, label="Website / Portfólio",
                             widget=forms.URLInput(attrs={
                                 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-roxo1 focus:border-roxo1 sm:text-sm bg-white text-gray-900'}))

    class Meta:
        model = Profile
        # Excluímos 'user', 'created_at', 'updated_at', 'last_activity_date' da edição direta pelo formulário
        exclude = ['user', 'created_at', 'updated_at', 'last_activity_date']
        labels = {
            'birth_date': 'Data de Nascimento',
            'address': 'Endereço',
            'city': 'Cidade',
            'state': 'Estado',
            'whatsapp': 'WhatsApp',
            'other_contact': 'Outro Contato',
            'quem_sou_para_escola': 'Quem sou para a Escola?',
            'biography': 'Biografia',
            'profile_picture': 'Foto de Perfil',
            'website': 'Website / Portfólio',
            'document_id': 'RA do Aluno',
        }

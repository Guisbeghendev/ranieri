<?php

namespace App\Policies;

use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;

class UserPolicy
{
    use HandlesAuthorization;

    // Antes de qualquer verificação, o admin pode fazer tudo
    public function before(User $authUser, $ability): ?bool
    {
        if ($authUser->hasRole('admin')) {
            return true;
        }

        return null;
    }


    // Visualizar lista de usuários — só admin (tratado no before) ou gestor
    public function viewAny(User $authUser): bool
    {
        return $authUser->hasRole('gestao');
    }

    // Visualizar um usuário específico — admin (before) ou o próprio usuário
    public function view(User $authUser, User $user): bool
    {
        return $authUser->id === $user->id || $authUser->hasRole('gestao');
    }


    // Criar usuário — só admin (before)
    public function create(User $authUser): bool
    {
        return false; // Só admin pode, já tratado no before
    }

    // Atualizar usuário — admin (before), ou usuário atual, ou funcionário/professor atualizando aluno/família
    public function update(User $authUser, User $user): bool
    {
        if ($authUser->id === $user->id) {
            return true;
        }

        if (($authUser->hasRole('funcionario') || $authUser->hasRole('professor')) && ($user->hasRole('aluno') || $user->hasRole('familia'))) {
            return true;
        }

        return false;
    }

    // Deletar usuário — só admin (before)
    public function delete(User $authUser, User $user): bool
    {
        return false; // Só admin (before)
    }
}

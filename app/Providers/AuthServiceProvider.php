<?php

namespace App\Providers;

use Illuminate\Foundation\Support\Providers\AuthServiceProvider as ServiceProvider;
use Illuminate\Support\Facades\Gate;
use App\Models\User;
use App\Policies\UserPolicy;

class AuthServiceProvider extends ServiceProvider
{
    /**
     * The policy mappings for the application.
     *
     * @var array<class-string, class-string>
     */
    protected $policies = [
        User::class => UserPolicy::class,
    ];

    /**
     * Register any authentication / authorization services.
     */
    public function boot()
    {
        $this->registerPolicies();

        // Gate before: admin pode tudo
        Gate::before(function (User $authUser, $ability) {
            if ($authUser->hasRole('admin')) {
                return true;
            }
        });

        // Visualizar lista de usuários - gestor ou admin (admin já liberado no before)
        Gate::define('viewAnyUser', function (User $authUser) {
            return $authUser->hasRole('gestao');
        });

        // Visualizar usuário específico - o próprio ou gestor
        Gate::define('viewUser', function (User $authUser, User $user) {
            return $authUser->id === $user->id || $authUser->hasRole('gestao');
        });

        // Criar usuário - só admin (já tratado no before)
        Gate::define('createUser', function (User $authUser) {
            return false; // só admin pode, permitido no before
        });

        // Atualizar usuário - o próprio, funcionário/professor atualizando aluno/família
        Gate::define('updateUser', function (User $authUser, User $user) {
            if ($authUser->id === $user->id) {
                return true;
            }

            if (
                ($authUser->hasRole('funcionario') || $authUser->hasRole('professor')) &&
                ($user->hasRole('aluno') || $user->hasRole('familia'))
            ) {
                return true;
            }

            return false;
        });

        // Deletar usuário - só admin (já tratado no before)
        Gate::define('deleteUser', function (User $authUser, User $user) {
            return false; // só admin (before)
        });
    }
}

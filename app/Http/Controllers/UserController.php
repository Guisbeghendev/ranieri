<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;

class UserController extends Controller
{
    // Exemplo: lista de usuários - só quem pode 'viewAnyUser'
    public function index()
    {
        if (Gate::denies('viewAnyUser')) {
            abort(403, 'Acesso negado');
        }

        $users = User::all();
        return view('users.index', compact('users'));
    }

    // Exemplo: visualizar um usuário específico
    public function show(User $user)
    {
        if (Gate::denies('viewUser', $user)) {
            abort(403, 'Acesso negado');
        }

        return view('users.show', compact('user'));
    }

    // Exemplo: atualizar usuário
    public function update(Request $request, User $user)
    {
        if (Gate::denies('updateUser', $user)) {
            abort(403, 'Acesso negado');
        }

        // validação e update simplificado
        $data = $request->validate([
            'name' => 'required|string|max:255',
            // outras validações conforme necessário
        ]);

        $user->update($data);

        return redirect()->route('users.show', $user)->with('success', 'Usuário atualizado!');
    }

    // Exemplo: deletar usuário
    public function destroy(User $user)
    {
        if (Gate::denies('deleteUser', $user)) {
            abort(403, 'Acesso negado');
        }

        $user->delete();

        return redirect()->route('users.index')->with('success', 'Usuário deletado!');
    }
}

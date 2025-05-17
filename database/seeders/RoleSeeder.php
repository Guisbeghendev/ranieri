<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Role;

class RoleSeeder extends Seeder
{
    public function run(): void
    {
        $roles = [
            ['name' => 'admin', 'label' => 'Administrador'],
            ['name' => 'fotografo', 'label' => 'Fotógrafo'],
            ['name' => 'familia', 'label' => 'Família'],
            ['name' => 'publico', 'label' => 'Público'],
            ['name' => 'aluno', 'label' => 'Aluno'],
            ['name' => 'gestao', 'label' => 'Gestão'],
            ['name' => 'de', 'label' => 'Diretoria de Ensino'],
            ['name' => 'funcionario', 'label' => 'Funcionário'],
            ['name' => 'professor', 'label' => 'Professor'],
        ];

        foreach ($roles as $role) {
            Role::firstOrCreate(['name' => $role['name']], ['label' => $role['label']]);
        }
    }
}
